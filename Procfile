release: python manage.py migrate
web: if [ -z "${KEY_PATH}" ]; then echo "KEY_PATH not set"; gunicorn config.wsgi; else if [ -z "${CRT_PATH}" ]; then echo "CRT_PATH not set"; gunicorn config.wsgi; else gunicorn --certfile=$CRT_PATH --keyfile=$KEY_PATH config.wsgi; fi; fi;
worker: celery -A config worker -l INFO
beat: celery -A config beat -l INFO
