FROM tiangolo/uvicorn-gunicorn:python3.8-slim
RUN pip install pipenv
COPY ./app /app
RUN pipenv lock --requirements > requirements.txt
RUN pipenv install --no-cache-dir -r requirements.txt
