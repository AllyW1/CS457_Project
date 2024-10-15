import argparse
import socket
import json

class TicTacToeClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        self.socket.connect((self.server_ip, self.server_port))
        print(f'Connected to Tic-Tac-Toe server at {self.server_ip}:{self.server_port}')

    def receive_messages(self):
        try:
            while True:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    print("Disconnected from server.")
                    break
                message = json.loads(data)
                print(message.get('message'))  # Print the message from the server
                if 'board' in message:
                    print(message['board'])  # Print the board if it's included
                if "Your move." in message.get('message', '') or "try again." in message.get('message', ''):
                    self.send_move()
                if "Game Over!" in message.get('message', ''):
                    print(message.get('message'))  # Display the game over message (win or draw)
                    break  # End the loop if the game is over
                if "The game has ended." in message.get('message', ''):
                    break  # Disconnect if the game ends or a player quits
        finally:
            self.close_connection()

    def send_move(self):
        move = input("Enter your move (1-9, q to quit): ")
        if move.lower() == 'q':
            message = {'type': 'quit'}
            self.socket.sendall(json.dumps(message).encode('utf-8'))
            print("You have quit the game.")
            return
        else:
            try:
                move = int(move)
                message = {'type': 'move', 'position': move}
            except ValueError:
                print("Invalid input. Please enter a number.")
                self.send_move()  # Retry sending the move
                return
        self.socket.sendall(json.dumps(message).encode('utf-8'))

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
