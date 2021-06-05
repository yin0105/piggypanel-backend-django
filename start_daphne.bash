#!/bin/bash

NAME="zohocrm"  # Name of the application
DJANGODIR=/home/grigorii/my/piggypanel-backend-django/zohocrm  # Django project directory
DJANGOENVDIR=/home/grigorii/my/piggypanel-backend-django/env  # Django project env

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source /home/grigorii/my/piggypanel-backend-django/env/bin/activate
source /home/grigorii/my/piggypanel-backend-django/.env
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start daphne
exec ${DJANGOENVDIR}/bin/daphne -u /home/grigorii/my/piggypanel-backend-django/env/run/daphne.sock --access-log - --proxy-headers zohocrm.asgi:application
