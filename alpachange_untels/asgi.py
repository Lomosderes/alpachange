"""
ASGI config for alpachange_untels project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys

from django.core.asgi import get_asgi_application

# Añadir la carpeta 'apps' al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpachange_untels.settings.local')

application = get_asgi_application()
