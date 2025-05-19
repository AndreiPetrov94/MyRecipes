# MyRecipes
MyRecipes — django проект, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

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

## Установка проекта на локальный компьютер из репозитория
* Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:<username>/MyRecipes.git
```
```
cd MyRecipes
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
git clone git@github.com:<username>/MyRecipes.git
```
```
cd MyRecipes
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
    <server_name>;
    
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
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
