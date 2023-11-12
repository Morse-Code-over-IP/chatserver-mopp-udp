FROM python:3

RUN mkdir /opt/log
WORKDIR /app
ADD *.py /app/

#ENTRYPOINT [ "python3", "./MOPP_Chat_server.py", "|", "tee", "/opt/log/logfile.txt" ]
ENTRYPOINT [ "/bin/sh", "-c", "/usr/local/bin/python3 ./MOPP_Chat_server.py |/usr/bin/tee /opt/log/logfile.txt" ]
