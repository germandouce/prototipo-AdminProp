FROM python:3.9

WORKDIR /usr/app
COPY . .
COPY .env-docker .env

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "app.py"]