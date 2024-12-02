Creator: Allison Whittern

# Tic-Tac-Toe Game

![image](https://github.com/user-attachments/assets/543d15a8-89b7-49b1-b6c6-8a08649d4519)

This is a simple Tic-Tac-Toe game implemented using Python and sockets. Made for CS457 at CSU.

**How to play:**
1. **Start the server:** Run the `server.py` script.
   - terminal: python3 server.py -p [port]
   - Ex: python3 server.py -p 9000
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
   - terminal: python3 client.py -i [hostname] -p [port]
   - python3 client.py -i antlion.cs.colostate.edu -p 9000
   - ENSURE client and server are looking at the same port. In the example that is localhost 9000
   - Game won't start until two clients are connected to the server.
     ![image](https://github.com/user-attachments/assets/7c6c898b-5975-43e8-9d37-d1442c65311d)

3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!
   - Players are allowed to set a username if they choose not to then they will be default assigned numbers/symbols: Player 1(X) and Player 2(O).
   - Players take turns entering their moves. The move is entered as a number (1-9), corresponding to the position on the Tic-Tac-Toe grid.
   - The first player to get three in a row (horizontally, vertically, or diagonally) wins!
   - The game will also end if all nine spaces are filled and no player has won, resulting in a draw.
   - You will look at the position key. Choose the number of the position you are choosing. Then wait till it is your turn again. 

4. **End of Game:**
   - When a player wins, the game will announce "Game Over! Player (username or X/O) wins!"
   - If the game results in a draw, it will announce "Game Over! The game is a draw!"
   - Game will force quit, Server and Client Connections will be cleaned up. (If you want to play again just start up the server and clients again)

**Game Message Protocol Specification:**
- Message Types:
   - Join: Sent when a client joins the server.
json
{ "type": "username_response", "username": "player_name" }
   - Move: Sent when a player makes a move by selecting a position on the board.
json
{ "type": "move", "position": 5 }
   - Quit: Sent when a player quits the game.
json
{ "type": "quit" }
   - Response: Sent from the server to clients with updated game information.
json
{
  "type": "response",
  "message": "Player X's turn."
}
   - Turn: Sent to notify clients whose turn it is to play.
json
{
  "type": "turn",
  "message": "player_name's turn. Your move.",
  "board": "Position Key:    Current Board:\n 1 | 2 | 3      X |   |  \n---+---+---    ---+---+---\n 4 | 5 | 6      O | X |  \n---+---+---    ---+---+---\n 7 | 8 | 9      X | O |  "
   - Move Acknowledgement: Sent from the server when a move has been made successfully, showing the updated board state.
json
{
  "type": "move",
  "message": "player_name placed X at position 5.",
  "board": "Position Key:    Current Board:\n 1 | 2 | 3      X |   |  \n---+---+---    ---+---+---\n 4 | 5 | 6      O | X |  \n---+---+---    ---+---+---\n 7 | 8 | 9      X | O |  "
}
   - End: Sends the result of the game after a win condition.
json
{
  "type": "end",
  "message": "Game Over! player_name (X) wins!",
  "board": "Position Key:    Current Board:\n 1 | 2 | 3      X | O | X \n---+---+---    ---+---+---\n 4 | 5 | 6      O | X |  \n---+---+---    ---+---+---\n 7 | 8 | 9      X | O |  "
}

**Technologies used:**
* Python 3.6
* Standard Python libraries: `socket`, `selectors`
* Communication Protocol: JSON for client-server communication

**Additional resources:**
- [Python documentation](https://docs.python.org/3/)
- [Python socket tutorial](https://realpython.com/python-sockets/)

**Note for CS457 Graders**
The requirements.txt is empty as I am only using the Standard Python Library. If that is not how I am suppoused to do it please let me know!

# Steps taken to create
**Step 0 (Sprint 0):**
- Creation of this github including this ReadMe.md and SOW.txt

**Step 1 (Sprint 1):**
- Basic Server Setup:
  - Create a server-side application that listens for incoming client connections on a specified port.
  - Implement a mechanism to handle multiple client connections simultaneously.
  - Log connection and disconnection events.
- Client-Side Connection:
  - Develop a client-side application that can connect to the server.
  - Implement error handling for failed connection attempts.
  - Log connection and disconnection events.
- Simple Message Exchange:
  - Establish a basic communication protocol between the server and clients.
  - Implement functions to send and receive messages.
  - Test the communication by sending simple messages back and forth.
- Error Handling:
  - Implement basic error handling for network-related issues (e.g., connection timeouts, socket errors).
  - Log error messages for debugging purposes.
- Testing and Debugging:
  - Test the server's ability to handle multiple client connections.
  - Verify that clients can connect to the server and exchange messages.
  - Debug any issues related to network communication or socket operations.
- Update README
- Include requirements.txt file (only need one per git repository)
  - This is done within a virtual python environment by running
  - pip freeze > requirements.txt
 
 
**Step 2 (Sprint 2):**
- Game Message Protocol Specification:
   - Define the structure and format of messages exchanged between the server and clients.
   - Include message types (e.g., join, move, chat, quit), data fields, and expected responses.
   - Consider using a well-defined protocol like JSON or Protocol Buffers for serialization and deserialization.  You may also things similar to the structs and classes of HW 3.
- Server-Side Message Handling:
   - Implement functions to receive, parse, and process incoming messages from clients.
   - Handle different message types appropriately (e.g., join requests, move commands, chat messages).
   - Maintain a list of connected clients and their associated game state.
- Client-Side Message Handling:
   - Implement functions to send messages to the server and handle incoming responses.
   - Parse server responses and update the client's game state accordingly.
   - Provide feedback to the user about the game's progress and any errors.
- Connection Management:
   - Implement mechanisms to handle client connections and disconnections.
   - Maintain a list of connected clients and their associated game data.
   - Notify other clients when a player joins or leaves the game.

**Step 3 (Sprint 3):**
- Game State Synchronization:
   - Implement a mechanism to synchronize the game state across all connected clients.
   - Use a central server to broadcast game state updates to all clients.
   - Implement techniques to handle network latency and ensure consistent gameplay.
- Client-Side Game Rendering:
   - Develop the client-side logic to render the game state based on updates received from the server.
   - Ensure that all clients display the same game state/board and player updates/moves.
- Turn-Based Gameplay:
   - Implement a system to manage player turns and ensure that only the current player can make moves.
   - If players compete for first time to answer implement the functionality to determine which player responded first
   - Synchronize turn information across all clients.
- Player Identification:
   - Assign unique identifiers to each player to distinguish them and track their game state.
   - Allow players to choose or be assigned unique usernames or avatars.

**Step 4 (Sprint 4):**
- Deliverables
   - Implement state, input handling, wining conditions, and gave over handling, and user interface.
   - Make sure client can be called like this:  client -i SERVER_IP/DNS -p PORT
   - Make sure server can be called like this:  server -p PORT  (set the listening IP to 0.0.0.0)
- Game State Management (continued):
   - Update the game state based on player moves and winning conditions.
   - Store information about the current player, the game board, and any relevant game settings.
- Input Handling:
   - Implement functions to handle user input (e.g., mouse clicks, keyboard input) and translate it into game actions (e.g., placing a piece on the board).
   - Validate user input to ensure it is within the game's boundaries and rules.
- Winning Conditions:
   - Define the conditions for winning the game (e.g., three in a row, diagonal, etc.).
   - Implement logic to check for winning conditions after each move.
   - Notify players when a winner is determined or the game ends in a draw.
- Game Over Handling:
   - Implement mechanisms to handle the end of a game, including:
   - Displaying the winner or announcing a draw.
   - Resetting the game state for a new round.
   - Providing options for players to start a new game or quit.
- User Interface (UI):
   - Develop a visually appealing and user-friendly UI for the game.
   - Display the game board, player information, and game status.
   - Provide clear and intuitive controls for players to interact with the game.

**Step 5 (Sprint 5):**
- Error Handling:
   - Implement error handling mechanisms to catch and handle potential exceptions or unexpected situations.
   - Handle network errors, invalid input, and other potential issues gracefully.
   - Provide informative error messages to the user.
- Integration Testing:
   - Test the entire game system to ensure that all components work together as expected.
   - Simulate different scenarios and test edge cases to identify potential bugs or issues.
- Security/Risk Evaluation:
   - Write a single paragraph or list describing what security issues your game may have and how they can be addressed. You do not need to address the security issues, just enumerate them and comment on how they could be addressed in a future iteration of the game.
