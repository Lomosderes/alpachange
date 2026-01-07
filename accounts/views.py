from pyexpat.errors import messages
from django.shortcuts import render, redirect
import secrets
from django.core.mail import send_mail
from django.conf import settings
from .forms import EditProfileForm, RegisterForm
from .models import UserProfile

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #alias = form.cleaned_data['alias']
            

            # Extraer código de estudiante
            student_code = email.split('@')[0]
            if not student_code.isdigit() or len(student_code) != 10:
                form.add_error('email', 'El correo no contiene un código de estudiante válido.')
                return render(request, 'accounts/register.html', {'form': form})

            # Crear usuario (inactivo hasta verificación)
            user = User.objects.create_user(
                username=student_code,
                email=email,
                password=password,
                is_active=False
            )

            # Pasar datos a la señal
            user._registration_data = {
                #'alias': alias,
                'student_code': student_code,
                'is_verified': False
            }

            # Generar código de verificación
            verification_code = secrets.token_urlsafe(16)

            # Guardar en sesión
            request.session['verification_code'] = verification_code
            request.session['pending_user_id'] = user.id

            # Enviar correo
            send_mail(
                subject='Verifica tu cuenta AlpaChange UNTELS',
                message=f'Hola, usa este código para verificar tu cuenta: {verification_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('verify_email')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == request.session.get('verification_code'):
            user_id = request.session.get('pending_user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                profile = user.userprofile
                profile.is_verified = True
                profile.save()
                # Limpiar sesión
                del request.session['verification_code']
                del request.session['pending_user_id']
                return redirect('login') 
        # Si falla
        error = "Código incorrecto o expirado."
        return render(request, 'accounts/verify.html', {'error': error})
    return render(request, 'accounts/verify.html')

def public_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile

    # Comentarios públicos (todos, ya que son anónimos por alias)
    comments = user.comment_set.all().order_by('-created_at')

    # Peticiones: solo si el usuario lo permite
    petitions = []
    if profile.show_petitions:
        petitions = user.petition_set.filter(is_active=True) | user.petition_set.filter(is_active=False)
        petitions = petitions.order_by('-created_at')

    context = {
        'viewed_user': user,
        'profile': profile,
        'comments': comments,
        'petitions': petitions,
    }
    return render(request, 'accounts/profile.html', context)

# accounts/views.py

@login_required         
def edit_profile(request):
    profile = request.user.userprofile
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, user=user)
        if form.is_valid():
            # Guardar nombre real
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            # Guardar perfil
            profile.comment_alias = form.cleaned_data['comment_alias']
            profile.show_real_name = form.cleaned_data['show_real_name']
            profile.show_petitions = form.cleaned_data['show_petitions']
            profile.save()

            messages.success(request, "Configuración actualizada.")
            return redirect('edit_profile')
    else:
        form = EditProfileForm(user=user)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard(request):
    user = request.user
    my_active_petitions = user.petition_set.filter(is_active=True)
    my_archived_petitions = user.petition_set.filter(is_active=False)

    return render(request, 'accounts/dashboard.html', {
        'active_petitions': my_active_petitions,
        'archived_petitions': my_archived_petitions,
    })

def custom_login(request):
    entered_email = ""

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        entered_email = email

        # Autenticar por email (Django por defecto usa username)
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return redirect('petition_list')  # o dashboard
            else:
                messages.error(request, "Contraseña incorrecta.")
        except User.DoesNotExist:
            messages.error(request, "Correo no registrado.")

    return render(request, 'accounts/login.html', {
        'entered_email':entered_email
    })

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('petition_list')  # o 'home'