import dj_database_url
import os
from .base import *

DEBUG = config('DEBUG', default=False, cast=bool)

# Permitir el dominio de Vercel y los definidos en .env
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.vercel.app,localhost').split(',')

# Configuración de Base de Datos para Neon/PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuración de archivos estáticos con WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Cambiamos a la versión que no requiere un manifiesto estricto para evitar errores 404
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ============================
# CONFIGURACIÓN DE CLOUDINARY
# ============================
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Configuraciones de seguridad para producción
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host.startswith('.')]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
