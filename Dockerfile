FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/djharshit/flask-rbac"
LABEL maintainer="Harshit M"

ARG PORT=5000

WORKDIR /home/app

COPY . .

RUN wget -q -t3 'https://packages.doppler.com/public/cli/rsa.8004D9FF50437357.key' -O /etc/apk/keys/cli@doppler-8004D9FF50437357.rsa.pub && \
    echo 'https://packages.doppler.com/public/cli/alpine/any-version/main' | tee -a /etc/apk/repositories && \
    apk add --no-cache doppler

RUN chmod 755 install.sh && chmod 755 run.sh && sh install.sh

EXPOSE ${PORT}

CMD [ "sh", "run.sh" ]