from .models import Teacher

def ranking_sidebar(request):
    # Obtiene los 5 profesores mejor calificados
    teachers = Teacher.objects.all()
    # Ordenar por la propiedad average_rating
    top_teachers = sorted(teachers, key=lambda t: t.average_rating, reverse=True)[:5]
    
    return {
        'top_teachers': top_teachers
    }
