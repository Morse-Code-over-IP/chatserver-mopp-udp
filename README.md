# chatserver-mopp-udp
Simple chat server for [Morserino-32](https://github.com/oe1wkl/Morserino-32) using the 
[MOPP protocol](https://github.com/Morse-Code-over-IP/protocol-mopp) over UDP.


# Features
* Listens for UDP messages and rebroadcasts them to all other clients.
* empty keepalive UDP packets sent each 10 seconds to avoid NAT timeouts
  **Caution: UDP keepalive messages, while invisible, prevent your Morserino-32 from auto-shutdown!**
* number of clients is restricted (to avoid abuse)
* small delay is introduced (to avoid abuse)

# Starting the UDP server on port 7373
## Using Docker
+ You can start the server using `docker-compose up`, once you are logged into ghcr.io registry. 
+ This will also launch [frontail](https://github.com/mthenw/frontail) on port 8001.
## Using Python
+ You can start the server usin `python3 MOPP_Chat_server.py`.

# How to use it?
To "connect" or "make yourself known" to the server, send "hi" message from your Morserino with 20 WPM. Server will respond with ":hi" with number of clients connected (1 means you're alone). After that, server will resend all messages from you to all other known clients (you excluded).

If client is inactive (not transmitting) for too long, it will be dropped from the list. This is indicated by ":bye" message sent from the server. To reconnect, send "hi" again.

You can also force disconnection by sending ":bye".

## Modifications (SIGBIT)
There are some additional server commands, such as activating / deactivating echo mode for testing purposes by sending :EM (---... . --). The server will respond by sending you the current state, either ON (--- -.) or OFF (--- ..-. ..-.). Usually the sending user is excluded from receiving his / her own transmissions. In echo mode, own transmissions are sent back to the sending user as well. This is not suitable for actual communication, but may be helpfull for testing / debugging purposes. Please note that this is a server setting which affects all users.

When sending the command :USR (---... ..- ... .-.), the server will report the number of currently active users.

# References
- Original [m32-chat-server](https://github.com/sp9wpn/m32_chat_server) by Wojtek, SP9WPN
- ReImplementation [SigBit](https://github.com/tuxintrouble/sigbit) by Sebastian Stetter, DJ5SE