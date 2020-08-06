import socket
import sys

from SocketPlayer import SocketPlayer

########
verbose = False
player = SocketPlayer()
########

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 41869)
print('Starting up server on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    if SocketPlayer.verbose:
        print('Waiting for a connection')
    connection, client_address = sock.accept()

    try:
        if SocketPlayer.verbose:
            print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            dataBytes = connection.recv(1600)
            dataStr = dataBytes.decode("ascii")
            if verbose:
                print('Received "%s"' % dataStr)
            if dataStr:
                res = player.interpretSocketOutput(dataStr)
                connection.sendall(res)
            else:
                if SocketPlayer.verbose:
                    print('No more data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
