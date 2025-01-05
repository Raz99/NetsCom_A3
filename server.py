# import random # Edge case (3)
from socket import *
from InputFileReader import *
from client import HEADER_SIZE, INPUT_FILE_PATH

def split_data(data, maximum_msg_size, remaining_messages):
    """
    Splits the received data into messages based on the header size and maximum message size.

    Args:
        data (bytes): The data received from the client.
        maximum_msg_size (int): The maximum size of a single message.
        remaining_messages (list): A list to store the split messages.

    Returns:
        None
    """
    while data:
        sequence_number = int(data[:HEADER_SIZE].decode('utf-8').strip())
        end_pos = min(HEADER_SIZE + maximum_msg_size, len(data))
        content = data[HEADER_SIZE: end_pos].decode('utf-8')
        remaining_messages.append((sequence_number, content))
        data = data[end_pos:]


def handle_client(server_addr):
    """
    Handles client connection, receives messages and sends acknowledgments.

    Args:
        server_addr (tuple): The server address (IP, port).

    Returns:
        None
    """
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Reuse Address - Allows the socket to reuse the address
    server_socket.bind(server_addr)
    server_socket.listen(1)
    keep_handling = True

    while keep_handling:
        print("Waiting for connection...")
        client_connection, client_addr = server_socket.accept()
        print(f"Accepted connection from {client_addr}")
        sentence = client_connection.recv(4096).decode('utf-8')
        while not sentence:  # Edge case of not getting any sentence
            sentence = client_connection.recv(4096).decode('utf-8')
        print(f"Got from Client {client_addr}: {sentence}")

        maximum_msg_size = None
        if sentence == "Define the maximum size of a single message":
            while maximum_msg_size is None:
                choice = input('[Prompt] Choose a number representing how you prefer to pass the value of the maximum message size (bytes)\n'
                               '[Prompt] ([1] input from the user | [2] from a text input file): ')

                if int(choice) == 1:
                    maximum_msg_size = input("[Prompt] Enter the maximum message size: ")

                    if not maximum_msg_size.isnumeric():
                        raise ValueError("Maximum message size should be a number")

                elif int(choice) == 2:
                    file_reader = InputFileReader(INPUT_FILE_PATH)  # Reads input file
                    maximum_msg_size = file_reader.get_value("maximum_msg_size")

                else:
                    print('[Prompt] Invalid input')

            print(f"Sent to Client: Maximum message size is {int(maximum_msg_size)}")
            print("Waiting for client's response...")
            client_connection.send(maximum_msg_size.encode('utf-8'))
            maximum_msg_size = int(maximum_msg_size)

        # If maximum_msg_size has been already defined
        if maximum_msg_size:
            # Gets packages from Client
            last_ack = -1
            received_out_of_order = []
            remaining_messages = []
            received_messages = {}

            while True:
                # Edge case (3) - start
                # Simulate random packet loss (10% chance)
                # if random.random() < 0.2:
                #     # Skip sending ACK on purpose
                #     _ = client_connection.recv(4096)
                #     continue
                # # Edge case (3) - end
                data = client_connection.recv(4096)

                if not data:
                    full_message = ""
                    for seq in sorted(received_messages.keys()):
                        full_message += received_messages[seq]['content']
                    print(f"[Prompt] The message is: \"{full_message}\"")
                    keep_handling = False  # Server will stop handling clients altogether
                    break

                split_data(data, maximum_msg_size, remaining_messages)

                for (sequence_number, content) in remaining_messages:
                    # # Edge case (2) - start
                    # if sequence_number == 2:
                    #     continue
                    # # Edge case (2) - end
                    received_messages[sequence_number] = {'seq': sequence_number, 'content': content}
                    print(f"Got from Client {client_addr}: [M{sequence_number}] Content: \"{content}\"")

                    # ACK handling
                    # If the current message is in sequence, then update last_ack
                    if sequence_number == (last_ack + 1):
                        last_ack += 1

                        # Checks if received messages out of order are now in sequence
                        while (last_ack + 1) in received_out_of_order:
                            last_ack += 1
                            received_out_of_order.remove(last_ack)

                    else:
                        # If the current message is not in sequence, then add it to received_out_of_order
                        received_out_of_order.append(sequence_number)

                    # Sends ACK to Client
                    if last_ack != -1:
                        ack_message = f"ACK{last_ack}"
                        client_connection.send(ack_message.encode('utf-8'))
                        print(f"Sent to Client: {ack_message}")

                remaining_messages.clear()

            print("Client disconnected")
            client_connection.close()

        print("Server will stop handling clients altogether")
        server_socket.close()


if __name__ == "__main__":
    server_name = '127.0.0.1'
    server_port = 8080

    handle_client((server_name, server_port))