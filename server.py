import selectors
import socket
import json
import argparse

class TicTacToeServer:
    def __init__(self, host, port):
        self.selector = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.clients = {}
        self.board = [' '] * 9
        self.player_symbols = ['X', 'O']
        self.turn_index = 0
        self.game_over = False
        self.running = True  # Flag to indicate whether the server is still running

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.server_socket.setblocking(False)
        self.selector.register(self.server_socket, selectors.EVENT_READ)
        print(f'Server started, listening on {self.host}:{self.port}')

    def accept_client(self):
        client_socket, addr = self.server_socket.accept()
        print(f'Accepted connection from {addr}')
        client_socket.setblocking(False)
        self.selector.register(client_socket, selectors.EVENT_READ, data=addr)
        self.clients[client_socket] = {
            'addr': addr,
            'symbol': self.player_symbols[len(self.clients) % 2],
            'ready': False
        }
        if len(self.clients) == 1:
            self.send_message(client_socket, {'type': 'response', 'message': 'Welcome Player X. Waiting for Player O...'})
        elif len(self.clients) == 2:
            self.broadcast({
                'type': 'response',
                'message': 'Both players connected. Game starts now. Player X\'s turn.',
                'board': self.get_board_string()
            }, include_turn_prompt=True)

    def broadcast(self, message, include_board=True, include_turn_prompt=False):
        for client, client_data in self.clients.items():
            final_message = message.copy()
            if include_board:
                final_message['board'] = self.get_board_string()  # Ensure both boards are shown
            if include_turn_prompt and client == self.get_current_player() and not self.game_over:
                final_message['message'] += " Your move."
            self.send_message(client, final_message)

    def send_message(self, client_socket, message):
        message_str = json.dumps(message)
        client_socket.sendall(message_str.encode('utf-8'))

    def get_current_player(self):
        for client, data in self.clients.items():
            if data['symbol'] == self.player_symbols[self.turn_index]:
                return client

    def get_board_string(self):
        # This returns both the key grid and the current board
        key_grid = "Position Key:\n1 | 2 | 3\n---+---+---\n4 | 5 | 6\n---+---+---\n7 | 8 | 9\n"
        board_str = "\nCurrent board:\n" + "\n---+---+---\n".join([" | ".join(self.board[i:i+3]) for i in range(0, 9, 3)])
        return key_grid + board_str

    def check_winner(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # Horizontal
                          (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Vertical
                          (0, 4, 8), (2, 4, 6)]  # Diagonal
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != ' ':
                return self.board[a]  # Return the winner (X or O)
        if ' ' not in self.board:
            return 'draw'
        return None

    def handle_game_logic(self, key, mask):
        sock = key.fileobj
        data = sock.recv(1024).decode('utf-8')
        if not data:
            self.disconnect_client(sock)  # Handle disconnect
            return
        
        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            sock.sendall("Invalid message format.".encode('utf-8'))
            return

        if self.game_over:
            sock.sendall("The game is over. Please restart the server for a new game.".encode('utf-8'))
            return

        message_type = message.get('type')
        if message_type == 'move':
            if sock != self.get_current_player():
                self.send_message(sock, {'type': 'response', 'message': "Wait for your turn."})
            elif message.get('position') is not None and 1 <= message['position'] <= 9:
                pos = message['position'] - 1
                if self.board[pos] == ' ':
                    self.board[pos] = self.player_symbols[self.turn_index]
                    winner = self.check_winner()
                    if winner == 'draw':
                        self.broadcast({'type': 'response', 'message': "Game Over! The game is a draw!"})
                        self.game_over = True
                        self.end_game()
                    elif winner:
                        self.broadcast({'type': 'response', 'message': f"Game Over! Player {winner} wins!"})
                        self.game_over = True
                        self.end_game()
                    else:
                        self.turn_index = 1 - self.turn_index
                        self.broadcast({'type': 'response', 'message': f"Player {self.player_symbols[self.turn_index]}'s turn."}, include_turn_prompt=True)
                else:
                    self.send_message(sock, {'type': 'response', 'message': "Position already taken, try again."})
            else:
                self.send_message(sock, {'type': 'response', 'message': "Invalid move, please enter a number between 1-9."})

        elif message_type == 'quit':
            self.broadcast({'type': 'response', 'message': "Player has quit the game. Disconnecting..."})
            self.disconnect_client(sock)
            self.end_game()

    def disconnect_client(self, client_socket):
        print(f"Disconnecting client {client_socket}")
        self.selector.unregister(client_socket)
        client_socket.close()
        if client_socket in self.clients:
            del self.clients[client_socket]

    def end_game(self):
        """End the game by disconnecting all remaining clients and stopping the server loop."""
        for client in list(self.clients.keys()):
            self.send_message(client, {'type': 'response', 'message': "The game has ended. Disconnecting..."})
            self.disconnect_client(client)
        self.game_over = True
        self.running = False  # Set the running flag to False to stop the server

    def run(self):
        try:
            while self.running:  # Use running flag to control the server loop
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.fileobj == self.server_socket:
                        self.accept_client()
                    else:
                        self.handle_game_logic(key, mask)
        finally:
            self.cleanup_all_connections()

    def cleanup_all_connections(self):
        for client in list(self.clients.keys()):
            self.disconnect_client(client)
        self.server_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a Tic-Tac-Toe server.')
    parser.add_argument('host', type=str, help='Host to bind the server to.')
    parser.add_argument('port', type=int, help='Port to bind the server to.')
    args = parser.parse_args()

    server = TicTacToeServer(args.host, args.port)
    server.start_server()
    server.run()
