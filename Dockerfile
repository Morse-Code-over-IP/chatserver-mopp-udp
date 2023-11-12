FROM python:3

WORKDIR /app
ADD *.py /app/

ENTRYPOINT [ "python3", "./MOPP_Chat_server.py" ]
