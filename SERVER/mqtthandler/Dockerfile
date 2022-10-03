FROM alpine:latest

RUN apk update
RUN apk add py-pip
RUN apk add --no-cache python3-dev
RUN pip install --upgrade pip

WORKDIR /app
COPY . /app
RUN pip --no-cache-dir install flask flask_restful pymongo paho-mqtt flask_mqtt requests 

ENV COSMICSWAMP_IP="http://35.177.218.103"
ENV CRSPY_PORT="4116"
ENV ORION_PORT="1026"
ENV IOTAGENT_PORT="3456"
ENV MONGO_PORT=""

CMD ["source", "setup.sh"]
CMD ["python3", "app.py"]

EXPOSE 4243
