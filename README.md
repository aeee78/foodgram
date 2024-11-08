# RU
# Сайт кулинарных рецептов

![example workflow](https://github.com/aeee78/recipes/actions/workflows/main.yml/badge.svg)


Это веб-приложение для обмена рецептами, добавления их в избранное, подписки на авторов и создания списков покупок.

## Основные возможности

- **Аутентификация и регистрация** — Регистрация новых пользователей и вход для зарегистрированных.
- **Просмотр и поиск рецептов** — Сортировка по дате публикации и фильтрация по тегам.
- **Рецепты** — Полные инструкции с ингредиентами и изображениями, возможность добавления в избранное.
- **Профили пользователей** — Просмотр рецептов и подписки на авторов.
- **Избранное** — Сохранение любимых рецептов для быстрого доступа.
- **Список покупок** — Автоматическое создание списка ингредиентов для выбранных рецептов.
- **Создание рецептов** — Пользователи могут добавлять и редактировать собственные рецепты.
- **Административные функции** — (Опционально) Управление пользователями, рецептами и тегами.

## Технологии

- Python
- Django
- Docker
- PostgreSQL
- HTML / CSS
- JavaScript

## Демонстрация проекта

Проект развернут и доступен по следующему адресу: [edafood.ddns.net](http://edafood.ddns.net)

## Установка и запуск

### Локальная установка

1. Клонируйте репозиторий:
2. Создайте виртуальное окружение:
   ```
   python -m venv venv
   ```
3. Активируйте виртуальное окружение:
   - Windows: `source venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
5. Выполните миграции:
   ```
   python manage.py migrate
   ```
6. Запустите сервер разработки:
   ```
   python manage.py runserver
   ```

### Запуск с Docker

1. Клонируйте репозиторий:
2. Создайте и заполните `.env` файл на основе `.env.example`.
3. Запустите Docker контейнеры:
   ```
   docker-compose up -d
   ```
4. Выполните миграции и создайте суперпользователя:
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   docker-compose exec backend python manage.py collectstatic --no-input
   ```


## Разграничение прав

* **Гость:**  Может просматривать рецепты и профили пользователей.
* **Зарегистрированный пользователь:** Доступ ко всем функциям, кроме административных.
* **Администратор:**  Полный доступ ко всем функциям, включая управление пользователями, тегами и рецептами.



## Примеры API запросов

### Получение списка рецептов

```http
GET /api/recipes/
```

### Получение рецепта по ID

```http
GET /api/recipes/{id}/
```

### Создание рецепта (требуется авторизация)

```http
POST /api/recipes/
```

```json
{
  "ingredients": [
    {"id": 1, "amount": 100},
    {"id": 2, "amount": 50}
  ],
  "tags": [1, 2],
  "image": "data:image/png;base64,...",
  "name": "Название рецепта",
  "text": "Описание рецепта",
  "cooking_time": 30
}
```

### Добавление рецепта в избранное (требуется авторизация)

```http
POST /api/recipes/{id}/favorite/
```

### Удаление рецепта из избранного (требуется авторизация)

```http
DELETE /api/recipes/{id}/favorite/
```

### Поиск ингредиентов по имени

```http
GET /api/ingredients/?name=карт
```

Полная документация доступна по  адресу: [edafood.ddns.net/api/docs/](http://edafood.ddns.net/api/docs/)

*Примечание:* Замените `{id}` на фактический ID. Для авторизованных запросов используйте заголовок `Authorization: Token <ваш_токен>`.
---
# EN
# Culinary Recipe Website

![example workflow](https://github.com/aeee78/recipes/actions/workflows/main.yml/badge.svg)

This is a web application for sharing recipes, adding them to favorites, following authors, and creating shopping lists.

## Main Features

- **Authentication and Registration** — Registration of new users and login for registered users.
- **Viewing and Searching Recipes** — Sort by publication date and filter by tags.
- **Recipes** — Full instructions with ingredients and images, with an option to add to favorites.
- **User Profiles** — View recipes and follow authors.
- **Favorites** — Save favorite recipes for quick access.
- **Shopping List** — Automatically create a list of ingredients for selected recipes.
- **Creating Recipes** — Users can add and edit their own recipes.
- **Administrative Functions** — (Optional) Management of users, recipes, and tags.

## Technologies

- Python
- Django
- Docker
- PostgreSQL
- HTML / CSS
- JavaScript

## Project Demo

The project is deployed and available at the following address: [edafood.ddns.net](http://edafood.ddns.net)

## Installation and Launch

### Local Installation

1. Clone the repository: 
2. Create a virtual environment: 
```
python -m venv venv` 
```
4. Activate the virtual environment: 
- Windows: ```source venv\Scripts\activate``` 
- Linux/macOS: ```source venv/bin/activate```
4. Install dependencies: 
```
pip install -r requirements.txt
``` 
5. Run migrations: 
```
python manage.py migrate
``` 
7. Start the development server: 
```
python manage.py runserver
```

### Launch with Docker

1. Clone the repository:
2. Create and fill in the `.env` file based on `.env.example`.
3. Start Docker containers:
```
docker-compose up -d
```
4. Run migrations and create a superuser:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```

## Access Rights

* **Guest:** Can view recipes and user profiles.
* **Registered User:** Has access to all features except administrative ones.
* **Administrator:** Full access to all features, including managing users, tags, and recipes.

## API Request Examples

### Getting the Recipe List

```http
GET /api/recipes/
```

### Getting a Recipe by ID

```http
GET /api/recipes/{id}/
```

### Creating a Recipe (authorization required)

```http
POST /api/recipes/
```

```json
{
  "ingredients": [
    {"id": 1, "amount": 100},
    {"id": 2, "amount": 50}
  ],
  "tags": [1, 2],
  "image": "data:image/png;base64,...",
  "name": "Название рецепта",
  "text": "Описание рецепта",
  "cooking_time": 30
}
```

### Adding a Recipe to Favorites (authorization required)

```http
POST /api/recipes/{id}/favorite/
```

### Removing a Recipe from Favorites (authorization required)

```http
DELETE /api/recipes/{id}/favorite/
```

### Searching Ingredients by Name

```http
GET /api/ingredients/?name=карт
```

Full documentation is available at: [edafood.ddns.net/api/docs/](http://edafood.ddns.net/api/docs/)

*Note:* Replace `{id}` with the actual ID. For authorized requests, use the header `Authorization: Token <your_token>`.
