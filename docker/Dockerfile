FROM python:3.8

RUN apt update
RUN apt install -y python3-pip python3-venv

WORKDIR /opt/challenge
ENV VIRTUAL_ENV=/opt/challenge
RUN python3.8 -m venv env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD uvicorn src.main:app --port 8888
