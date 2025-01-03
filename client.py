import math
import time
from socket import *
from InputFileReader import *

# Global variables
HEADER_SIZE = 4

def strip_ack(ack_message):
    index = ack_message.rfind("ACK") # Finds the last occurrence of "ACK"
    return int(ack_message[index + 3:])

def send_message(client_socket, message, maximum_msg_size, window_size, time_out):
    message_bytes = message.encode('utf-8') # Converts to bytes
    message_size = len(message_bytes) # Size of the message in bytes
    num_of_messages = math.ceil(message_size / maximum_msg_size)

    # Sends the initial window of messages
    lar = -1
    lss = 0
    start_time = {}

    while lar < num_of_messages - 1:
        while lss < num_of_messages and lss - lar <= window_size:
            start = lss * maximum_msg_size
            end = min(start + maximum_msg_size, message_size)
            content = message_bytes[start:end]
            sequence_number = f"{lss}" # Adds sequence number
            while len(sequence_number) < HEADER_SIZE:
                sequence_number = " " + sequence_number
            sequence_number = sequence_number.encode('utf-8')
            package = sequence_number + content
            client_socket.send(package)  # Sends the package
            start_time[lss] = time.time()
            print(f"Sent to Server: [M{lss}] Content: \"{content.decode('utf-8')}\" (status: {lss + 1}/{num_of_messages}):")
            print(f"[Prompt] Window status: {lss - lar}/{window_size} occupied slots")
            lss += 1

        flag = True
        ack_message = ""
        while flag:
            flag = False
            ack_message = client_socket.recv(4096).decode('utf-8')
            if ack_message:
                last_ack = strip_ack(ack_message)
                if last_ack > lar:
                    lar = last_ack
                    print(f"Got from Server: ACK{last_ack}")
                    flag = True

        current_time = time.time()
        for i in range(lar + 1, lss):
            if current_time - start_time.get(i, 0) > time_out:
                print(f"Timeout exceeded for M{i}. Resending...")
                start = i * maximum_msg_size
                end = min(start + maximum_msg_size, message_size)
                content = message_bytes[start:end]
                sequence_number = f"{lss}"  # Adds sequence number
                while len(sequence_number) < HEADER_SIZE:
                    sequence_number = " " + sequence_number
                sequence_number = sequence_number.encode('utf-8')
                package = sequence_number + content
                client_socket.send(package)  # Sends the package
                start_time[i] = time.time()
                print(f"Resent to Server: [M{i}] Content: \"{content.decode('utf-8')}\"")


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

    timeout = None
    while timeout is None:
        choice = input('[Prompt] Choose a number representing how you prefer to pass the value of the timeout\n'
                       '[Prompt] ([1] input from the user | [2] from a text input file): ')

        if int(choice) == 1:
            timeout = input('[Prompt] Provide the required timeout: ')

            if not timeout.isnumeric():
                raise ValueError("The timeout should be a number")

        elif int(choice) == 2:
            timeout = file_reader.get_value("timeout")

        else:
            print('[Prompt] Invalid input')

    print(f"[Prompt] Timeout: {timeout}")
    timeout = int(timeout)

    send_message(client_socket, message, maximum_msg_size, window_size, timeout)

    print("Connection closed")
    client_socket.close()

if __name__ == "__main__":
    server_name = '127.0.0.1'
    server_port = 9999

    connect_to_server(server_name, server_port)
