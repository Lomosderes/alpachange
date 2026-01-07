from django.db import models

# Create your models here.

# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_code = models.CharField(max_length=12, unique=True)  # ej. 2313010818
    #alias = models.CharField(max_length=50, unique=True)
    is_verified = models.BooleanField(default=False)
    show_real_name = models.BooleanField(default=False)# si quiere mostrar su nombre real
    comment_alias = models.CharField(max_length=50, blank=True, null=True) 
    show_petitions = models.BooleanField(default=True)            # ¿mostrar peticiones en perfil?
    
    def __str__(self):
        return f"{self.alias} ({self.student_code})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Extraer código si el email tiene formato válido
        student_code = None
        if instance.email.endswith('@untels.edu.pe'):
            sc = instance.email.split('@')[0]
            if sc.isdigit() and len(sc) == 10:  
                student_code = sc
        
        # Crear UserProfile con valores por defecto
        profile = UserProfile.objects.create(
            user=instance,
            student_code=student_code or 'unknown',
            #alias=f"user_{instance.id}"  # temporal
        )
        
        # Si el usuario fue creado desde el registro (con sesión), actualizarlo
        if hasattr(instance, '_registration_data'):
            reg_data = instance._registration_data
            profile.alias = reg_data.get('alias', profile.alias)
            profile.student_code = reg_data.get('student_code', profile.student_code)
            profile.is_verified = reg_data.get('is_verified', False)
            profile.save()
