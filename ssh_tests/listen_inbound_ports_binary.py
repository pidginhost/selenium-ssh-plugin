
PYTHON_BINARY = """
import socket
import threading

def handle_client(client_socket, port):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        client_socket.send(f'Received: {data}')
    client_socket.close()

def server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f'Server listening on port {port}...')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f'Connection from {client_address[0]}:{client_address[1]} on port {port}')

        client_handler = threading.Thread(target=handle_client, args=(client_socket, port))
        client_handler.start()

# List of ports you want to listen on
ports = [443, 80, 1000]

# Start a server for each port
for p in ports:
    threading.Thread(target=server, args=(p,)).start()

print('Servers are up and running!')
"""