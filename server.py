from socket import *
from InputFileReader import *


# def receive_message(client_connection, buffer_size):
#     data = client_connection.recv(buffer_size)
#     if not data:
#         return None, None
#     separate_index = data.index(b'|')
#     sequence_number = int(data[:separate_index].decode('utf-8'))
#     content = data[separate_index + 1:].decode('utf-8')
#     return sequence_number, content

def split_data(data, maximum_msg_size, remaining_messages):
    while data.find(b'|') != -1:  # Runs as long as there are separators in data
        separator_index = data.index(b'|')
        sequence_number = data[:separator_index].decode('utf-8')
        end_pos = min(separator_index + 1 + maximum_msg_size, len(data))
        content = data[separator_index + 1: end_pos].decode('utf-8')
        remaining_messages.append((sequence_number, content))
        data = data[end_pos:]


def handle_client(server_addr):
    # server_socket = socket.socket()
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Reuse Address - Allows the socket to reuse the address
    # [?] - Buffer Size - Sets the send/receive buffer sizes
    server_socket.bind(server_addr)
    server_socket.listen(1)
    keep_handling = True

    while keep_handling:
        print("Waiting for connection...")
        client_connection, client_addr = server_socket.accept()
        print(f"Accepted connection from {client_addr}")
        sentence = client_connection.recv(4096).decode('utf-8')
        print(f"Got from client {client_addr}: {sentence}")

        maximum_msg_size = None
        if sentence == "Define the maximum size of a single message":
            while maximum_msg_size is None:
                choice = input(
                    '[Prompt] Choose a number representing how you prefer to pass the value of the maximum message size (bytes)\n'
                    '[Prompt] ([1] input from the user | [2] from a text input file): ')

                if int(choice) == 1:
                    maximum_msg_size = input("[Prompt] Enter the maximum message size: ")

                    if not maximum_msg_size.isnumeric():
                        raise ValueError("Maximum message size should be a number")

                elif int(choice) == 2:
                    file_reader = InputFileReader("input.txt")  # Reads input file
                    maximum_msg_size = file_reader.get_value("maximum_msg_size")

                else:
                    print('[Prompt] Invalid input')

            client_connection.send(maximum_msg_size.encode('utf-8'))

        if maximum_msg_size is not None:  # if maximum_msg_size has been already defined
            # Gets packages from Client
            full_message = ""
            received_sequences = {}

            last_ack = -1
            received_out_of_order = []
            remaining_messages = []

            while True:
                # data = connectionSocket.recv(int(maximum_msg_size) + len(client.sequence_number)).decode('utf-8')
                # data = connectionSocket.recv(int(maximum_msg_size) + 10).decode('utf-8')

                # Temp - start
                data = client_connection.recv(4096)

                if not data:
                    print(f"The message is: \"{full_message}\"")
                    keep_handling = False  # Server will stop handling clients altogether
                    break

                split_data(data, int(maximum_msg_size), remaining_messages)

                for (sequence_number, content) in remaining_messages:
                    full_message = full_message + content
                    print(f"Got from client {client_addr}: [M{sequence_number}] Content: \"{content}\"")
                remaining_messages = []
                # Temp - end

                # sequence_number, content = receive_message(client_connection, maximum_msg_size)

                # if not content:
                #     print(f"Combining the messages provides the data: \"{full_message}\"")
                #     keep_handling = False # Server will stop handling clients altogether
                #     break

                # Decodes the sequence number and content
                # sequence_number = int(sequence_number)  # Casting
                # full_message = full_message + content
                # print(f"Got from client {client_addr}: [M{sequence_number}] Content: \"{content}\"")

                # ACK
                # If the current message is in sequence, then update last_ack
                # if sequence_number == (last_ack + 1):
                #     last_ack += 1
                #
                #     # Checks if received messages out of order are now in sequence
                #     while (last_ack + 1) in received_out_of_order:
                #         last_ack += 1
                #         received_out_of_order.remove(last_ack)
                #
                # else:
                #     # If the current message is not in sequence, then add it to received_out_of_order
                #     received_out_of_order.append(sequence_number)
                #
                # # Sends ACK to Client
                # # ack_message = f"ACK{last_ack}"
                # # client_connection.send(ack_message.encode('utf-8'))
                # # print(f"Sent to Client: {ack_message}")
                #
                # client_connection.send(str(last_ack).encode('utf-8'))
                # print(f"Sent to Client: ACK{last_ack}")

            print("Client disconnected")
            client_connection.close()

        print("Server will stop handling clients altogether")
        server_socket.close()


if __name__ == "__main__":
    server_name = ''
    server_port = 13000

    handle_client((server_name, server_port))
