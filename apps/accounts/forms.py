from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .utils import contains_profanity
from accounts.models import UserProfile

class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@untels.edu.pe'):
            raise ValidationError("Solo se permiten correos institucionales (@untels.edu.pe).")
        student_code = email.split('@')[0]
        if not student_code.isdigit() or len(student_code) != 10:
            raise ValidationError("El correo no contiene un código de estudiante válido.")
    
        if UserProfile.objects.filter(student_code=student_code).exists():
            raise ValidationError("Este código de estudiante ya está registrado.")
    
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password_confirm'):
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    comment_alias = forms.CharField(max_length=50, required=False)
    show_real_name = forms.BooleanField(required=False)
    show_petitions = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = []  # No editamos User directamente aquí, pero lo usamos

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            profile = self.user.userprofile
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['comment_alias'].initial = profile.comment_alias or ''
            self.fields['show_real_name'].initial = profile.show_real_name
            self.fields['show_petitions'].initial = profile.show_petitions

    def clean_comment_alias(self):
        alias = self.cleaned_data.get('comment_alias', '').strip()
        if not alias:
            return None
        if len(alias) < 3:
            raise forms.ValidationError("El alias debe tener al menos 3 caracteres.")
        if contains_profanity(alias):
            raise forms.ValidationError("El alias contiene lenguaje inapropiado.")
        return alias