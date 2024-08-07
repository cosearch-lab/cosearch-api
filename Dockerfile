FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY ./prestart.sh /app/

COPY ./app /app/app