from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Teacher, Course, Review
from django.db.models import Avg, Q, Count

def teacher_list(request):
    query = request.GET.get('q', '')
    dept_filter = request.GET.get('dept', '')
    sort = request.GET.get('sort', 'rating')

    # Anotamos los promedios de las 4 categorías para poder filtrar/ordenar en DB
    teachers = Teacher.objects.annotate(
        avg_t=Avg('review__score_teaching'),
        avg_p=Avg('review__score_punctuality'),
        avg_r=Avg('review__score_respect'),
        avg_k=Avg('review__score_knowledge'),
        review_count=Count('review')
    )

    # Cálculo del promedio general (promedio de los promedios)
    # Nota: Si no hay reseñas, el valor será None, lo tratamos como 0 en el template o con Coalesce
    
    # Aplicar búsqueda
    if query:
        teachers = teachers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # Aplicar filtro de departamento
    if dept_filter:
        teachers = teachers.filter(department=dept_filter)

    # Lista de departamentos únicos para el dropdown
    departments = Teacher.objects.values_list('department', flat=True).distinct()

    # Convertimos a lista para manejar los promedios calculados por propiedad si fuera necesario,
    # pero aquí intentaremos mantenerlo en QuerySet para eficiencia.
    
    # Ordenamiento
    if sort == 'name':
        teachers = teachers.order_by('last_name', 'first_name')
    else:
        # Ordenar por rating (aproximado por la suma de promedios)
        # Usamos Python sort para la propiedad compleja si el volumen lo permite, 
        # o una expresión F() en DB.
        teachers = sorted(teachers, key=lambda t: t.average_rating, reverse=True)

    return render(request, 'evaluations/teacher_list.html', {
        'teachers': teachers,
        'departments': departments,
        'query': query,
        'dept_filter': dept_filter,
        'sort': sort
    })

def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    reviews = teacher.review_set.all().order_by('-created_at')
    
    category_avgs = reviews.aggregate(
        teaching=Avg('score_teaching'),
        punctuality=Avg('score_punctuality'),
        respect=Avg('score_respect'),
        knowledge=Avg('score_knowledge')
    )

    courses = Course.objects.all()

    return render(request, 'evaluations/teacher_detail.html', {
        'teacher': teacher,
        'reviews': reviews,
        'category_avgs': category_avgs,
        'courses': courses
    })

@login_required
def add_review(request, teacher_id):
    if request.method == 'POST':
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, pk=course_id)
        
        if Review.objects.filter(user=request.user, teacher=teacher, course=course).exists():
            messages.error(request, "Ya has calificado a este profesor para este curso.")
            return redirect('teacher_detail', pk=teacher.id)

        try:
            Review.objects.create(
                user=request.user,
                teacher=teacher,
                course=course,
                score_teaching=int(request.POST.get('score_teaching')),
                score_punctuality=int(request.POST.get('score_punctuality')),
                score_respect=int(request.POST.get('score_respect')),
                score_knowledge=int(request.POST.get('score_knowledge')),
                comment=request.POST.get('comment'),
                is_anonymous=request.POST.get('is_anonymous') == 'on'
            )
            messages.success(request, "Tu reseña ha sido publicada exitosamente.")
        except Exception as e:
            messages.error(request, f"Hubo un error al publicar tu reseña: {e}")

        return redirect('teacher_detail', pk=teacher.id)
    
    return redirect('teacher_list')
