import argparse
import socket
import json

class TicTacToeClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None

    def connect_to_server(self):
        self.socket.connect((self.server_ip, self.server_port))
        print(f'Connected to Tic-Tac-Toe server at {self.server_ip}:{self.server_port}')

    def receive_messages(self):
        try:
            buffer = ""
            while True:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    print("Disconnected from server.")
                    break

                buffer += data
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)  # Split by newline
                    try:
                        message = json.loads(message_str)
                    except json.JSONDecodeError:
                        print("Failed to decode JSON:", message_str)
                        continue

                    print(message.get('message'))

                    if message['type'] == 'username_request':
                        self.send_username()

                    if 'board' in message:
                        print(message['board'])

                    if "Your move." in message.get('message', ''):
                        self.send_move()

                    if "Game Over!" in message.get('message', ''):
                        break

                    if message['type'] == 'disconnect_notice':
                        print("The other player has disconnected.")
                        self.handle_disconnect_option()
                        return  # End the loop after handling disconnect option
        except (ConnectionResetError, BrokenPipeError):
            print("Connection to the server has been lost.")
        finally:
            self.close_connection()

    def send_username(self):
        if not self.username:
            self.username = input("Enter your username: ")
        message = {'type': 'username_response', 'username': self.username}
        self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))  # Add newline delimiter

    def send_move(self):
        move = input("Enter your move (1-9, q to quit): ")
        if move.lower() == 'q':
            message = {'type': 'quit'}
            self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))  # Add newline delimiter
        else:
            try:
                move = int(move)
                message = {'type': 'move', 'position': move}
                self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))  # Add newline delimiter
            except ValueError:
                print("Invalid input. Please enter a valid move.")
                self.send_move()

    def handle_disconnect_option(self):
        while True:
            choice = input("The other player has left the game. Do you want to quit? (Type 'q' to quit): ")
            if choice.lower() == 'q':
                print("You have chosen to quit the game.")
                self.close_connection()
                break
            else:
                print("Invalid input. Type 'q' to quit.")

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
    client.receive_messages()
