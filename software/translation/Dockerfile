FROM python:3.11-slim

# パッケージインストール
RUN pip install --no-cache-dir streamlit pandas

# 作業ディレクトリ
WORKDIR /app

# アプリ本体をコピー
COPY . .

# 親ディレクトリの database もマウントされる前提で辞書を参照

# ポート開放 & 実行
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
