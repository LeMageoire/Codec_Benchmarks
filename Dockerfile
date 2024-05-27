FROM python:3.9-slim 

WORKDIR /app

COPY requirements.txt .
COPY python/setup.py ./python/setup.py

RUN python3 python/setup.py 



