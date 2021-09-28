# foodgram-project-react

![foodgram workflow](https://github.com/petrimma/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)

Онлайн-сервис и API для сайта **Foodgram** (**Продуктовый помощник**). На  сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка

Установите Docker:
> https://docs.docker.com/engine/install/ubuntu/

Клонируйте репозиторий: 
```
git clone https://github.com/petrimma/foodgram-project-react.git
```

В папку infra добавьте файл .env и укажите в нем следующие переменные:
```
DB_ENGINE=  
POSTGRES_DB=   
POSTGRES_USER=  
POSTGRES_PASSWORD=  
DB_HOST=  
DB_PORT=5432  
```

Запустите проект из директории infra:
```
docker-compose up
```

Документация:  
> http://localhost/api/docs/redoc.html

Админка:
>  http://localhost/admin/

Создать суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser 
```

## Технологии
- python
- django
- drf
- posgresql
- docker

## Автор проекта 
Римма Авакимова   
https://github.com/petrimma

