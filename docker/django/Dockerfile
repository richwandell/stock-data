FROM node:13 as stage1
WORKDIR /app
ENV NODE_ENV production
ENV CI 1
COPY ./frontend/ /app/frontend/
RUN cd frontend && npm ci

FROM python:3.9.2-slim as stage2
WORKDIR /app
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

ENV PIPENV_VENV_IN_PROJECT "enabled"
ENV DJANGO_SECRET_KEY abc

COPY docker/django/nginx.nginx /etc/nginx/nginx.conf
COPY . /app/
COPY --from=stage1 /app/frontend/build/ /app/stonks/frontend/static/frontend/

RUN cd /app \
    && pipenv install --skip-lock \
    && pipenv run python manage.py collectstatic

CMD pipenv run gunicorn \
    stonks.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -b :8000 \
    --user www-data \
    & nginx
