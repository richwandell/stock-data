FROM python:3.9.2-slim

RUN apt-get update \
    && apt-get install -y \
    ssh \
    screen \
    vim \
    libev-dev \
    python3-dev \
    libevdev2 \
    libpq-dev \
    libpcre3 \
    libpcre3-dev \
    gcc \
    nginx \
    htop \
    psmisc \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && update-rc.d -f nginx disable \
    && pip install pipenv

WORKDIR /app
ENV PIPENV_VENV_IN_PROJECT "enabled"

COPY docker/django/nginx.nginx /etc/nginx/nginx.conf
COPY . /app/

RUN cd /app \
    && pipenv install --skip-lock \
    && pipenv run python manage.py collectstatic

CMD pipenv run gunicorn \
    stonks.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -b :8000 \
    --user www-data \
    & nginx
