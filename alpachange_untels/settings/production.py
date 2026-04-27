from .base import *

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# Configuraciones adicionales de seguridad para producción
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
