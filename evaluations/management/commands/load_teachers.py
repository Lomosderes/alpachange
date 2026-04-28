import os
from django.core.management.base import BaseCommand
from evaluations.models import Teacher

class Command(BaseCommand):
    help = 'Carga profesores desde un archivo txt'

    def handle(self, *args, **options):
        file_path = 'profesores.txt'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Archivo {file_path} no encontrado'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                
                try:
                    last_name, first_name = line.split(',', 1)
                    last_name = last_name.strip()
                    first_name = first_name.strip()

                    teacher, created = Teacher.objects.get_or_create(
                        first_name=first_name,
                        last_name=last_name,
                        defaults={'department': 'General'}
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Creado: {teacher}'))
                    # else:
                    #    self.stdout.write(self.style.WARNING(f'Ya existe: {teacher}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error procesando linea "{line}": {e}'))

        self.stdout.write(self.style.SUCCESS('Carga de profesores finalizada'))
