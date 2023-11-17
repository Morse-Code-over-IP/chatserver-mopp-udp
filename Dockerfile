FROM python:3

WORKDIR /app
RUN mkdir logs
ADD requirements.txt .
RUN pip3 install -r requirements.txt
ADD *.py /app/

ENV SERVER_IP "0.0.0.0"
ENV UDP_PORT "7373"
ENV CLIENT_TIMEOUT "300" 
ENV MAX_CLIENTS "10"
ENV KEEPALIVE "10"

ENTRYPOINT [ "python3", "./MOPP_Chat_server.py" ]