"""
WSGI config for alpachange_untels project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpachange_untels.settings')

application = get_wsgi_application()

from whitenoise import WhiteNoise

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.MEDIA_ROOT)