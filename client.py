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

    # Sends the initial window of messages
    i = 0  # Current message index
    ack = -1 # No ACKs has been received yet
    limit = window_size
    while i < num_of_messages or i < ack + 1:
        if i < window_size or i < limit:
            start = i * maximum_msg_size
            end = min(start + maximum_msg_size, message_size)
            content = message_bytes[start:end]
            sequence_number = f"{i}" # Adds sequence number
            while len(sequence_number) < HEADER_SIZE:
                sequence_number = " " + sequence_number
            sequence_number = sequence_number.encode('utf-8')
            package = sequence_number + content
            client_socket.send(package)  # Sends the package
            print(f"Sent to Server: [M{i}] Content: \"{content.decode('utf-8')}\" (status: {i + 1}/{num_of_messages}):")
            i += 1

        print(f"[Prompt] Window status: {limit - i}/{window_size} available slots")
        ack_message = client_socket.recv(4096).decode('utf-8')

        if not ack_message:
            continue

        prev_ack = ack
        ack = strip_ack(ack_message)
        print(f"Got from Server: ACK{ack}")
        limit += ack - prev_ack # Slides window

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
    print(f"Got from Server: {maximum_msg_size}")

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

    print(f"[Prompt] Message: {message}")

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

    print(f"[Prompt] Window size: {window_size}")
    window_size = int(window_size)
    send_message(client_socket, message, maximum_msg_size, window_size)

    print("Connection closed")
    client_socket.close()

if __name__ == "__main__":
    server_name = 'localhost'
    server_port = 13000

    connect_to_server(server_name, server_port)
