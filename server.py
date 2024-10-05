import selectors
import socket
import argparse
import types

class TicTacToeServer:
    def __init__(self, host, port):
        self.selector = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.clients = {}  # Dictionary to store client socket info
        self.game_state = {}  # Stores game state, key as client addr

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.server_socket.setblocking(False)
        self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)
        print(f'Server started, listening on {self.host}:{self.port}')

    def accept_client(self):
        client_socket, addr = self.server_socket.accept()
        print(f'Accepted connection from {addr}')
        client_socket.setblocking(False)
        self.clients[addr] = client_socket
        self.selector.register(client_socket, selectors.EVENT_READ, data=addr)
        self.game_state[addr] = {'board': [' ']*9, 'turn': 'X'}

    def service_connection(self, key, mask):
        sock = key.fileobj
        addr = key.data
        if mask & selectors.EVENT_READ:
            data = sock.recv(1024)  # Buffer size
            if data:
                self.process_client_message(addr, data.decode('utf-8'))
            else:
                print(f'Closing connection to {addr}')
                self.selector.unregister(sock)
                sock.close()
                del self.clients[addr]
                del self.game_state[addr]

    def process_client_message(self, addr, message):
        print(f'Message from {addr}: {message}')
        response = f'ACK: {message}'  # Placeholder response
        self.clients[addr].send(response.encode('utf-8'))

    def run(self):
        try:
            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_client()
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Server is shutting down.")
        finally:
            self.selector.close()
            self.server_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a Tic-Tac-Toe server.')
    parser.add_argument('host', type=str, nargs='?', default='localhost', help='Host to bind the server to.')
    parser.add_argument('port', type=int, nargs='?', default=9999, help='Port to bind the server to.')
    args = parser.parse_args()

    server = TicTacToeServer(args.host, args.port)
    server.start_server()
    server.run()
