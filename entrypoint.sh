if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python /app/innotter/manage.py migrate
python /app/innotter/manage.py runserver 0.0.0.0:8001

exec "$@"
