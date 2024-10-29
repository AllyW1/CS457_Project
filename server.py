import selectors
import socket
import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
        self.running = True

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.server_socket.setblocking(False)
        self.selector.register(self.server_socket, selectors.EVENT_READ)
        logging.info(f'Server started, listening on {self.host}:{self.port}')

    def accept_client(self):
        client_socket, addr = self.server_socket.accept()
        logging.info(f'Accepted connection from {addr}')
        client_socket.setblocking(False)
        self.selector.register(client_socket, selectors.EVENT_READ, data=addr)
        
        # Wait for the player to send their username
        self.send_message(client_socket, {'type': 'username_request', 'message': "Please enter a username:"})

    def broadcast(self, message, include_board=True, include_turn_prompt=False):
        for client, client_data in self.clients.items():
            final_message = message.copy()
            if include_board:
                final_message['board'] = self.get_board_string()
            if include_turn_prompt and client == self.get_current_player() and not self.game_over:
                final_message['message'] += " Your move."
            self.send_message(client, final_message)

    def send_message(self, client_socket, message):
        try:
            message_str = json.dumps(message) + '\n'  # Add newline delimiter
            client_socket.sendall(message_str.encode('utf-8'))
            logging.info(f"Sent message to client: {message}")
        except (ConnectionResetError, BrokenPipeError):
            self.disconnect_client(client_socket)

    def get_current_player(self):
        for client, data in self.clients.items():
            if data['symbol'] == self.player_symbols[self.turn_index]:
                return client

    def get_board_string(self):
        key_grid = [" 1 | 2 | 3 ", "---+---+---", " 4 | 5 | 6 ", "---+---+---", " 7 | 8 | 9 "]
        current_board = [" {} | {} | {} ".format(self.board[0], self.board[1], self.board[2]),
                         "---+---+---",
                         " {} | {} | {} ".format(self.board[3], self.board[4], self.board[5]),
                         "---+---+---",
                         " {} | {} | {} ".format(self.board[6], self.board[7], self.board[8])]
        combined_str = '\n'.join([f"{key_grid[i]}    {current_board[i]}" for i in range(len(key_grid))])
        return f"Position Key:  Current Board:\n{combined_str}"

    def check_winner(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != ' ':
                return self.board[a]
        if ' ' not in self.board:
            return 'draw'
        return None

    def handle_game_logic(self, key, mask):
        sock = key.fileobj
        data = sock.recv(1024).decode('utf-8')
        if not data:
            self.disconnect_client(sock)
            return
        
        try:
            message = json.loads(data)
            logging.info(f"Received message from client: {message}")
        except json.JSONDecodeError:
            self.send_message(sock, {'type': 'error', 'message': "Invalid message format."})
            return

        if self.game_over:
            self.send_message(sock, {'type': 'error', 'message': "The game is over. Please restart."})
            return

        # Handle username assignment
        if 'type' in message and message['type'] == 'username_response':
            self.assign_username(sock, message.get('username', ''))

        # Game logic (moves, quit, etc.)
        elif message['type'] == 'move':
            if sock != self.get_current_player():
                self.send_message(sock, {'type': 'error', 'message': "Wait for your turn."})
            else:
                pos = message.get('position')
                if 1 <= pos <= 9 and self.board[pos - 1] == ' ':
                    self.board[pos - 1] = self.player_symbols[self.turn_index]
                    self.broadcast({'type': 'move', 'message': f"{self.clients[sock]['username']} placed {self.player_symbols[self.turn_index]}."}, include_board=True)
                    
                    winner = self.check_winner()
                    if winner == 'draw':
                        self.broadcast({'type': 'end', 'message': "Game Over! It's a draw!"}, include_board=True)
                        self.game_over = True
                        self.end_game()
                    elif winner:
                        self.broadcast({'type': 'end', 'message': f"Game Over! {self.clients[sock]['username']} ({winner}) wins!"}, include_board=True)
                        self.game_over = True
                        self.end_game()
                    else:
                        self.turn_index = 1 - self.turn_index
                        self.broadcast({'type': 'turn', 'message': f"{self.clients[self.get_current_player()]['username']}'s turn."}, include_board=True, include_turn_prompt=True)
                else:
                    self.send_message(sock, {'type': 'error', 'message': "Invalid move or position taken, try again."})
                    self.broadcast({'type': 'turn', 'message': f"Invalid move or position taken. {self.clients[self.get_current_player()]['username']}'s turn."}, include_board=True)

        elif message['type'] == 'quit':
            self.broadcast({'type': 'end', 'message': f"{self.clients[sock]['username']} has quit the game."}, include_board=True)
            self.disconnect_client(sock)
            self.end_game()

    def assign_username(self, sock, username):
        if not username:
            username = f"Player {len(self.clients) + 1}"
        self.clients[sock] = {
            'username': username,
            'symbol': self.player_symbols[len(self.clients) % 2],
        }
        self.send_message(sock, {'type': 'response', 'message': f"Welcome {username}. You are {self.clients[sock]['symbol']}."})
        if len(self.clients) == 2:
            self.broadcast({
                'type': 'start',
                'message': f"Both players connected. {self.clients[self.get_current_player()]['username']}'s turn.",
                'board': self.get_board_string()
            }, include_turn_prompt=True)

    def disconnect_client(self, client_socket):
        if client_socket in self.clients:
            username = self.clients[client_socket]['username']
            logging.info(f"Disconnecting {username}")
            self.selector.unregister(client_socket)
            client_socket.close()
            del self.clients[client_socket]
            if len(self.clients) == 1:
                # Notify the remaining client
                remaining_client = next(iter(self.clients))
                self.send_message(remaining_client, {'type': 'disconnect_notice', 'message': f"{username} has left the game."})

    def end_game(self):
        for client in list(self.clients.keys()):
            self.send_message(client, {'type': 'end', 'message': "Game has ended. Disconnecting..."})
            self.disconnect_client(client)
        self.running = False

    def run(self):
        try:
            while self.running:
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
