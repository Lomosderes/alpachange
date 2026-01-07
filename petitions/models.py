# petitions/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Petition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    #####################################################################################
    votes = models.ManyToManyField(User, through='Vote', related_name='voted_petitions')
    #####################################################################################
    is_active = models.BooleanField(default=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="petitions"
)

    
    followup_pdf = models.FileField(upload_to='followups/', null=True, blank=True)
    followup_notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def vote_count(self):
        return self.vote_set.count()

    def created_by_alias(self):
        return self.author.userprofile.alias

#relación DÉBIL
class PetitionAttachment(models.Model):
    """
    Adjunto que sólo existe mientras exista la petición.
    No tiene id propio → clave compuesta (petición + orden).
    """
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()   # 1,2,3…
    file = models.FileField(upload_to='attachments/')
    caption = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ('petition', 'order')   # ← clave compuesta
        ordering = ['order']

    def __str__(self):
        return f"Adjunto {self.order} de {self.petition.title}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'petition')

class Comment(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50)  # alias por comentario (pero fijo por usuario)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_hidden = models.BooleanField(default=False)  # oculto si es denunciado y revisado

    def __str__(self):
        return f"{self.alias}: {self.content[:30]}"


class Report(models.Model):
    REPORT_TYPES = [
        ('petition', 'Petición'),
        ('comment', 'Comentario'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Denuncia por {self.reporter} - {self.report_type}"

from django.core.exceptions import ValidationError

class PromoContent(models.Model):

    def validate_promo_file(value):
        if not value.name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm')):
            raise ValidationError('Solo se permiten imágenes (png, jpg, gif) y videos (mp4, webm).')
    
    POSITION_CHOICES = [
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
    ]
    
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='promo/', validators=[validate_promo_file])
    link = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='right')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.position})"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.recipient} sobre denuncia {self.report.id}"


