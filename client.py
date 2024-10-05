import argparse
import socket

class TicTacToeClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        self.socket.connect((self.server_ip, self.server_port))
        print(f'Connected to Tic-Tac-Toe server at {self.server_ip}:{self.server_port}')

    def send_move(self, move):
        try:
            print(f'Sending move to server: {move}')
            self.socket.send(move.encode('utf-8'))
            response = self.socket.recv(1024)
            print(f'Received from server: {response.decode("utf-8")}')
        except Exception as e:
            print(f'Error: {str(e)}')

    def close_connection(self):
        self.socket.close()
        print('Disconnected from server.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client for the Tic-Tac-Toe game.')
    parser.add_argument('host', type=str, help='Host IP address to connect to')
    parser.add_argument('port', type=int, help='Port number to connect on')
    args = parser.parse_args()

    client = TicTacToeClient(args.host, args.port)
    client.connect_to_server()
    while True:
        move = input("Enter your move (q to quit): ")
        if move.lower() == 'q':
            break
        client.send_move(move)
    client.close_connection()
