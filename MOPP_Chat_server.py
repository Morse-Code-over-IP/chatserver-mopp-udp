#!/usr/bin/env python3
#
# This file was originally part of the sigbit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
# 
# Implements a chat server for the MOPP - morse over packet protocol
# and uses additional code fragments from https://github.com/sp9wpn/m32_chat_server

import socket
import time
import struct
from math import ceil
from mopp import encode, decode, zfill, ljust, ditlen
from datetime import datetime
import sys
import os

SERVER_IP = os.environ.get('SERVER_IP', "0.0.0.0")
UDP_PORT = int(os.environ.get('UDP_PORT', "7373"))
CLIENT_TIMEOUT = int(os.environ.get('CLIENT_TIMEOUT', "300")) # seconds
MAX_CLIENTS = int(os.environ.get('MAX_CLIENTS', "10"))
KEEPALIVE = int(os.environ.get('KEEPALIVE', "10"))
DEBUG = 1
LOG = 1 # write logs to logs/logfile.txt
ECHO = False

serversock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serversock.bind((SERVER_IP, UDP_PORT))
serversock.settimeout(KEEPALIVE)

receivers = {}
last_time_heartbeat=time.time()
protocol_version = 1
serial = 1


def debug(s):
  if DEBUG:
    print(datetime.now().strftime("%d-%m-%Y, %H:%M:%S -") + s)
    sys.stdout.flush() # TODO: use logging

    if LOG:
      logfile = open("logs/logfile.txt","a")
      logfile.write((datetime.now().strftime("%d-%m-%Y, %H:%M:%S -") + s+"\n"))
      logfile.close()

def encode_mopp(protocol_version, serial, wpm, payload):
  '''converts a received mopp structure and return bytestring to be sent to mopp'''
  data_arr1 = []
  data_str2 = ''
  data_arr3 = bytearray()

  if wpm > 63:
      wpm = 63

  data_arr1.append(zfill(bin(protocol_version)[2:],2)) #2bits for protocol_version
  data_arr1.append(zfill(bin(serial)[2:],6)) #6bits for serial number
  data_arr1.append(zfill(bin(wpm)[2:],6)) #6bits for wpm
  data_arr1 += encode(payload) # add complete endoded payload (dihs dahs)

  data_str2 = ''.join(data_arr1)

  l = len(data_str2)%8
  if l:
    for x in range(0, (8-l)):
      data_str2 += "0"

  for byte in [int(data_str2[i:i+8],2) for i in range(0, len(data_str2), 8)]:
    data_arr3.append(byte)

  return data_arr3
 
def decode_mopp(data):
  '''converts a received udp data to mopp structure and return complete list of the data'''
  bits = ''
  b_payload = []
  for byte in data:
    bits += zfill(bin(byte)[2:],8)
  m_protocol = int(bits[:2],2)
  m_serial = int(bits[3:8],2)
  m_wpm = int(bits[9:14],2)
  m_payload = bits[14:]

  for i in range(0, len(m_payload),2):
    el = m_payload[i]+m_payload[i+1]
    b_payload.append(el)

  while b_payload[-1] == "00": #remove surplus '00' elements
    b_payload.pop()

  if b_payload[-1] != "11": #for some reason morserino is not always sending EOW
    b_payload.append("11")

  return m_protocol, m_serial, m_wpm, decode(b_payload)

def broadcast(data, client):
  global ECHO
  for c in receivers.keys():
    if c == client and not ECHO:
     continue
    debug("Sending to %s" % c)
    ip,port = c.split(':')
    serversock.sendto(data, (ip, int(port)))

def welcome(client, speed):
  ip,port = client.split(':')
  serversock.sendto(encode_mopp(protocol_version, serial, speed, 'welcome '), addr)
  serversock.sendto(encode_mopp(protocol_version, serial, speed, 'ur '), addr)
  serversock.sendto(encode_mopp(protocol_version, serial, speed, 'wpm '), addr)
  serversock.sendto(encode_mopp(protocol_version, serial, speed, str(speed)), addr)
  receivers[client] = time.time()
  time.sleep(2)
  serversock.sendto(encode_mopp(protocol_version, serial, speed, 'qrv'), addr)
  time.sleep(ditlen(speed)*7)
  serversock.sendto(encode_mopp(protocol_version, serial, speed, 'no users'), addr)
  debug("New client: %s" % client)

def reject(client, speed):
  ip,port = client.split(':')
  serversock.sendto(encode_buffer(encode(':qrl'),speed), addr)


while KeyboardInterrupt:
  time.sleep(0.2)						# anti flood
  try:
    data, addr = serversock.recvfrom(64)
    client = addr[0] + ':' + str(addr[1])
    
    if client in receivers and data == b'': #just a heartbeat signal from the client
      receivers[client] = time.time()
      debug("heartbeat detected from %s " % client)
      continue

    if data != b'':
      proto, serial, speed, payload = decode_mopp(data)
      print(proto, speed, serial, payload)
      if client in receivers:
        if payload == ':qrt ':
          serversock.sendto(encode_mopp(protocol_version, serial, speed, 'bye'), addr)
          del receivers[client]
          debug ("Removing client %s on request" % client)

        elif payload == ':em ':
          if ECHO:
            ECHO = False
            serversock.sendto(encode_mopp(protocol_version, serial, speed, 'off'), addr)
          else:
            ECHO = True
            serversock.sendto(encode_mopp(protocol_version, serial, speed, 'on'), addr)

        elif payload == ':usr ':
          serversock.sendto(encode_mopp(protocol_version, serial, speed, 'no users'), addr)
      
        else:
          broadcast (data, client)
          receivers[client] = time.time()
      else:
        if payload == 'hi ':
          if (len(receivers) < MAX_CLIENTS):
            receivers[client] = time.time()
            if payload == 'hi ':
            	welcome(client, speed)
          else:
            reject(client, speed)
            debug ("ERR: maximum clients reached- %s" %client)

    #send keepalives if not sent the last 10 secs
    for c in receivers.keys():
      if last_time_heartbeat + 10 < time.time():
        ip,port = c.split(':')
        serversock.sendto(b'', (ip,int(port)))
        last_time_heartbeat=time.time()

  except socket.timeout:
    # Send UDP keepalives
    # Explanation: we are always trying to receive packets. If nothing is sent, the connection will timeout.
    # This timeout triggers the sending of empty hearbeat packets to all clients. If the clients respond, their session gets updated.
    for c in receivers.keys():
      ip,port = c.split(':')
      serversock.sendto(b'', (ip,int(port)))
      last_time_heartbeat=time.time()

  except (KeyboardInterrupt, SystemExit):
    serversock.close()
    break

  # clean clients list
  for c in receivers.copy().items():
    if c[1] + CLIENT_TIMEOUT < time.time():
      del receivers[c[0]]
      debug ("Removing expired client %s" % c[0])
