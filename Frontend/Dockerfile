FROM python:3.9

WORKDIR /usr/app/src
COPY . ./

RUN pip install -r requirements.txt
RUN bash -c "mv /usr/app/src/.env-docker /usr/app/src/.env"
