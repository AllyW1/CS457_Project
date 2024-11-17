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
        print(f"Connected to Tic-Tac-Toe server at {self.server_ip}:{self.server_port}")

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
                    message_str, buffer = buffer.split('\n', 1)
                    try:
                        message = json.loads(message_str)
                    except json.JSONDecodeError:
                        print("Failed to decode JSON:", message_str)
                        continue

                    if message['type'] == 'username_request':
                        self.send_username()
                        continue

                    print(message.get('message'))

                    if 'board' in message:
                        print(message['board'])

                    if "Your move." in message.get('message', ''):
                        self.send_move()

                    if message.get('type') == 'prompt_restart':
                        self.handle_game_over()
                        continue

                    if message.get('type') == 'end':
                        print("The game has ended. Disconnecting...")
                        return
        except (ConnectionResetError, BrokenPipeError):
            print("Connection to the server has been lost.")
        finally:
            self.close_connection()

    def send_username(self):
        if not self.username:
            self.username = input("Enter your username: ")
        message = {'type': 'username_response', 'username': self.username}
        self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))

    def send_move(self):
        while True:
            move = input("Enter your move (1-9, q to quit): ").strip()
            if move.lower() == 'q':
                message = {'type': 'quit'}
                self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
                print("You chose to quit. Disconnecting...")
                self.close_connection()
                return
            try:
                move = int(move)
                if 1 <= move <= 9:
                    message = {'type': 'move', 'position': move}
                    self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
                    break
                else:
                    print("Invalid input. Enter a number between 1 and 9.")
            except ValueError:
                print("Invalid input. Please enter a valid move.")

    def handle_game_over(self):
        print("Game over!")
        while True:
            decision = input("Would you like to play again? (y/n): ").strip().lower()
            if decision in ('y', 'n'):
                message = {'type': 'restart_decision', 'decision': decision}
                self.socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
                if decision == 'n':
                    print("You chose to quit. Disconnecting from the game...")
                    self.close_connection()
                    return
                else:
                    print("Waiting for the other player to decide...")
                    return
            else:
                print("Invalid input. Please type 'y' or 'n'.")

    def close_connection(self):
        self.socket.close()
        print('Disconnected from server.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for the Tic-Tac-Toe game.")
    parser.add_argument('-i', '--host', type=str, required=True, help="Host IP address or DNS to connect to.")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port number to connect on.")
    args = parser.parse_args()

    client = TicTacToeClient(args.host, args.port)
    client.connect_to_server()
    client.receive_messages()
