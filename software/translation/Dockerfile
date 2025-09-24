FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app


COPY software/translation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY software/translation/ /app/
COPY database/translation_jpn_to_eng.csv /app/

# ポート開放 & 実行
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
