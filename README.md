# chatserver-mopp-udp
Simple chat server for [Morserino-32](https://github.com/oe1wkl/Morserino-32)


This server script listens for UDP messages and rebroadcasts them to all other clients.

# Features
* empty keepalive UDP packets sent each 10 seconds to avoid NAT timeouts
  **Caution: UDP keepalive messages, while invisible, prevent your Morserino-32 from auto-shutdown!**
* number of clients is restricted (to avoid abuse)
* small delay is introduced (to avoid abuse)

# Starting the UDP server on port 7373
## Docker
+ `docker-compose up`
+ Will also launch frontail on port 8001
## Locally 
+ `python3 MOPP_Chat_server.py`

# How to use it?
To "connect" or "make yourself known" to the server, send "hi" message from your Morserino with 20 WPM. Server will respond with ":hi" with number of clients connected (1 means you're alone). After that, server will resend all messages from you to all other known clients (you excluded).

If client is inactive (not transmitting) for too long, it will be dropped from the list. This is indicated by ":bye" message sent from the server. To reconnect, send "hi" again.

You can also force disconnection by sending ":bye".



# References
- m32-chat-server by https://github.com/sp9wpn/m32_chat_server
- sigbit by https://github.com/tuxintrouble/sigbit