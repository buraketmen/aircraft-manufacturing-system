FROM python:3.12-slim

ARG DEBIAN_FRONTEND="noninteractive"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV DJANGO_SETTINGS_MODULE=aircraft_manufacturing.settings.production

ENV APP_ROOT=/src
ENV CONFIG_ROOT=/config

RUN apt-get update &&\
    apt-get install -y supervisor &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/* &&\
    mkdir ${CONFIG_ROOT} 
    
COPY requirements.txt ${CONFIG_ROOT}/requirements.txt

RUN pip install --no-cache-dir -r ${CONFIG_ROOT}/requirements.txt &&\
    mkdir ${APP_ROOT}

COPY ./deploy/supervisor.conf /etc/supervisor/conf.d/app.conf
COPY ./aircraft_manufacturing/ ${APP_ROOT}/

RUN chmod -R u+r+x ${APP_ROOT}/management/scripts/

WORKDIR ${APP_ROOT}

RUN rm -f ${APP_ROOT}/db.sqlite3

ENTRYPOINT ["/bin/bash", "-c", \
    "${APP_ROOT}/management/scripts/wait-for-it.sh -t 180 ${POSTGRES_HOST}:${POSTGRES_PORT} -- echo 'Database is up...' \
    && ${APP_ROOT}/management/scripts/init.sh \
    && /usr/bin/supervisord -n -c /etc/supervisor/conf.d/app.conf"]

