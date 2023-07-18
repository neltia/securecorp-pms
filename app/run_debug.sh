export DJANGO_SETTINGS_MODULE=config.settings.debug
echo $DJANGO_SETTINGS_MODULE
python manage.py runserver 0.0.0.0:8080 --settings=config.settings.debug