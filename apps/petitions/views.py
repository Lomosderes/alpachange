# petitions/views.py
import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone

from .models import Category, Notification, Petition, Report, Vote, Comment
from .forms import PetitionForm, CommentForm, ResolveReportForm
from evaluations.models import Teacher

# --- Funciones de Utilidad (Lógica de Negocio) ---

def get_expiration_info(petition):
    """
    Calcula la fecha de vencimiento, duración total del ciclo y tiempo restante.
    Optimizado para evitar bucles.
    """
    now = timezone.now()
    if not petition.is_active:
        return None, 0, 0

    age = now - petition.created_at
    
    if age < timedelta(days=8):
        # Vencimiento inicial del día 8
        expires_at = petition.created_at + timedelta(days=8)
    else:
        # Modo extensión: vence cada 24 horas después del día 8
        days_passed = age.days
        expires_at = petition.created_at + timedelta(days=days_passed + 1)

    total_duration = (expires_at - petition.created_at).total_seconds()
    remaining_seconds = max(0, (expires_at - now).total_seconds())

    return expires_at, int(total_duration), int(remaining_seconds)

def get_vote_growth(petition):
    """Devuelve cantidad de apoyos recibidos en las últimas 24 horas."""
    last_24h = timezone.now() - timedelta(hours=24)
    return petition.votes.filter(vote__voted_at__gte=last_24h).count()

# --- Vistas de Usuario ---

@login_required
def create_petition(request):
    if not request.user.userprofile.is_verified:
        messages.error(request, "Debes verificar tu correo institucional antes de crear una petición.")
        return redirect('verify_email')

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

    petition = get_object_or_404(Petition, id=petition_id, is_active=True)
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

def petition_list(request):
    petitions = Petition.objects.filter(is_active=True) \
        .annotate(vote_count_val=Count('votes')) \
        .order_by('-vote_count_val', '-created_at')

    petition_data = []
    for p in petitions:
        expires_at, _, remaining = get_expiration_info(p)
        petition_data.append({
            'petition': p,
            'vote_count': p.vote_count_val,
            'time_left': timedelta(seconds=remaining),
            'end_timestamp': int(expires_at.timestamp()) * 1000 if expires_at else 0
        })

    # Estadísticas para el HERO
    last_24h = timezone.now() - timedelta(days=1)
    total_votes_today = Vote.objects.filter(voted_at__gte=last_24h).count()
    approved_petitions = Petition.objects.filter(is_active=False).count()
    
    # Contar profesores que tienen al menos una reseña
    rated_teachers_count = Teacher.objects.filter(review__isnull=False).distinct().count()

    return render(request, 'petitions/list.html', {
        'petition_data': petition_data,
        'total_votes_today': total_votes_today,
        'approved_petitions': approved_petitions,
        'rated_teachers_count': rated_teachers_count,
    })

def petition_detail(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    expires_at, _, remaining = get_expiration_info(petition)
    
    context = {
        'petition': petition,
        'time_left': timedelta(seconds=remaining) if petition.is_active else None,
        'comment_form': CommentForm(user=request.user) if request.user.is_authenticated else None,
    }
    return render(request, 'petitions/petition_detail.html', context)

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

            # Guardar alias en perfil si es nuevo o ha cambiado
            alias = form.cleaned_data['alias']
            profile = request.user.userprofile
            if profile.comment_alias != alias:
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

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    report_type = data.get("type")
    reason = data.get("reason", "").strip()
    if not reason:
        return JsonResponse({"error": "Debes indicar una razón."}, status=400)

    report = Report(reporter=request.user, reason=reason, report_type=report_type)

    if report_type == "petition":
        report.petition = get_object_or_404(Petition, id=data.get("petition_id"))
    elif report_type == "comment":
        report.comment = get_object_or_404(Comment, id=data.get("comment_id"))
    else:
        return JsonResponse({"error": "Datos no válidos."}, status=400)

    report.save()
    return JsonResponse({"success": True, "message": "Denuncia enviada correctamente."})

# --- Vistas de Administración (Staff) ---

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

@staff_member_required
def resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        form = ResolveReportForm(request.POST)
        if form.is_valid():
            report.reviewed = report.resolved = True
            report.save()
            Notification.objects.create(
                recipient=report.reporter,
                report=report,
                message=form.cleaned_data['resolution_message']
            )
            messages.success(request, "Denuncia resuelta y notificación enviada.")
            return redirect('admin_reports')
    else:
        suggested = f"Tu denuncia sobre '{report.get_report_type_display()}' ha sido revisada."
        form = ResolveReportForm(initial={'resolution_message': suggested})

    return render(request, 'petitions/resolve_report.html', {'report': report, 'form': form})

@staff_member_required
def delete_reported_content(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        form = ResolveReportForm(request.POST)
        if form.is_valid():
            if report.petition:
                report.petition.is_active = False
                report.petition.archived_at = timezone.now()
                report.petition.save()
            elif report.comment:
                report.comment.is_hidden = True
                report.comment.save()

            report.reviewed = report.resolved = True
            report.save()
            Notification.objects.create(
                recipient=report.reporter,
                report=report,
                message=form.cleaned_data['resolution_message']
            )
            messages.success(request, "Contenido eliminado y notificación enviada.")
            return redirect('admin_reports')
    else:
        suggested = "El contenido que denunciaste ha sido eliminado por violar las normas."
        form = ResolveReportForm(initial={'resolution_message': suggested})

    return render(request, 'petitions/delete_reported_content.html', {'report': report, 'form': form})

# --- Vistas de Perfil y Notificaciones ---

@login_required
def my_reports(request):
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'petitions/my_reports.html', {'reports': reports})

@login_required
def notifications(request):
    notifs = request.user.notifications.all().order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'petitions/notifications.html', {'notifications': notifs})

@login_required
def my_petitions(request):
    active = Petition.objects.filter(author=request.user.userprofile, is_active=True)
    archived = Petition.objects.filter(author=request.user.userprofile, is_active=False)

    for p in active:
        expires_at, total_dur, remaining = get_expiration_info(p)
        p.expires_at = expires_at
        p.total_duration = total_dur
        p.remaining_seconds = remaining
        p.vote_growth_24h = get_vote_growth(p)

    for p in archived:
        p.vote_growth_24h = get_vote_growth(p)

    return render(request, "accounts/dashboard.html", {
        "active_petitions": active,
        "archived_petitions": archived,
    })
