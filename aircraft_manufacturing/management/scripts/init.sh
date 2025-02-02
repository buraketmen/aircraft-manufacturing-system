#!/bin/bash

set +e

if [ -f "/src/management/scripts/init_script.lock" ]; then
    echo "The script has already been executed, exiting..."
    exit 0
fi

touch /src/management/scripts/init_script.lock
export DEBIAN_FRONTEND=noninteractive
python manage.py create_database
python manage.py makemigrations
python manage.py migrate
