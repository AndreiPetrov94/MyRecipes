# Дипломный проект Foodgram
Kittygram — социальная сеть для обмена фотографиями любимых питомцев. Это полностью рабочий проект, который состоит из бэкенд-приложения на Django и фронтенд-приложения на React. Проект доступен по электронному адресу: 
[foodgram-ap94.zapto.org](https://foodgram-ap94.zapto.org/).

[![Main Kittygram workflow](https://github.com/AndreiPetrov94/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/AndreiPetrov94/foodgram/actions/workflows/main.yml)

## Стек использованных технологий
* Python
* Django
* Django REST framework
* Postgresql
* Nginx
* Gunicorn
* Github Actions
* Docker
* Yandex Coud

## Разница между продакшн-версией и обычной версией для разработки
Продакшн — это окончательная версия продукта, которая доступна пользователям. Она должна работать стабильно и надежно.
Обычная версия (разработка или стейджинг) предназначена для тестирования и доработки кода. В ней могут быть недочеты и баги.

Когда использовать:
* Продакшн — когда продукт готов к работе с реальными пользователями.
* Обычную версию — когда нужно протестировать новый функционал или внести изменения перед релизом.

## Установка проекта на локальный компьютер из репозитория
* Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:<username>/foodgram.git
```
```
cd foodgram
```
* Установить и активировать виртуальное окружение:

Команда для Linux и macOS:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Команда для Windows:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
* Установить зависимости pip install -r requirements.txt
```
pip install -r requirements.txt
```
* В корневой папке создать файл .env:
```
touch .env
```
* В файле .env добавить переменные из файла .env.example
* Запустить проект:

Команда для Linux и macOS:
```
python3 manage.py runserver
```
Команда для Windows:
```
python manage.py runserver
```

## Деплой проекта на удаленный сервер
* Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:<username>/foodgram.git
```
```
cd foodgram
```
* Установить Docker Compose на сервер:
```
sudo apt update
```
```
sudo apt install curl
```
```
curl -fSL https://get.docker.com -o get-docker.sh
```
```
sudo sh ./get-docker.sh
```
```
sudo apt install docker-compose-plugin
```
* В корневой папке создать файл .env:
```
touch .env
```
* В файле .env добавить переменные из файла .env.example
* Установить и запустить Nginx:
```
sudo apt install nginx -y
```
```
sudo systemctl start nginx
```
* Настроить и включить firewall:
```
sudo ufw allow 'Nginx Full'
```
```
sudo ufw allow OpenSSH
```
```
sudo ufw enable
```
* Поменять настройки в файле Nginx:
```
sudo nano /etc/nginx/sites-enabled/default
```
```
server {
    listen 80;
    <server_name>;
    
    location / {
        proxy_set_header HOST $host;
        proxy_pass http://127.0.0.1:7000;
    }
}
```
* Выполните команду проверки конфигурации:
```
sudo nginx -t
```
```
sudo service nginx reload
```
* Загрузить и запустить образы из DockerHub:
```
sudo docker compose -f docker-compose.production.yml pull
```
```
sudo docker compose -f docker-compose.production.yml up -d
```
* Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

## Автор
* [Андрей Петров](https://github.com/AndreiPetrov94)