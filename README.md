Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.




# Описание

Этот проект предоставляет REST API для взаимодействия с приложением Yatube.


## Как запустить проект:

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/<ваш никнейм>/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```


## Примеры запросов к API

Получить список всех публикаций. При указании параметров limit и offset выдача должна работать с пагинацией:
```
GET http://127.0.0.1:8000/api/v1/posts/
```

Получение публикации по id:
```
http://127.0.0.1:8000/api/v1/posts/{id}/
```

Получение всех комментариев к публикации:
```
http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/
```

Получение комментария к публикации по id:
```
http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/{id}/
```

### В директории `postman_collection` находится Postman коллекция запросов `Yatube_API.postman_collection.json` для удобного тестирования API.
### Полная документация к API проекта в Redoc доступна по адресу: `http://127.0.0.1:8000/redoc/`



# Description

This project provides a REST API for interaction with the Yatube application.


## How to run the project:

Clone the repository and navigate to it in the command line:

```
git clone https://github.com/<ваш никнейм>/api_final_yatube.git
```

```
cd api_final_yatube
```

Create and activate a virtual environment:

```
python3 -m venv env
```

```
source env/bin/activate
```

Install dependencies from the requirements.txt file:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Run migrations:

```
python3 manage.py migrate
```


## API request examples

Get a list of all posts. When specifying the limit and offset parameters, output should work with pagination:
```
GET http://127.0.0.1:8000/api/v1/posts/
```

Get a post by id:
```
http://127.0.0.1:8000/api/v1/posts/{id}/
```

Get all comments for a post:
```
http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/
```

Get a comment for a post by id:
```
http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/{id}/
```

### The `postman_collection` directory contains a Postman collection of requests `Yatube_API.postman_collection.json` for convenient API testing.
### Full API documentation in Redoc is available at: `http://127.0.0.1:8000/redoc/`