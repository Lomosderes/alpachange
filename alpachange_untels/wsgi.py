"""
WSGI config for alpachange_untels project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

from django.conf import settings
from django.core.wsgi import get_wsgi_application

# Añadir la carpeta 'apps' al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpachange_untels.settings.local')

application = get_wsgi_application()

from whitenoise import WhiteNoise
application = WhiteNoise(application, root=settings.MEDIA_ROOT)