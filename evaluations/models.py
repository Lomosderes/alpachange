from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Teacher(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    department = models.CharField(max_length=100, verbose_name="Departamento/Área")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def average_rating(self):
        # Calcula el promedio general basado en las 4 categorías de todas sus reseñas
        reviews = self.review_set.all()
        if not reviews.exists():
            return 0
        
        # Obtenemos el promedio de cada categoría
        avgs = reviews.aggregate(
            avg_teaching=Avg('score_teaching'),
            avg_punctuality=Avg('score_punctuality'),
            avg_respect=Avg('score_respect'),
            avg_knowledge=Avg('score_knowledge')
        )
        
        # El promedio final es el promedio de los promedios
        total_avg = (avgs['avg_teaching'] + avgs['avg_punctuality'] + 
                     avgs['avg_respect'] + avgs['avg_knowledge']) / 4
        return round(total_avg, 1)

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"

class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Curso")
    code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Alumno")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Profesor")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Curso")
    
    # Calificaciones de 1 a 5
    score_teaching = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Enseñanza"
    )
    score_punctuality = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Puntualidad"
    )
    score_respect = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Respeto"
    )
    score_knowledge = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Conocimiento"
    )
    
    comment = models.TextField(verbose_name="Comentario")
    is_anonymous = models.BooleanField(default=True, verbose_name="¿Es anónimo?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        unique_together = ('user', 'teacher', 'course') # Evita duplicados por el mismo alumno para el mismo profesor y curso

    def __str__(self):
        return f"Reseña de {self.teacher} por {self.user}"
