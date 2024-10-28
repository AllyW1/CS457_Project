import argparse
import socket
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TicTacToeClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None

    def connect_to_server(self):
        self.socket.connect((self.server_ip, self.server_port))
        logging.info(f'Connected to Tic-Tac-Toe server at {self.server_ip}:{self.server_port}')

    def receive_messages(self):
        try:
            buffer = ""
            while True:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    logging.info("Disconnected from server.")
                    break

                buffer += data
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    try:
                        message = json.loads(message_str)
                    except json.JSONDecodeError:
                        logging.error("Failed to decode JSON:", message_str)
                        continue

                    logging.info(f"Received message: {message}")

                    if message['type'] == 'username_request':
                        self.send_username()

                    if 'board' in message:
                        print(message['board'])

                    if "Your move." in message.get('message', ''):
                        self.send_move()

                    if "Game Over!" in message.get('message', ''):
                        break
        except (ConnectionResetError, BrokenPipeError):
            logging.error("Connection to the server has been lost.")
        finally:
            self.close_connection()

    def send_username(self):
        if not self.username:
            self.username = input("Enter your username: ")
        message = {'type': 'username_response', 'username': self.username}
        self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))

    def send_move(self):
        move = input("Enter your move (1-9, q to quit): ")
        if move.lower() == 'q':
            message = {'type': 'quit'}
            self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
        else:
            try:
                move = int(move)
                message = {'type': 'move', 'position': move}
                self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
            except ValueError:
                logging.error("Invalid input. Please enter a valid move.")
                self.send_move()

    def close_connection(self):
        self.socket.close()
        logging.info('Disconnected from server.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client for the Tic-Tac-Toe game.')
    parser.add_argument('host', type=str, help='Host IP address to connect to')
    parser.add_argument('port', type=int, help='Port number to connect on')
    args = parser.parse_args()

    client = TicTacToeClient(args.host, args.port)
    client.connect_to_server()
    client.receive_messages()

