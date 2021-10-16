FROM alpine:3.14.2

WORKDIR /alertmanager-webhook-pushsafer-python
COPY . /alertmanager-webhook-pushsafer-python

RUN apk update \
    && apk add py-pip bash gcc python3-dev musl-dev libffi-dev openssl-dev \
    && rm -rf /var/cache/apk/* \
    && pip install -r requirements.txt \
    && apk del py-pip gcc python3-dev musl-dev libffi-dev openssl-dev \
    && chmod +x run.sh

EXPOSE 9196

ENTRYPOINT ["./run.sh"]
