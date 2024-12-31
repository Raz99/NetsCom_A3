# import socket
from socket import *
from turtledemo.penrose import start

# SERVER_ADDRESS = ('localhost', 13000)
serverName = 'localhost'
serverPort = 13000
SERVER_ADDRESS = (serverName, serverPort)

# clientSocket = socket.socket()
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(SERVER_ADDRESS)

def send_message(socket, message, maximum_msg_size):
    message_bytes = message.encode('utf-8') # convert to bytes
    message_size = len(message_bytes) # the size of bytes
    num_of_messages = int((message_size / maximum_msg_size) + 1)
    for i in range(num_of_messages):
        start = i * maximum_msg_size
        end = start + maximum_msg_size
        package = message_bytes[start:end]
        socket.sendall(package) # check if send or sendall











if __name__ == "__main__":
    # Client sends a request to Server
    print("The client is asking the server for maximum size of of a single message")
    sentence = "asking the maximum size of of a single message"
    clientSocket.send(sentence.encode())

    # Client gets a response from Server
    maximum_msg_size = clientSocket.recv(4096)
    print('From Server:', maximum_msg_size.decode())

    choice = input('Choose a number representing how you prefer to pass the content of the message\n'
                           '([1] input from the user | [2] from a text input file): ')

    if int(choice) == 1:
        message = input('Provide the message: ')

    elif int(choice) == 2:
        str = InputFileReader.get_value("message")
        # Re-write this - take the message field from the file
        pass

    send_message(clientSocket, message, maximum_msg_size)

    # message.byte.size < clientSocket.recv(maximum_msg_size)


    # while(not all acks has been returned)
    #     clientSocket.send(sentence.encode()) # Sending message
    #     clientSocket.sendall()

    clientSocket.close()
