cd /app/innotter/
celery -A innotter worker -l info

exec "$@"
