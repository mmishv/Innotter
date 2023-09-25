until cd /app/innotter
do
    echo "Waiting for server volume..."
done

celery -A innotter worker -l info

exec "$@"
