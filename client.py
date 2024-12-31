import math
import struct
from socket import *
from InputFileReader import *

def send_message(socket, message, maximum_msg_size, window_size):
    message_bytes = message.encode('utf-8') # convert to bytes
    message_size = len(message_bytes) # the size of bytes
    num_of_messages = math.ceil(message_size / maximum_msg_size)
    flag = False
    i = 0
    if not flag:
        while i < num_of_messages or i < window_size:
            

    for i in range(num_of_messages):
        start = i * maximum_msg_size
        end = start + maximum_msg_size
        content = message_bytes[start:end]

        # Separation represented by "|"
        sequence_number = f"{i}|".encode('utf-8')
        package = sequence_number + content

        socket.send(package)
        print(f"M{i} has been sent to server (status: {i+1}/{num_of_messages})")
        ack = socket.recv(1)

if __name__ == "__main__":
    # SERVER_ADDRESS = ('localhost', 13000)
    serverName = 'localhost'
    serverPort = 13000
    SERVER_ADDRESS = (serverName, serverPort)

    # clientSocket = socket.socket()
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(SERVER_ADDRESS)

    # Client sends a request to Server
    print("The client is asking the server for maximum size of a single message")
    sentence = "asking the maximum size of of a single message"
    clientSocket.send(sentence.encode())

    # Client gets a response from Server
    maximum_msg_size = clientSocket.recv(4096)
    print('From Server:', maximum_msg_size.decode())

    file_reader = InputFileReader("input.txt") # Reads input file

    message = None
    while message is None:
        choice = input('Choose a number representing how you prefer to pass the content of the message\n'
                       '([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            message = input('Provide the message: ')

        elif int(choice) == 2:
            message = file_reader.get_value("message")

        else:
            print('Invalid input')

    window_size = None
    while window_size is None:
        choice = input('Choose a number representing how you prefer to pass the value of the window size\n'
                       '([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            window_size = input('Provide the required window size:')

        elif int(choice) == 2:
            window_size = file_reader.get_value("window_size")

        else:
            print('Invalid input')



    send_message(clientSocket, message, int(maximum_msg_size), window_size)

    # message.byte.size < clientSocket.recv(maximum_msg_size)


    # while(not all acks has been returned)
    #     clientSocket.send(sentence.encode()) # Sending message
    #     clientSocket.sendall()

    clientSocket.close()
