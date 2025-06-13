echo "Сборка и запуск контейнеров..."
docker-compose up --build -d

echo "Миграции..."
docker-compose exec web python manage.py migrate

echo "Сбор статики..."
docker-compose exec web python manage.py collectstatic --noinput

echo "✅ Готово!"
