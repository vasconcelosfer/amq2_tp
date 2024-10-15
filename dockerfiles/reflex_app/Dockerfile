FROM python:3.12


ENV REDIS_URL=redis://redis PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


#ENTRYPOINT ["reflex", "run", "--env", "prod", "--backend-only", "--loglevel", "debug" ]
ENTRYPOINT ["reflex", "run", "--loglevel", "debug" ]