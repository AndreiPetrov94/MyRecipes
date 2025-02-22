python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py load_data_csv --no-input
gunicorn --bind 0.0.0.0:8000 foodgram.wsgi