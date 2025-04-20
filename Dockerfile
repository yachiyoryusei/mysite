# ベースイメージとしてPythonを使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要な依存関係をコピー
COPY requirements.txt .

# pipをアップグレード
RUN pip install --upgrade pip

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Flaskアプリケーションを実行
CMD ["python", "app.py"]
