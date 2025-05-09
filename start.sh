#!/bin/bash
cd /home/webmaster/django-apps
source ./venv/bin/activate
exec python manage.py runserver 0.0.0.0:8094
