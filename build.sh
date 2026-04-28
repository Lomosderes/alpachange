# build.sh
set -e # Detener el script si algún comando falla

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
# Usamos --clear para limpiar cualquier basura previa
python manage.py collectstatic --noinput --clear

echo "Running migrations..."
python manage.py migrate --noinput

echo "Build complete."
