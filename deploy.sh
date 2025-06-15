echo "Сборка и запуск контейнеров..."
docker-compose up --build -d

echo "Миграции..."
docker-compose exec web python manage.py migrate

echo "Сбор статики..."
docker-compose exec web python manage.py collectstatic --noinput

echo "Получение SSL сертификата от Let's Encrypt (только при первом запуске)..."
docker-compose run --rm certbot

echo "Перезапуск Nginx для применения SSL..."
docker-compose restart nginx

echo "✅ Готово! Приложение доступно по HTTPS!"
