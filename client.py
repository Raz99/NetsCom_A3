import math
import time
from socket import *
from InputFileReader import *

# Global variables
HEADER_SIZE = 4
INPUT_FILE_PATH = "input.txt"

def strip_ack(ack_message):
    """
    Extracts the acknowledgment number from the ACK message.

    Args:
        ack_message (str): The acknowledgment message received from the server.

    Returns:
        int: The acknowledgment number extracted from the message.
    """
    index = ack_message.rfind("ACK") # Finds the last occurrence of "ACK"
    return int(ack_message[index + 3:]) # Cuts the word "ACK" and returns the number only

def send_message(client_socket, message, maximum_msg_size, window_size, time_out):
    """
    Sends a message to the server using a sliding window protocol.

    Args:
        client_socket (socket): The socket object for the client.
        message (str): The message to be sent to the server.
        maximum_msg_size (int): The maximum size of a single message segment.
        window_size (int): The size of the sliding window.
        time_out (int): The timeout duration for waiting for ACKs (relevant for the oldest unacknowledged message).
    """
    message_bytes = message.encode('utf-8') # Converts to bytes
    message_size = len(message_bytes) # Size of the message in bytes
    num_of_messages = math.ceil(message_size / maximum_msg_size) # Checks the number of messages after splitting the data

    # Sliding window
    lar = -1 # Last ack
    lss = 0 # Current message
    sent_time = time.time() # Timer start

    while lar < num_of_messages - 1:
        # Checks for ACKs
        try:
            client_socket.settimeout(0.1)
            ack_message = client_socket.recv(4096).decode('utf-8')

            if ack_message:
                ack_number = strip_ack(ack_message)
                print(f"Got from Server: ACK{ack_number}")
                if ack_number > lar:
                    lar = ack_number
                    sent_time = None # Resets timer

        except timeout:
            pass

        current_time = time.time()
        # Timeout exceeded
        if sent_time is not None and current_time - sent_time > time_out:
            print(f"Timeout exceeded for M{lar+1}. Resending all un-ACKed messages...")
            for i in range(lar + 1, lss):
                print(f"[M{i}] Resending message...")
                start = i * maximum_msg_size
                end = min(start + maximum_msg_size, message_size)
                content = message_bytes[start:end]
                sequence_number = f"{i}"  # Adds sequence number
                while len(sequence_number) < HEADER_SIZE:
                    sequence_number = " " + sequence_number
                sequence_number = sequence_number.encode('utf-8')
                package = sequence_number + content
                client_socket.send(package)  # Sends the package
                print(f"Resent to Server: [M{i}] Content: \"{content.decode('utf-8')}\"")
                if lar + 1 == i:
                    sent_time = time.time() # Starts a new timer

                    # Checks for ACKs
                    try:
                        client_socket.settimeout(0.1)
                        ack_message = client_socket.recv(4096).decode('utf-8')

                        if ack_message:
                            ack_number = strip_ack(ack_message)
                            print(f"Got from Server: ACK{ack_number}")
                            if ack_number > lar:
                                lar = ack_number
                                sent_time = None  # Resets timer

                    except timeout:
                        pass

        if lss < num_of_messages and lss - lar <= window_size:
            start = lss * maximum_msg_size
            end = min(start + maximum_msg_size, message_size)
            content = message_bytes[start:end] # Cuts the content according to the maximum message size
            sequence_number = f"{lss}" # Adds the sequence number
            while len(sequence_number) < HEADER_SIZE: # Extends according to header size
                sequence_number = " " + sequence_number
            sequence_number = sequence_number.encode('utf-8')
            package = sequence_number + content # Combine the sequence number with the content
            client_socket.send(package)  # Sends the package
            print(f"Sent to Server: [M{lss}] Content: \"{content.decode('utf-8')}\" (status: {lss + 1}/{num_of_messages})")
            print(f"[Prompt] Window status: {lss - lar}/{window_size} occupied slots")
            if lar + 1 == lss:
                sent_time = time.time() # Starts a new timer
            lss += 1


def connect_to_server(host, port):
    """
    Connects to the server and initiates the message sending process for getting the required definitions.

    Args:
        host (str): The server's hostname.
        port (int): The port number on which the server is listening to.
    """
    server_addr = (host, port)
    client_socket = socket(AF_INET, SOCK_STREAM) # Creates socket
    client_socket.connect(server_addr) # Connects to server
    print(f"Connected to server at: {host} on port {port}")

    # Client sends a request to Server
    sentence = "Define the maximum size of a single message"
    client_socket.send(sentence.encode()) # Sends request
    print(f"Sent to Server: {sentence}")
    print("Waiting for server's response...")

    # Client gets a response from Server
    maximum_msg_size = int(client_socket.recv(4096).decode('utf-8'))
    print(f"Got from Server: {maximum_msg_size}")

    file_reader = InputFileReader(INPUT_FILE_PATH)  # Reads input file

    message = None
    while message is None:
        choice = input('[Prompt] Choose a number representing how you prefer to pass the content of the message\n'
                       '[Prompt] ([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            message = input('[Prompt] Provide the message: ')

        elif int(choice) == 2:
            message = file_reader.get_value("message") # Gets the message from the file

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
            window_size = file_reader.get_value("window_size") # Gets the window size from the file

        else:
            print('[Prompt] Invalid input')

    window_size = int(window_size)
    print(f"[Prompt] Window size: {window_size}")

    timeout = None
    while timeout is None:
        choice = input('[Prompt] Choose a number representing how you prefer to pass the value of the timeout\n'
                       '[Prompt] ([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            timeout = input('[Prompt] Provide the required timeout: ')

            if not timeout.isnumeric():
                raise ValueError("The timeout should be a number")

        elif int(choice) == 2:
            timeout = file_reader.get_value("timeout") # Gets the window size from the file

        else:
            print('[Prompt] Invalid input')

    print(f"[Prompt] Timeout: {timeout}")
    timeout = int(timeout) # Casting

    send_message(client_socket, message, maximum_msg_size, window_size, timeout)

    print("Connection closed")
    client_socket.close() # Close connection

if __name__ == "__main__":
    server_name = '127.0.0.1'
    server_port = 8080

    connect_to_server(server_name, server_port)