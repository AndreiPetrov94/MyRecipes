python manage.py makemigrations --no-input
python manage.py migrate --no-input
gunicorn --bild 0.0.0.0:8000 foodgram.wsgi