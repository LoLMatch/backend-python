FROM python:alpine3.19

RUN addgroup -S usergroup && adduser -S user -G usergroup

WORKDIR /app

COPY . .

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev  && pip install -r requirements.txt

USER user

ENTRYPOINT [ "python", "-m", "api.front_api" ]