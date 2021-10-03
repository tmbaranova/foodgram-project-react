![yamdb_workflow](https://github.com/tmbaranova/foodgram-project-react/actions/workflows/backend.yml/badge.svg?branch=master)



# Foodgram - продуктовый помощник
Foodgram - сервис для публикации рецептов. 

## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```
git clone https://github.com/tmbaranova/foodgram-project-react
```
## Для работы с удаленным сервером (на ubuntu):
### Выполните вход на свой удаленный сервер

### Установите docker на сервер:
```
sudo apt install docker.io 
```
### Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
### Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
### Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
### На сервере создайте файл .env (nano .env) и заполните переменные окружения (или создайте этот файл локально и скопируйте файл по аналогии с предыдущим пунктом):
```
SECRET_KEY=<секретный ключ проекта django>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432
POSTGRES_PASSWORD=<пароль для базы данных> 
DB_NAME=<название базы данных>
POSTGRES_USER=<имя пользователя>
```
### На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```
### После успешной сборки на сервере выполните команды:
#### Соберите статические файлы:
```
sudo docker-compose exec backend python manage.py collectstatic --noinput
```
#### Применитe миграции:
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
#### Загрузите ингридиенты в базу данных (не обязательно)
```
sudo docker-compose exec backend python manage.py loaddata fixtures/ingredients.json
```
#### Создать суперпользователя Django:
```
sudo docker-compose exec backend python manage.py createsuperuser
```

## Проект доступен по адресу http://84.201.177.123
### Суперюзер:
```
qwerty@gmail.com
admin2508
```
