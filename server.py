#import socket
from socket import *

SERVER_ADDRESS = ('', 13000)
# serverSocket = socket.socket()
serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(SERVER_ADDRESS)
serverSocket.listen(1)
print("The server is ready to receive client")
while True:
    connectionSocket, addrClient = serverSocket.accept()
    sentence = connectionSocket.recv(4096).decode()
    print("Get from client ", addrClient, ":", sentence)

    if sentence == "asking the maximum size of of a single message":
        choice = input('Choose a number representing how you prefer to pass the value of the maximum message size\n'
                       '([1] input from the user | [2] from a text input file): ')

        maximum_msg_size = "0"  # Re-write this

        if int(choice) == 1:
            maximum_msg_size = input("Enter the maximum message size: ")

        elif int(choice) == 2:
            # Write here
            maximum_msg_size = "1000"  # Re-write this

        else:
            print('Invalid input')

        connectionSocket.send(bytes(maximum_msg_size.encode()))

    # connectionSocket.send(capitalizedSentence).encode()
    connectionSocket.close()