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
    lss = 0
    lar = -1
    start_time = None  # Timer for oldest unacknowledged message
    unacked_messages = {}  # Store unacknowledged messages

    # While there are still messages to send
    # or all the messages have been already sent, but not all the ACKs have been received
    while lss < num_of_messages or lar < num_of_messages - 1:
        if lss-lar <= window_size and lss not in list(unacked_messages.keys()): # Means there is an available spot in the window
            start = lss * maximum_msg_size
            end = min(start + maximum_msg_size, message_size)
            content = message_bytes[start:end]
            sequence_number = f"{lss}" # Adds sequence number
            while len(sequence_number) < HEADER_SIZE:
                sequence_number = " " + sequence_number
            sequence_number = sequence_number.encode('utf-8')
            package = sequence_number + content
            client_socket.send(package)  # Sends the package
            # if lar + 1 == lss:
            #     start_time = time.time()
            # Store message and start timer if it's the first unacknowledged message
            unacked_messages[lss] = {'seq': sequence_number, 'package': package}
            if start_time is None:
                start_time = time.time()
            print(f"Sent to Server: [M{lss}] Content: \"{content.decode('utf-8')}\" (status: {lss + 1}/{num_of_messages})")
            print(f"[Prompt] Window status: {lss - lar}/{window_size} occupied slots")
            lss += 1

        if start_time and (time.time() - start_time) > time_out:
            print(f"[Prompt] M{lar+1} has not received ACK yet and timeout was exceeded, sending un-ACKed messages again...")
            # lss = lar + 1
            # Resend all unacknowledged messages
            for seq in sorted(unacked_messages.keys()):
                client_socket.send(unacked_messages[seq]['package'])
                print(f"Resent to Server: [M{seq}]")
            start_time = None # Reset timer
            continue

        try:
            client_socket.settimeout(0.1)  # Short timeout for checking ACKs
            ack_message = client_socket.recv(4096).decode('utf-8')

            if not ack_message:
                continue # Keep sending packages if there are available spots in window size

            last_ack = strip_ack(ack_message)
            print(f"Got from Server: ACK{last_ack}")
            # lar = last_ack
            # start_time = None

            # Remove acknowledged messages
            for seq in list(unacked_messages.keys()):
                if seq < num_of_messages and seq <= lar:
                    del unacked_messages[seq]

            lar = last_ack

            # Reset timer for next unacknowledged message if any
            if unacked_messages:
                start_time = time.time()
            else:
                start_time = None

        except timeout:
            continue  # No ACK received, continue checking

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

    print(f"[Prompt] Window size: {int(window_size)}")
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
    timeout = float(timeout)

    send_message(client_socket, message, maximum_msg_size, window_size, timeout)

    print("Connection closed")
    client_socket.close()

if __name__ == "__main__":
    server_name = "127.0.0.1"
    server_port = 8080

    connect_to_server(server_name, server_port)
