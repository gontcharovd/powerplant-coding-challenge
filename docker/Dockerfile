FROM python:3.8-alpine

WORKDIR /opt/challenge

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD uvicorn src.rest_api:app --port 8888
