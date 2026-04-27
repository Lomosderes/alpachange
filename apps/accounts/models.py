from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_code = models.CharField(
        max_length=12, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='El código de estudiante debe tener exactamente 10 dígitos numéricos.',
                code='invalid_student_code'
            )
        ]
    )  # ej. 2313010818
    is_verified = models.BooleanField(default=False)
    show_real_name = models.BooleanField(default=False) # si quiere mostrar su nombre real
    comment_alias = models.CharField(max_length=50, blank=True, null=True) 
    show_petitions = models.BooleanField(default=True)  # ¿mostrar peticiones en perfil?
    
    def __str__(self):
        return f"{self.user.username} ({self.student_code or 'Sin código'})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Extraer código si el email tiene formato válido
        student_code = None
        if instance.email and instance.email.endswith('@untels.edu.pe'):
            sc = instance.email.split('@')[0]
            if sc.isdigit() and len(sc) == 10:
                student_code = sc
        
        # Crear UserProfile con valores por defecto
        # Usamos None en lugar de strings vacíos para evitar colisiones en campos UNIQUE
        profile = UserProfile.objects.create(
            user=instance,
            student_code=student_code
        )
        
        # Si el usuario fue creado desde el registro (con datos adicionales en la instancia)
        if hasattr(instance, '_registration_data'):
            reg_data = instance._registration_data
            if 'comment_alias' in reg_data:
                profile.comment_alias = reg_data['comment_alias']
            if 'student_code' in reg_data:
                # Validar código antes de asignar
                sc = reg_data['student_code']
                if sc and str(sc).isdigit() and len(str(sc)) == 10:
                    profile.student_code = sc
            if 'is_verified' in reg_data:
                profile.is_verified = reg_data['is_verified']
            profile.save()
