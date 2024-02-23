FROM python:alpine3.10

WORKDIR /app

COPY . /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "flask", "run" ]