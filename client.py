import math
from socket import *
from InputFileReader import *

# Global variables
HEADER_SIZE = 4

def strip_ack(ack_message):
    index = ack_message.rfind("ACK") # Find the last occurrence of "ACK"
    return int(ack_message[index + 3:])

def send_message(client_socket, message, maximum_msg_size, window_size):
    message_bytes = message.encode('utf-8') # Converts to bytes
    message_size = len(message_bytes) # Size of the message in bytes
    num_of_messages = math.ceil(message_size / maximum_msg_size)
    i = 0  # Current message index

    # Sends the initial window of messages
    while i < num_of_messages and i < window_size:
        start = i * maximum_msg_size
        end = min(start + maximum_msg_size, message_size)
        content = message_bytes[start:end]
        sequence_number = f"{i}" # Adds sequence number
        while len(sequence_number) < HEADER_SIZE:
            sequence_number = " " + sequence_number
        sequence_number = sequence_number.encode('utf-8')
        package = sequence_number + content
        client_socket.send(package)  # Sends the package
        print(f"M{i} has been sent to server (status: {i + 1}/{num_of_messages}):")
        print(f"Content: \"{content.decode('utf-8')}\"")
        i += 1

    while True:
        ack_message = client_socket.recv(1024).decode('utf-8')  # Gets ACK when one is sent
        ack = strip_ack(ack_message)  # Separate ACKs
        print(f"ACK{ack} has been received")

        if i >= num_of_messages and i == ack + 1:
            break

        # Sends another package if ACK arrived
        start = i
        end = min(ack + 1 + window_size, num_of_messages)

        # Waits for the next ACK
        for j in range(start, end):
            start = j * maximum_msg_size
            end = min(start + maximum_msg_size, message_size)
            content = message_bytes[start:end]
            sequence_number = f"{j}"  # Adds sequence number
            while len(sequence_number) < HEADER_SIZE:
                sequence_number = " " + sequence_number
            sequence_number = sequence_number.encode('utf-8')
            package = sequence_number + content
            client_socket.send(package)  # Sends the package
            print(f"M{j} has been sent to server (status: {j + 1}/{num_of_messages}):")
            print(f"Content: \"{content.decode('utf-8')}\"")
            i+=1

def connect_to_server(host, port):
    server_addr = (host, port)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(server_addr)
    print(f"Connected to server at: {host} on port {port}")

    # Client sends a request to Server
    sentence = "Define the maximum size of a single message"
    client_socket.send(sentence.encode())
    print(f"Sent to Server: {sentence}")
    print("Waiting for server's response...")

    # Client gets a response from Server
    maximum_msg_size = int(client_socket.recv(4096).decode('utf-8'))
    print('From Server:', maximum_msg_size)

    file_reader = InputFileReader("input.txt")  # Reads input file

    message = None
    while message is None:
        choice = input('[Prompt] Choose a number representing how you prefer to pass the content of the message\n'
                       '[Prompt] ([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            message = input('[Prompt] Provide the message: ')

        elif int(choice) == 2:
            message = file_reader.get_value("message")

        else:
            print('[Prompt] Invalid input')

    window_size = None
    while window_size is None:
        choice = input('[Prompt] Choose a number representing how you prefer to pass the value of the window size\n'
                       '[Prompt] ([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            window_size = input('[Prompt] Provide the required window size: ')

            if not window_size.isnumeric():
                raise ValueError("Window size should be a number")

        elif int(choice) == 2:
            window_size = file_reader.get_value("window_size")

        else:
            print('[Prompt] Invalid input')

    window_size = int(window_size)
    send_message(client_socket, message, maximum_msg_size, window_size)

    # message.byte.size < clientSocket.recv(maximum_msg_size)

    # while(not all acks has been returned)
    #     clientSocket.send(sentence.encode()) # Sending message
    #     clientSocket.sendall()

    client_socket.close()

if __name__ == "__main__":
    server_host = "127.0.0.1"
    server_port = 9999

    connect_to_server(server_host, server_port)
