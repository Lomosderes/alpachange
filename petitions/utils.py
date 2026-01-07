# petitions/utils.py
from django.utils import timezone
from datetime import timedelta
from .models import Petition, Vote

def should_archive_petition(petition):
    """
    Evalúa si una petición debe archivarse HOY.
    Devuelve True si debe archivarse.
    """
    now = timezone.now()
    age = now - petition.created_at  # en timedelta

    # Si tiene menos de 8 días, no se evalúa
    if age < timedelta(days=8):
        return False

    # Calcular votos en los primeros 7 días
    start_7 = petition.created_at
    end_7 = petition.created_at + timedelta(days=7)
    votes_first_7 = Vote.objects.filter(
        petition=petition,
        voted_at__gte=start_7,
        voted_at__lt=end_7
    ).count()

    # Verificar bloques de 1 día desde el día 8 en adelante
    current_day = 8
    while True:
        block_start = petition.created_at + timedelta(days=current_day - 1)
        block_end = petition.created_at + timedelta(days=current_day)

        # ¿Ya pasó este bloque?
        if block_end > now:
            # Aún no llegamos a este día de evaluación
            break

        # Contar votos en este bloque (1 día)
        votes_today = Vote.objects.filter(
            petition=petition,
            voted_at__gte=block_start,
            voted_at__lt=block_end
        ).count()

        # Umbral: 10% de los votos del bloque anterior
        if current_day == 8:
            threshold = 0.1 * votes_first_7
        else:
            # Para bloques posteriores, necesitamos los votos del bloque inmediato anterior
            prev_block_start = petition.created_at + timedelta(days=current_day - 2)
            prev_block_end = block_start
            votes_prev_block = Vote.objects.filter(
                petition=petition,
                voted_at__gte=prev_block_start,
                voted_at__lt=prev_block_end
            ).count()
            threshold = 0.1 * votes_prev_block

        # Si no alcanzó el umbral, se archiva
        if votes_today < threshold:
            return True

        # Si lo alcanzó, sigue activa → pasar al próximo bloque
        current_day += 1

    return False