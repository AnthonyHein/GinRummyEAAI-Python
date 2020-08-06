import socket
import sys

from SocketPlayer import SocketPlayer

player = SocketPlayer()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('Starting up server on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection')
    connection, client_address = sock.accept()

    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            dataBytes = connection.recv(1600)
            dataStr = dataBytes.decode("ascii")
            print('Received "%s"' % dataStr)
            if dataStr:
                res = player.interpretSocketOutput(dataStr)
                connection.sendall(res)
            else:
                print('No more data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
