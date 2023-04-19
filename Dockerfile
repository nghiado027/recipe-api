FROM python:3.11.2-alpine3.17
LABEL maintainer="do.nghia027@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

#not development mode
ENV DEV=false

# create venv and upgrade pip, install requirements, add user in alpine image
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    #add package & install (postgresql client), use --virtual to remove later then install
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV="true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    #cleaning
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    #add user
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

#update python path enviroment
ENV PATH="/py/bin:$PATH"

USER django-user
