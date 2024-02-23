FROM python:3.11-slim

COPY requirements.txt .
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /app
VOLUME /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "2", "--port", "8000"]
