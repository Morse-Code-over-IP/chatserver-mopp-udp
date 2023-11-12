FROM python:3

WORKDIR /app
RUN mkdir logs
ADD *.py /app/

ENTRYPOINT [ "python3", "./MOPP_Chat_server.py" ]
