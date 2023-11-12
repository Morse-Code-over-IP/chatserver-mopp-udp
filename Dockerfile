FROM python:3

WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt
ADD *.py /app/

ENTRYPOINT [ "python3", "./MOPP_Chat_server.py", "|", "tee", "/opt/log/logfile.txt" ]
