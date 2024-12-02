import selectors
import socket
import json
import argparse
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TicTacToeServer:
    def __init__(self, port, timeout=90):
        #Initialize the server with a given port and timeout.
        self.selector = selectors.DefaultSelector()
        self.host = '0.0.0.0'
        self.port = port
        self.clients = {}
        self.board = [' '] * 9
        self.player_symbols = ['X', 'O']
        self.turn_index = 0
        self.game_over = False
        self.last_activity = time.time()
        self.timeout = timeout

    def start_server(self):
        #Start the server and bind it to the specified port.
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.server_socket.setblocking(False)
            self.selector.register(self.server_socket, selectors.EVENT_READ)
            logging.info(f"Server started on {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Error starting server: {e}")
            exit(1)

    def accept_client(self):
        #Accept a new client connection.
        try:
            client_socket, addr = self.server_socket.accept()
            logging.info(f"Accepted connection from {addr}")
            client_socket.setblocking(False)
            self.selector.register(client_socket, selectors.EVENT_READ, data=addr)

            if len(self.clients) == 0:
                self.reset_game()

            if client_socket not in self.clients:
                self.clients[client_socket] = {'username': None, 'restart_decision': None}
                self.send_message(client_socket, {'type': 'username_request', 'message': "Please enter a username:"})
            self.update_last_activity()
        except Exception as e:
            logging.error(f"Error accepting client: {e}")

    def send_message(self, client_socket, message):
        #Send a JSON-formatted message to a client.
        try:
            message_str = json.dumps(message) + '\n'
            client_socket.sendall(message_str.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            logging.info(f"Failed to send message to client. Disconnecting client.")
            self.disconnect_client(client_socket)
        except Exception as e:
            logging.error(f"Error sending message: {e}")

    def broadcast(self, message, include_board=True, include_turn_prompt=False):
        #Send a message to all connected clients.
        for client, data in self.clients.items():
            final_message = message.copy()
            if include_board:
                final_message['board'] = self.get_board_string()
            if include_turn_prompt and client == self.get_current_player() and not self.game_over:
                final_message['message'] += " Your move."
            self.send_message(client, final_message)

    def get_current_player(self):
        #Get the current player's client socket.
        return next((client for client, data in self.clients.items() if 'symbol' in data and data['symbol'] == self.player_symbols[self.turn_index]), None)

    def get_board_string(self):
        #Generate a formatted string representation of the board.
        key_grid = [" 1 | 2 | 3 ", "---+---+---", " 4 | 5 | 6 ", "---+---+---", " 7 | 8 | 9 "]
        current_board = [
            " {} | {} | {} ".format(self.board[0], self.board[1], self.board[2]),
            "---+---+---",
            " {} | {} | {} ".format(self.board[3], self.board[4], self.board[5]),
            "---+---+---",
            " {} | {} | {} ".format(self.board[6], self.board[7], self.board[8])
        ]
        combined_str = '\n'.join([f"{key_grid[i]}    {current_board[i]}" for i in range(len(key_grid))])
        return f"Position Key:  Current Board:\n{combined_str}"

    def check_winner(self):
        #Check if there is a winner or if the game is a draw.
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != ' ':
                return self.board[a]
        return 'draw' if ' ' not in self.board else None

    def handle_game_logic(self, key, mask):
        #Handle game-related messages from clients.
        sock = key.fileobj
        try:
            data = sock.recv(1024).decode('utf-8')
            if not data:
                self.disconnect_client(sock)
                return
        except ConnectionResetError:
            self.disconnect_client(sock)
            return
        except Exception as e:
            logging.error(f"Unexpected error during message handling: {e}")
            self.send_message(sock, {'type': 'error', 'message': "Unexpected error occurred."})
            return

        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            self.send_message(sock, {'type': 'error', 'message': "Invalid message format."})
            return

        if message.get('type') == 'username_response':
            self.assign_username(sock, message.get('username', ''))

        elif message.get('type') == 'move':
            if sock != self.get_current_player():
                self.send_message(sock, {'type': 'error', 'message': "Wait for your turn."})
            else:
                pos = message.get('position')
                if 1 <= pos <= 9 and self.board[pos - 1] == ' ':
                    self.board[pos - 1] = self.player_symbols[self.turn_index]
                    winner = self.check_winner()
                    if winner:
                        self.game_over = True
                        winning_player = next((data['username'] for client, data in self.clients.items() if data.get('symbol') == winner), None)
                        self.broadcast({'type': 'end', 'message': f"Game over! {winning_player} wins!"}, include_board=True)
                        self.prompt_restart()
                    else:
                        self.turn_index = 1 - self.turn_index
                        self.broadcast({'type': 'turn', 'message': "Next player's turn."}, include_board=True, include_turn_prompt=True)
                else:
                    self.send_message(sock, {'type': 'error', 'message': "Invalid move. Try again."})
                    self.send_message(sock, {'type': 'turn', 'message': "Your move.", 'board': self.get_board_string()})

        elif message.get('type') == 'restart_decision':
            self.handle_restart_decision(sock, message.get('decision'))

        elif message.get('type') == 'quit':
            username = self.clients[sock]['username']
            self.broadcast({'type': 'end', 'message': f"The game has ended because {username} has quit."})
            self.disconnect_client(sock)
            self.end_game()

    def handle_restart_decision(self, sock, decision):
        #Handle restart decisions from clients.
        self.clients[sock]['restart_decision'] = decision
        remaining_decisions = [data.get('restart_decision') for data in self.clients.values()]

        if None not in remaining_decisions:
            if 'n' in remaining_decisions:
                self.broadcast({'type': 'end', 'message': "The game has ended because a player chose to quit."})
                self.end_game()
            elif all(d == 'y' for d in remaining_decisions):
                self.reset_game()
                self.broadcast({'type': 'start', 'message': "Both players agreed to restart the game!"}, include_board=True, include_turn_prompt=True)

    def prompt_restart(self):
        #Prompt all clients to decide whether to restart or quit.
        for client in self.clients:
            self.send_message(client, {'type': 'prompt_restart', 'message': "Would you like to play again? (y/n)"})

    def reset_game(self):
        #Reset the game state for a new game.
        self.board = [' '] * 9
        self.turn_index = 0
        self.game_over = False
        for client in self.clients.values():
            client.pop('restart_decision', None)

    def assign_username(self, sock, username):
        #Assign a username to a client.
        self.clients[sock]['username'] = username
        self.clients[sock]['symbol'] = self.player_symbols[len(self.clients) - 1]
        self.send_message(sock, {'type': 'response', 'message': f"Welcome {username}. You are {self.clients[sock]['symbol']}."})
        if len(self.clients) == 2:
            self.broadcast({'type': 'start', 'message': "Game starts now!"}, include_board=True, include_turn_prompt=True)

    def disconnect_client(self, sock):
        #Disconnect a client from the server.
        if sock in self.clients:
            del self.clients[sock]
        try:
            self.selector.unregister(sock)
        except KeyError:
            logging.info("Socket already unregistered.")
        try:
            sock.close()
        except OSError:
            logging.info("Socket already closed.")
        logging.info(f"Client disconnected.")

    def update_last_activity(self):
        #Update the last activity timestamp.
        self.last_activity = time.time()

    def check_timeout(self):
        #Check if the server has been inactive for too long.
        if time.time() - self.last_activity > self.timeout:
            logging.info("Server inactive for too long. Shutting down.")
            self.shutdown()

    def shutdown(self):
        #Shutdown the server and disconnect all clients.
        logging.info("Shutting down server.")
        for client in list(self.clients.keys()):
            self.disconnect_client(client)
        self.selector.unregister(self.server_socket)
        self.server_socket.close()
        exit(0)

    def end_game(self):
        #End the game and shutdown the server.
        logging.info("Ending the game and shutting down the server.")
        for client in list(self.clients.keys()):
            self.send_message(client, {'type': 'end', 'message': "The game has ended."})
            self.disconnect_client(client)
        self.selector.unregister(self.server_socket)
        self.server_socket.close()
        exit(0)

    def run(self):
        #Run the server to accept and handle client connections.
        while True:
            self.check_timeout()
            events = self.selector.select(timeout=1)
            for key, mask in events:
                if key.fileobj == self.server_socket:
                    self.accept_client()
                else:
                    self.handle_game_logic(key, mask)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Tic-Tac-Toe server.")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port to bind the server to.")
    args = parser.parse_args()

    server = TicTacToeServer(args.port)
    server.start_server()
    server.run()
