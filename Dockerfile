FROM tiangolo/uvicorn-gunicorn:python3.8-slim
RUN pip install pipenv
RUN pipenv lock --requirements > app/requirements.txt
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt
