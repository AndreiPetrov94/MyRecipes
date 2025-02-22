python manage.py makemigrations
python manage.py migrate
gunicorn --bild 0.0.0.0:8000 foodgram.wsgi