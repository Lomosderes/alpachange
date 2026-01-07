# petitions/views.py
from tokenize import Comment
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PetitionForm

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Category, Notification, Petition, Report, Vote

from datetime import timedelta
from django.utils import timezone

from .forms import CommentForm
from django.shortcuts import get_object_or_404

from django.contrib.admin.views.decorators import staff_member_required

from .models import Comment    


@login_required
def create_petition(request):
    # Verificar que el usuario esté verificado
    if not request.user.userprofile.is_verified:
        messages.error(request, "Debes verificar tu correo institucional antes de crear una petición.")
        return redirect('verify_email')  # o a un panel de aviso

    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.author = request.user
            petition.save()
            messages.success(request, "Petición creada exitosamente.")
            return redirect('petition_list')
    else:
        form = PetitionForm()
    return render(request, 'petitions/create.html', {'form': form})

@login_required
@require_POST
def toggle_vote(request, petition_id):
    user = request.user
    if not user.userprofile.is_verified:
        return JsonResponse({'error': 'Solo usuarios verificados pueden votar.'}, status=403)

    try:
        petition = Petition.objects.get(id=petition_id, is_active=True)
    except Petition.DoesNotExist:
        return JsonResponse({'error': 'Petición no encontrada o archivada.'}, status=404)

    # Si ya votó, eliminar el voto (desvotar)
    existing_vote = Vote.objects.filter(user=user, petition=petition).first()
    
    if existing_vote:
        existing_vote.delete()
        voted = False
        message = "Voto retirado."
    else:
        Vote.objects.create(user=user, petition=petition)
        voted = True
        message = "Voto registrado."
    return JsonResponse({
        'success': True,
        'voted': voted,
        'vote_count': petition.vote_count(),
        'message': message
    })
    
    



from django.db.models import Count,Q

def petition_list(request):
    # Orden real por número de apoyos
    petitions = Petition.objects.filter(is_active=True) \
        .annotate(vote_count=Count('votes')) \
        .order_by('-vote_count', '-created_at')

    total_votes_today = Vote.objects.filter(
        voted_at__gte=timezone.now() - timedelta(days=1)
    ).count()

    approved_petitions = Petition.objects.filter(is_active=False).count()

    petition_data = []

    for p in petitions:
        age = timezone.now() - p.created_at

        if age < timedelta(days=8):
            expires_at = p.created_at + timedelta(days=8)
        else:
            current_day = 8
            while True:
                next_eval = p.created_at + timedelta(days=current_day)
                if next_eval > timezone.now():
                    expires_at = next_eval
                    break
                current_day += 1

        time_left = expires_at - timezone.now()

        petition_data.append({
            'petition': p,
            'vote_count': p.vote_count,     # <- añadimos esto
            'time_left': time_left,
            'end_timestamp': int(expires_at.timestamp()) * 1000
        })

    # Estadísticas para el HERO
    total_votes_today = Vote.objects.filter(voted_at__gte=timezone.now() - timedelta(days=1)).count()
    approved_petitions = Petition.objects.filter(is_active=False).count()

    return render(request, 'petitions/list.html', {'petition_data': petition_data,'total_votes_today': total_votes_today,
        'approved_petitions': approved_petitions,})



@login_required
def add_comment(request, petition_id):
    if not request.user.userprofile.is_verified:
        messages.error(request, "Debes verificar tu cuenta para comentar.")
        return redirect('petition_detail', petition_id=petition_id)

    petition = get_object_or_404(Petition, id=petition_id, is_active=True)

    if request.method == 'POST':
        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.petition = petition
            comment.author = request.user

            # Asignar alias de comentario
            alias = form.cleaned_data['alias']
            comment.alias = alias

            # Guardar alias en perfil si es la primera vez
            profile = request.user.userprofile
            if not profile.comment_alias:
                profile.comment_alias = alias
                profile.save()

            comment.save()
            return redirect('petition_detail', petition_id=petition_id)
    else:
        form = CommentForm(user=request.user)

    return render(request, 'petitions/add_comment.html', {'form': form, 'petition': petition})

@login_required
def report_content(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    report_type = data.get("type")
    reason = data.get("reason", "").strip()
    petition_id = data.get("petition_id")
    comment_id = data.get("comment_id")

    if not reason:
        return JsonResponse({"error": "Debes indicar una razón."}, status=400)

    report = Report(
        reporter=request.user,
        reason=reason,
        report_type=report_type
    )

    if report_type == "petition" and petition_id:
        petition = get_object_or_404(Petition, id=petition_id)
        report.petition = petition

    elif report_type == "comment" and comment_id:
        from .models import Comment
        comment = get_object_or_404(Comment, id=comment_id)
        report.comment = comment

    else:
        return JsonResponse({"error": "Datos no válidos."}, status=400)

    report.save()
    return JsonResponse({
        "success": True,
        "message": "Denuncia enviada correctamente."
    })


@staff_member_required
def admin_reports(request):
    reports = Report.objects.filter(reviewed=False).order_by('-created_at')
    return render(request, 'admin/reports.html', {'reports': reports})

@staff_member_required
def add_followup(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    if request.method == 'POST':
        petition.followup_notes = request.POST.get('notes', '')
        if 'pdf' in request.FILES:
            petition.followup_pdf = request.FILES['pdf']
        petition.save()
        return redirect('petition_detail', petition_id=petition_id)
    return render(request, 'admin/add_followup.html', {'petition': petition})


from .models import Petition

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

def petition_detail(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    
    # Calcular tiempo restante (igual que en petition_list)
    now = timezone.now()
    age = now - petition.created_at
    
    if not petition.is_active:
        time_left = None
    elif age < timedelta(days=8):
        expires_at = petition.created_at + timedelta(days=8)
        time_left = expires_at - now
    else:
        # Ya en modo extensión: encontrar próximo día de evaluación
        current_day = 8
        while True:
            next_eval = petition.created_at + timedelta(days=current_day)
            if next_eval > now:
                time_left = next_eval - now
                break
            current_day += 1

    context = {
        'petition': petition,
        'time_left': time_left,
        'comment_form': CommentForm(user=request.user) if request.user.is_authenticated else None,
    }
    return render(request, 'petitions/petition_detail.html', context)


from .forms import ResolveReportForm

@staff_member_required
def resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        form = ResolveReportForm(request.POST)
        if form.is_valid():
            # Marcar denuncia como resuelta
            report.reviewed = True
            report.resolved = True
            report.save()

            # Obtener mensaje personalizado
            message = form.cleaned_data['resolution_message']

            # Crear notificación para el denunciante
            Notification.objects.create(
                recipient=report.reporter,
                report=report,
                message=message
            )

            messages.success(request, "Denuncia resuelta y notificación enviada al denunciante.")
            return redirect('admin_reports')
    else:
        # Mensaje predeterminado sugerido
        suggested = f"Tu denuncia sobre '{report.get_report_type_display()}' ha sido revisada."
        form = ResolveReportForm(initial={'resolution_message': suggested})

    return render(request, 'petitions/resolve_report.html', {
        'report': report,
        'form': form
    })

@staff_member_required
def delete_reported_content(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        form = ResolveReportForm(request.POST)
        if form.is_valid():
            # Eliminar/ocultar contenido
            if report.petition:
                report.petition.is_active = False
                report.petition.archived_at = timezone.now()
                report.petition.save()
            elif report.comment:
                report.comment.is_hidden = True
                report.comment.save()

            # Marcar como resuelta
            report.reviewed = True
            report.resolved = True
            report.save()

            # Notificar al denunciante
            Notification.objects.create(
                recipient=report.reporter,
                report=report,
                message=form.cleaned_data['resolution_message']
            )

            messages.success(request, "Contenido eliminado y notificación enviada.")
            return redirect('admin_reports')
    else:
        suggested = "El contenido que denunciaste ha sido eliminado por violar las normas de la plataforma."
        form = ResolveReportForm(initial={'resolution_message': suggested})

    return render(request, 'petitions/delete_reported_content.html', {
        'report': report,
        'form': form
    })

@login_required
def my_reports(request):
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'petitions/my_reports.html', {'reports': reports})

@login_required
def notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    # Marcar todas como leídas
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'petitions/notifications.html', {'notifications': notifications})

################################################################################3
#PARTE EXPERIMENTAL 
###########################333
#Cambiar con responsabilidad puede llevar a fallos

from django.utils import timezone
from datetime import timedelta

def get_expiration_info(petition):

    now = timezone.now()
    age = now - petition.created_at

    # --- Calcular próximo vencimiento ---
    if age < timedelta(days=8):
        # Vencimiento del día 8
        expires_at = petition.created_at + timedelta(days=8)
    else:
        # Extensiones: día 9, 10, 11...
        day = int(age.days) + 1
        expires_at = petition.created_at + timedelta(days=day)

    # Total del ciclo actual
    total_duration = (expires_at - petition.created_at).total_seconds()

    # Tiempo restante
    remaining_seconds = max(0, (expires_at - now).total_seconds())

    return expires_at, int(total_duration), int(remaining_seconds)


def get_vote_growth(petition):
    """
    Devuelve cantidad de apoyos recibidos en las últimas 24 horas.
    """
    last_24h = timezone.now() - timedelta(hours=24)
    return petition.votes.filter(created_at__gte=last_24h).count()


def my_petitions(request):
    profile = request.user.userprofile

    # Activadas por el usuario
    active = Petition.objects.filter(author=profile, is_active=True)
    archived = Petition.objects.filter(author=profile, is_active=False)

    # Empaquetar datos para frontend
    active_data = []
    for p in active:
        expires_at, total_dur, remaining = get_expiration_info(p)
        growth = get_vote_growth(p)

        p.expires_at = expires_at
        p.total_duration = total_dur
        p.remaining_seconds = remaining
        p.vote_growth_24h = growth

        active_data.append(p)

    archived_data = []
    for p in archived:
        p.vote_growth_24h = get_vote_growth(p)
        archived_data.append(p)

    return render(request, "accounts/dashboard.html", {
        "active_petitions": active_data,
        "archived_petitions": archived_data,
    })
######################################################################
#Fin de parte experimental 
##########################################################33