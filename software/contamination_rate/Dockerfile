FROM python:3.12-rc-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get -y upgrade && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080

COPY . /app

ENTRYPOINT ["streamlit", "run"]

CMD ["main.py", "--server.port=8080"]
