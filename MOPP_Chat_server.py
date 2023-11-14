#!/usr/local/bin/python3
#
# This file is part of the sigbit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
# 
# Implements a chat server for the MOPP - morse over packet protocol
# on PC
# uses code fragments from https://github.com/sp9wpn/m32_chat_server

import socket
import time
import struct
from math import ceil
from mopp import encode, decode, zfill, ljust, ditlen
from datetime import datetime
import sys

SERVER_IP = "0.0.0.0"
UDP_PORT = 7373
CLIENT_TIMEOUT = 60*5 #seconds
MAX_CLIENTS = 10
KEEPALIVE = 10
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
    sys.stdout.flush() # TODO: uses logging

    if LOG:
      logfile = open("logs/logfile.txt","a")
      logfile.write((datetime.now().strftime("%d-%m-%Y, %H:%M:%S -") + s+"\n"))
      logfile.close()
      
def encode_buffer(buffer,wpm):

  global protocol_version
  global serial
  '''creates an bytes for sending throught a socket'''

  #prevent overflow in wpm - we have only 6 bits in MOPP
  if wpm > 63:
      wpm = 63

  #create 14 bit header
  m = zfill(bin(protocol_version)[2:],2) #2bits for protocol_version
  m += zfill(bin(serial)[2:],6) #6bits for serial number
  m += zfill(bin(wpm)[2:],6) #6bits for words per minute

  #add payload
  for el in buffer:
    m += el
    
  m = ljust(m,int(8*ceil(len(m)/8.0)),'0') #fill in incomplete byte
  res = ''

  for i in range(0, len(m),8):
    res += chr(int(m[i:i+8],2)) #convert 8bit chunks to integers and the to characters

  #prevent overflow - we have only 6 bits MOPP
  if serial < 62:
    serial +=1
  else:
    serial = 0
    
  return res.encode('utf-8') #convert string of characters to bytes


def decode_header(unicodestring):
  '''converts a received morse code byte string and returns a list
  with the header info [protocol_v, serial, wpm]''' 
  #bytestring = unicodestring.decode("utf-8")
  bytestring = unicodestring.decode("utf-8", errors='ignore')
  bitstring = ''
  
  for byte in bytestring:
    bitstring += zfill(bin(ord(byte))[2:],8) #works in uPython
  debug(bitstring)#check content
  m_protocol = int(bitstring[:2],2)
  m_serial = int(bitstring[3:8],2)
  m_wpm = int(bitstring[9:14],2)
		
  return [m_protocol, m_serial, m_wpm]


def decode_payload(unicodestring):
  '''converts a received morse code byte string to text'''
  bytestring = unicodestring.decode("utf-8", errors='ignore')
  bitstring = ''
	
  for byte in bytestring:
    #convert byte to 8bits
    bitstring += zfill(bin(ord(byte))[2:],8) #works in uPython

  m_payload = bitstring[14:] #we just need the payload here

  buffer = []
  for i in range(0, len(m_payload),2):
    el = m_payload[i]+m_payload[i+1]
    buffer.append(el)

  while buffer[-1] == "00": #remove surplus '00' elements
    buffer.pop()

  return buffer


def broadcast(data,client):
  global ECHO
  for c in receivers.keys():
    if c == client and not ECHO:
     continue
    debug("Sending to %s" % c)
    ip,port = c.split(':')
    serversock.sendto(data, (ip, int(port)))

def welcome(client, speed):
  ip,port = client.split(':')
  serversock.sendto(encode_buffer(encode('welcome'),speed), addr)
  receivers[client] = time.time()
  time.sleep(2)
  serversock.sendto(encode_buffer(encode('qrv'),speed), addr)
  time.sleep(ditlen(speed)*7)
  serversock.sendto(encode_buffer(encode('%i' %len(receivers)),speed), addr)
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
    
    if client in receivers and data != b'':
      speed = decode_header(data)[2]
      if decode_payload(data) == encode(':qrt'):
        serversock.sendto(encode_buffer(encode('bye'),speed), addr)
        del receivers[client]
        debug ("Removing client %s on request" % client)

      elif decode_payload(data) == encode(':em'):
        if ECHO:
          ECHO = False
          serversock.sendto(encode_buffer(encode('off'),speed), addr)
        else:
          ECHO = True
          serversock.sendto(encode_buffer(encode('on'),speed), addr)

      elif decode_payload(data) == encode(':usr'):
        serversock.sendto(encode_buffer(encode('%i users'%len(receivers)),speed), addr)
      
      else:
        broadcast (data, client)
        receivers[client] = time.time()
    elif data != b'':
      speed = decode_header(data)[2]
      if decode_payload(data) == encode('hi'):
        if (len(receivers) < MAX_CLIENTS):
          receivers[client] = time.time()
          if decode_payload(data) == encode('hi'):
          	welcome(client, speed)
        else:
          reject(client, speed)
          debug ("ERR: maximum clients reached- %s" %client)

      else:
        pass
        #debug ("-unknown client, ignoring- %s" %client)

      
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
