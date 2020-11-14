FROM tiangolo/uvicorn-gunicorn:python3.8-slim
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt
