FROM tiangolo/uvicorn-gunicorn:python3.8-slim
RUN pip install pipenv
COPY ./app/requirements.txt /app/
RUN pipenv lock --requirements
RUN pipenv lock --requirements > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app

