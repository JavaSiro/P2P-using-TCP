import os
import socket
import threading
import json

# Define the port number to listen on
PORT = 5000

# Define the buffer size for receiving files
BUFFER_SIZE = 1024

# Create a list to store connected clients
clients = []


def handle_client(client_socket):
    """
    Handle each client connection in a separate thread.
    """
    while True:
        try:
            # Receive the client's request
            request = client_socket.recv(BUFFER_SIZE).decode()
            if not request:
                # Client has disconnected
                break

            # Process the request based on its type
            if request == '1':
                # Option 1: Send and visualize a file
                send_file(client_socket)

            elif request == '2':
                # Option 2: Broadcast a file to multiple clients
                broadcast_file(client_socket)

        except ConnectionResetError:
            # Client has forcibly closed the connection
            break

    # Remove the client from the list
    clients.remove(client_socket)
    client_socket.close()


def send_file(client_socket):
    """
    Send a file to a client.
    """
    # Receive the file information from the client
    file_info = client_socket.recv(BUFFER_SIZE).decode()
    file_info = json.loads(file_info)

    # Extract the file type and content
    file_type = file_info['file_type']
    file_content = file_info['file_content']

    # Save the file on the server side
    file_name = f'received_file.{file_type}'
    with open(file_name, 'w') as file:
        file.write(file_content)

    # Send a confirmation message to the client
    response = 'File received successfully'
    client_socket.send(response.encode())


def broadcast_file(client_socket):
    """
    Broadcast a file to all connected clients.
    """
    # Receive the file information from the client
    file_info = client_socket.recv(BUFFER_SIZE).decode()
    file_info = json.loads(file_info)

    # Extract the file type and content
    file_type = file_info['file_type']
    file_content = file_info['file_content']

    # Iterate over all connected clients
    for client in clients:
        if client != client_socket:
            # Send the file to each client
            client.send(file_info.encode())

    # Send a confirmation message to the broadcasting client
    response = 'File broadcasted successfully'
    client_socket.send(response.encode())


def menu():
    """
    Display a menu to the client and process their choice.
    """
    while True:
        print("1. Send and visualize a file")
        print("2. Broadcast a file to multiple clients")
        print("3. Quit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            # Option 1: Send and visualize a file
            send_and_visualize_file()

        elif choice == '2':
            # Option 2: Broadcast a file to multiple clients
            broadcast_file_to_clients()

        elif choice == '3':
            # Option 3: Quit
            break

        else:
            print("Invalid choice. Please try again.")


def send_and_visualize_file():
    """
    Send a file to another client and visualize it.
    """
    file_path = input("Enter the path of the file: ")

    # Extract the file name and extension
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1][1:]

    # Read the file content
    with open(file_path, 'r') as file:
        file_content = file
        # Create a JSON object with file information
        file_info = {
            'file_name': file_name,
            'file_type': file_extension,
            'file_content': file_content
        }

        # Convert the JSON object to a string
        file_info_str = json.dumps(file_info)
        # Connect to the other client
        target_ip = input("Enter the IP address of the target client: ")
        target_port = input("Enter the port number of the target client: ")
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((target_ip, int(target_port)))

        # Send the file information to the target client
        target_socket.send(file_info_str.encode())

        # Receive a confirmation message from the target client
        response = target_socket.recv(BUFFER_SIZE).decode()
        print(response)

        # Close the connection to the target client
        target_socket.close()


def broadcast_file_to_clients():
    """
    Broadcast a file to multiple clients.
    """
    file_path = input("Enter the path of the file: ")

    # Extract the file name and extension
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1][1:]

    # Read the file content
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Create a JSON object with file information
    file_info = {
        'file_name': file_name,
        'file_type': file_extension,
        'file_content': file_content
    }

    # Convert the JSON object to a string
    file_info_str = json.dumps(file_info)

    # Iterate over all connected clients
    for client in clients:
        # Send the file information to each client
        client.send(file_info_str.encode())

        # Receive a confirmation message from the client
        response = client.recv(BUFFER_SIZE).decode()
        print(response)


# Start the P2P system
if __name__ == '__main__':
    # Create a server socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(5)

    print("P2P system started. Waiting for connections...")

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()

        # Add the client to the list of connected clients
        clients.append(client_socket)

        # Start a new thread to handle the client connection
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

    # Close the server socket
    server_socket.close()