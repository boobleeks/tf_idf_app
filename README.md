# TF-IDF API App
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Django](https://img.shields.io/badge/django-4.x-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)


## 🎥 Демо
Веб: http://37.9.53.58/
![TF-IDF Web UI](https://github.com/user-attachments/assets/ad5df9bd-ca60-485a-8227-f40b94052bb5)



## 📦 О проекте
Проект включает два Django-приложения:
1) Приложение реализует **API-интерфейс**, который позволяет:

- Управлять коллекциями документов
- Загружать и просматривать текстовые документы
- Выполнять Huffman-кодирование текста
- Вычислять TF-IDF метрики
- Регистрировать и аутентифицировать пользователей
- Получать системные метрики и статистику

2) **Web‑app** — обычное Django-приложение с UI:
   - загрузка файла через форму
   - отображение результатов TF‑IDF в таблице



## 🔧 Технологии

- Python 3.10+
- Django 4.x
- Django REST Framework
- PostgreSQL
- Docker + Docker Compose
- Gunicorn + Nginx



## 🚀 Быстрый старт
⚙️ Настройка .env
Откройте файл .env в редакторе и укажите свои значения:
Содержимое env.
```
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=tfidf_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_db_password
```
⚠️ Примечание: файл .env.example уже содержит шаблон — просто скопируйте и отредактируйте его. Ниже гайд:
Склонируйте репозиторий и запустите деплой-скрипт (deploy.sh):
```bash
git clone https://github.com/boobleeks/tf_idf_app.git
cd tf_idf_app
cp .env.example .env
vim или nano .env #подставьте свои значения
./deploy.sh #запустите скрипт
```
Скрипт deploy.sh выполнит за вас:
- установку зависимостей
- миграции
- запуск контейнеров Docker

После остается лишь открыть localhost c 8000 портом (http://localhost:8000/)



## 🚀 Ручная установка
```bash
git clone https://github.com/your_username/tf-idf-api.git
cd tf-idf-api
cp .env.example .env
docker-compose up --build
```



## 🗂 Структура проекта
```
├── Dockerfile                # Инструкция сборки образа Django-приложения
├── docker-compose.yml       # Запуск нескольких контейнеров: Django, Nginx, Postgres
├── deploy.sh                # Bash-скрипт для автоматического деплоя (build, migrate и т.д.)
├── requirements.txt         # Python-зависимости
├── manage.py                # CLI-скрипт управления Django-проектом
├── README.md                # Документация проекта

├── tf_idf/                  # Основной Django-проект (настройки)
│   ├── settings.py          # Настройки Django (базы данных, статика, приложения и т.д.)
│   ├── urls.py              # Глобальные маршруты URL
│   └── wsgi.py / asgi.py    # WSGI/ASGI входные точки сервера

├── api/                     # Django REST Framework приложение (API-часть)
│   ├── models.py            # Модели БД для коллекций и документов
│   ├── serializers.py       # Сериализаторы для API
│   ├── views.py             # Представления для API эндпоинтов
│   ├── urls.py              # Маршруты API
│   ├── metrics.py           # Логика метрик и сбора статистики
│   ├── decorators.py        # Кастомные декораторы
│   ├── utils.py             # Вспомогательные функции

├── tf_idf_calculator/       # Обычное Django-приложение с HTML-формой и обработкой TF-IDF
│   ├── views.py             # Представления (загрузка, отображение TF-IDF)
│   ├── forms.py             # Django-формы для загрузки файла
│   ├── functions.py         # Алгоритм TF-IDF, Huffman и др. логика
│   ├── templates/
│   │   └── upload.html      # Шаблон формы загрузки
│   ├── static/
│   │   └── styles.css       # Стили для HTML-шаблона
│   ├── urls.py              # URL-маршруты этого приложения
│   ├── validators.py        # Проверка загружаемых файлов
│   ├── models.py            # Модель, если есть сохранение данных в БД

├── nginx/
│   └── default.conf         # Конфигурация для Nginx (обработка статики, прокси на gunicorn)

├── media/                   # Загруженные пользователями файлы (настройка в MEDIA_ROOT)
├── staticfiles/            # Собранные статики из всех приложений (через collectstatic)
```

## 📦Структура базы данных
```
+-------------------+       +-------------------+       +-------------------+
|       User        |       |     Document      |       |    Collection     |
+-------------------+       +-------------------+       +-------------------+
| id (PK)           |       | id (PK, UUID)     |       | id (PK)           |
| username          |<----->| owner (FK)        |<----->| owner (FK)        |
| password          |       | title             |       | name              |
|                   |       | file              |       | created_at        |
|                   |       | created_at        |       | updated_at        |
|                   |       | updated_at        |       |                   |
+-------------------+       +-------------------+       +-------------------+
                                    ^                           ^
                                    |                           |
                                    |                           |
                                    |                           |
                                    |                           |
                            +-------------------+       +-------------------+
                            |   Statistics      |       | documents (M2M)   |
                            +-------------------+       +-------------------+
                            | id (PK)           |       | id (PK)           |
                            | document (FK)     |       | collection_id (FK)|
                            | collection (FK)   |       | document_id (FK)  |
                            | data (JSON)       |       +-------------------+
                            | created_at        |
                            +-------------------+
```

User (наследуется от AbstractUser) - центральная модель для аутентификации

### Document:
Имеет ForeignKey к User (owner)
Связан с Collection через ManyToManyField (через промежуточную таблицу documents)

### Collection:
Имеет ForeignKey к User (owner)
Связан с Document через ManyToManyField

### Statistics:
Имеет ForeignKey как к Document, так и к Collection (может быть связана с одним из них)
Содержит JSON-данные

### Отношения:

User → Document: One-to-Many (один пользователь - много документов) 

User → Collection: One-to-Many (один пользователь - много коллекций)

Document ↔ Collection: Many-to-Many (документ может быть в нескольких коллекциях, коллекция содержит несколько документов)

Statistics → Document/Collection: One-to-Many (один документ/коллекция - много статистик)

## 📄API Эндпоинты localhost:<ваш порт>/api/

🔐 Авторизация
Используется токен-авторизация. После логина получаете токен и передаёте его в заголовке (headers):
```bash
Authorization: Token <ваш_токен>
```

### 🔐 Аутентификация и Пользователи
| Метод  | URL                  | Описание                        |
| ------ | -------------------- | ------------------------------- |
| POST   | `/register/`         | Регистрация нового пользователя |
| POST   | `/login/`            | Авторизация, получение токена   |
| POST   | `/logout/`           | Выход (аннулирование токена)    |
| POST   | `/user/<id>/`        | Смена пароля                    |
| DELETE | `/user/<id>/delete/` | Удаление пользователя           |
### 📚 Документы

| Метод  | URL                                   | Описание                                    |
| ------ | ------------------------------------- | ------------------------------------------- |
| GET    | `/documents/`                         | Получить список документов                  |
| POST   | `/documents/`                         | Загрузить новый документ                    |
| GET    | `/documents/<uuid:doc_id>`            | Получить содержимое документа               |
| DELETE | `/documents/<uuid:doc_id>`            | Удалить документ                            |
| GET    | `/documents/<uuid:doc_id>/statistics` | Получить статистику документа               |
| GET    | `/documents/<uuid:doc_id>/huffman/`   | Получить Huffman-кодировку текста документа |

### 📁 Коллекции

| Метод  | URL                                           | Описание                                    |
| ------ | --------------------------------------------- | ------------------------------------------- |
| GET    | `/collections/`                               | Список всех коллекций текущего пользователя |
| POST   | `/collections/`                               | Создать новую коллекцию                     |
| GET    | `/collections/<int:pk>/`                      | Получить детали коллекции                   |
| DELETE | `/collections/<int:pk>/`                      | Удалить коллекцию                           |
| GET    | `/collections/<int:pk>/statistics/`           | Получить статистику по коллекции            |
| POST   | `/collections/<int:pk>/<uuid:doc_id>/`        | Добавить документ в коллекцию               |
| DELETE | `/collections/<int:pk>/<uuid:doc_id>/delete/` | Удалить документ из коллекции               |

### 📊 Статистика и Система
| Метод | URL         | Описание                              |
| ----- | ----------- | ------------------------------------- |
| GET   | `/metrics/` | Общая статистика обработки документов |
| GET   | `/status/`  | Статус сервера                        |
| GET   | `/version/` | Версия приложения                     |


## 📘 Документация API (Swagger)

После запуска проекта доступна интерактивная документация API:

* [http://localhost:8000/swagger/](http://localhost:8000/swagger/) — Swagger UI

> Здесь вы можете удобно протестировать все эндпоинты: загрузку документа, расчёт TF‑IDF, Huffman‑кодирование, метрики и др.


## 🔧 Изменения
Все изменения проекта смотреть тут - [CHANGELOG](https://github.com/boobleeks/tf_idf_app/blob/main/changelog.md)


## 👤 Автор

[Gulom-Mirzo](https://github.com/boobleeks)  
Telegram: [@gulom_mirzo](https://t.me/gulom_mirzo)  
Email: abdugaforovvv@gmail.com



## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для подробностей.





