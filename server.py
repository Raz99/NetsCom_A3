from socket import *

import client
from InputFileReader import *

if __name__ == "__main__":
    SERVER_ADDRESS = ('', 13000)
    # serverSocket = socket.socket()
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.bind(SERVER_ADDRESS)
    serverSocket.listen(1)
    print("The server is ready to receive client")
    while True:
        connectionSocket, addrClient = serverSocket.accept()
        sentence = connectionSocket.recv(4096).decode()
        print("Got from client ", addrClient, ":", sentence)

        maximum_msg_size = None

        if sentence == "asking the maximum size of of a single message":
            file_reader = InputFileReader("input.txt")  # Reads input file

            while maximum_msg_size is None:
                choice = input('Choose a number representing how you prefer to pass the value of the maximum message size (bytes)\n'
                               '([1] input from the user | [2] from a text input file): ')

                if int(choice) == 1:
                    maximum_msg_size = input("Enter the maximum message size: ")

                    if not maximum_msg_size.isnumeric():
                        raise ValueError("Maximum message size should be a number")

                elif int(choice) == 2:
                    maximum_msg_size = file_reader.get_value("maximum_msg_size")

                else:
                    print('Invalid input')

            connectionSocket.send(maximum_msg_size.encode())

        if maximum_msg_size is not None: # if maximum_msg_size has been already defined
            # Gets packages from Client
            full_message = ""
            received_sequences = []

            last_ack = -1
            received_out_of_order = []

            while True:
                # data = connectionSocket.recv(int(maximum_msg_size) + len(client.sequence_number)).decode('utf-8')
                data = connectionSocket.recv(int(maximum_msg_size) + 10).decode('utf-8')
                # data = connectionSocket.recv(4096).decode('utf-8')

                if not data:
                    print(f"The message is: \"{full_message}\"")
                    break

                # Decodes the sequence number and content
                sequence_number, content = data.split('|', 1)  # Separation represented by "|"
                sequence_number = int(sequence_number)  # Casting
                full_message = full_message + content
                print(f"Got from client {addrClient}: [M{sequence_number}] Content: {content}")

                # ACK
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
                #ack_message = f"ACK{last_ack}"
                # connectionSocket.send(ack_message.encode('utf-8'))
                # print(f"Sent to Client: {ack_message}")
                connectionSocket.send(str(last_ack).encode('utf-8'))
                print(f"Sent to Client: ACK{last_ack}")

        connectionSocket.close()