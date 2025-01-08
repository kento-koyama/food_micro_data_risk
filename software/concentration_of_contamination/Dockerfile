FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get -y upgrade && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080

COPY . /app

ENTRYPOINT ["streamlit", "run"]

CMD ["risk_concentration_test_JH.py", "--server.port=8080"]
