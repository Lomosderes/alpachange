# petitions/utils.py
from django.utils import timezone
from datetime import timedelta
from .models import Vote

def should_archive_petition(petition):
    """
    Evalúa si una petición debe archivarse basándose en el crecimiento de votos.
    Optimizado para reducir consultas a la base de datos.
    """
    now = timezone.now()
    age = now - petition.created_at

    # Si tiene menos de 8 días, no se archiva aún
    if age < timedelta(days=8):
        return False

    # Obtener todos los votos relevantes de una sola vez
    all_votes = list(Vote.objects.filter(petition=petition).values_list('voted_at', flat=True))
    
    def count_votes_in_range(start, end):
        return sum(1 for v in all_votes if start <= v < end)

    # Votos en los primeros 7 días (Bloque inicial)
    votes_first_7 = count_votes_in_range(petition.created_at, petition.created_at + timedelta(days=7))

    # Verificar cada día desde el día 8 hasta hoy
    current_day = 8
    prev_votes = votes_first_7
    
    # Calculamos cuántos días completos han pasado para evaluar
    total_days_to_check = age.days # ej. si age es 8.5 días, age.days es 8
    
    for day in range(8, total_days_to_check + 1):
        block_start = petition.created_at + timedelta(days=day - 1)
        block_end = petition.created_at + timedelta(days=day)
        
        # Si el bloque termina en el futuro, no lo evaluamos (aunque total_days_to_check previene esto)
        if block_end > now:
            break
            
        votes_today = count_votes_in_range(block_start, block_end)
        
        # Umbral: 10% de los votos del bloque anterior
        threshold = 0.1 * prev_votes
        
        if votes_today < threshold:
            return True
            
        prev_votes = votes_today
        
    return False