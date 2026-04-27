# Alpachange 🦙📢

**Alpachange** es una plataforma web universitaria de participación estudiantil desarrollada con **Django**. Inspirada en herramientas de cambio social, busca democratizar la voz de los estudiantes, facilitando la visibilización y el seguimiento de problemáticas institucionales dentro de la universidad.

---

## 🚀 Estado Actual y Mejoras Recientes

El proyecto ha pasado por una fase de refactorización y expansión significativa:
- **Arquitectura Modular:** Las aplicaciones se han organizado bajo el directorio `apps/` para una mejor escalabilidad.
- **Configuración Profesional:** División de `settings` en entornos `base`, `local` y `production`.
- **Nuevo Módulo de Evaluaciones:** Implementación de un sistema de evaluación de docentes.
- **Automatización:** Comando de gestión para el archivado automático de peticiones expiradas.
- **Seguridad y Moderación:** Integración de filtros de profanidad y validaciones robustas en perfiles de usuario.

---

## ✨ Características Principales

### 📋 Gestión de Peticiones
- **Creación y Votación:** Los estudiantes pueden registrar reportes o peticiones y recolectar firmas (votos).
- **Categorización:** Clasificación de peticiones por áreas (Académica, Administrativa, Infraestructura, etc.).
- **Seguimiento Institucional:** Soporte para que las autoridades suban notas de seguimiento y documentos PDF.
- **Expiración Inteligente:** Sistema de archivado automático basado en la vigencia de la petición.

### 🎓 Evaluaciones Docentes (Nuevo)
- Sistema dedicado para que los alumnos califiquen y comenten sobre el desempeño académico, promoviendo la transparencia educativa.

### 👤 Perfiles y Comunidad
- **Privacidad:** Opción de participar con alias para proteger la identidad del estudiante.
- **Notificaciones:** Sistema interno para informar sobre actualizaciones en peticiones seguidas.
- **Dashboard:** Panel personalizado para gestionar peticiones propias y participación.

---

## 🛠️ Tecnologías y Herramientas

- **Core:** Python 3.x & Django 5.x
- **Arquitectura:** Estructura modular (Apps separadas)
- **Frontend:** HTML5, CSS3 (Estrategia de diseño institucional OKLCH), Django Templates
- **Seguridad:** Scikit-learn & Profanity-check para moderación de contenido
- **Almacenamiento:** SQLite (Local) / Compatible con PostgreSQL (Producción)
- **Despliegue:** Whitenoise para estáticos y Django-storages para medios

---

## 📂 Estructura del Proyecto

```text
alpachange/
├── alpachange_untels/ # Configuración central y WSGI/ASGI
│   └── settings/      # Configuraciones divididas (Base, Local, Prod)
├── apps/              # Lógica de negocio modular
│   ├── accounts/      # Gestión de usuarios, perfiles y autenticación
│   ├── petitions/     # Core de peticiones, votos, comentarios y categorías
│   └── evaluations/   # Sistema de evaluación docente
├── templates/         # Plantillas globales y específicas por app
├── static/            # Recursos estáticos (Logos, favicon)
├── media/             # Archivos de usuario (PDFs de seguimiento, imágenes promo)
├── manage.py
└── requirements.txt
```

---

## 🛠️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd alpachange
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Copia el archivo `.env.example` a `.env` y completa tus credenciales (Base de datos, Email, etc.).

5. **Migrar y Correr:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---
*Desarrollado con ❤️ para la comunidad estudiantil.*
