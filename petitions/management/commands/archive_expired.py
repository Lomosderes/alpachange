# petitions/management/commands/archive_expired.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from petitions.models import Petition
from petitions.utils import should_archive_petition

class Command(BaseCommand):
    help = 'Archiva peticiones que no cumplen el umbral de votos'

    def handle(self, *args, **options):
        active_petitions = Petition.objects.filter(is_active=True)
        archived_count = 0

        for petition in active_petitions:
            if should_archive_petition(petition):
                petition.is_active = False
                petition.archived_at = timezone.now()
                petition.save()
                archived_count += 1
                self.stdout.write(f"Archivada: {petition.title}")

        self.stdout.write(
            self.style.SUCCESS(f'{archived_count} peticiones archivadas.')
        )