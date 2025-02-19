FROM alpine:latest

WORKDIR /
COPY . /

RUN apk update
RUN apk add python3 py3-pip
RUN pip install -r requirements.txt --break-system-packages

EXPOSE 8000
CMD ["sh", "start.sh"]



