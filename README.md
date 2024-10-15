Creator: Allison Whittern

# Tic-Tac-Toe Game

![image](https://github.com/user-attachments/assets/543d15a8-89b7-49b1-b6c6-8a08649d4519)

This is a simple Tic-Tac-Toe game implemented using Python and sockets. Made for CS457 at CSU.

**How to play:**
1. **Start the server:** Run the `server.py` script.
   - terminal: python3 server.py [hostname] [port]
   - Ex: python3 server.py localhost 9000
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
   - terminal: python3 client.py [hostname] [port]
   - python3 client.py localhost 9000
   - ENSURE client and server are looking at the same port. In the example that is localhost 9000
   - Game won't start until two clients are connected to the server.
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!
   - Players are assigned symbols: Player X and Player O.
   - Players take turns entering their moves. The move is entered as a number (1-9), corresponding to the position on the Tic-Tac-Toe grid.
   - The first player to get three in a row (horizontally, vertically, or diagonally) wins!
   - The game will also end if all nine spaces are filled and no player has won, resulting in a draw.
     <img width="323" alt="image" src="https://github.com/user-attachments/assets/11869fe2-1eca-47f9-92a0-520ffd20ac1a">
   - You will look at the position key. Choose the number of the position you are choosing. Then wait till it is your turn again. 

4. **End of Game:**
   - When a player wins, the game will announce "Game Over! Player X/O wins!"
   - If the game results in a draw, it will announce "Game Over! The game is a draw!"
   - Game will force quit, Server and Client Connections will be cleaned up. (If you want to play again just start up the server and clients again)

**Game Message Protocol Specification:**
- Message Types:
   - Join: Sent when a client joins the server.
json
{ "type": "join" }
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
  "message": "Player X's turn.",
  "board": "1 | 2 | 3\n4 | 5 | 6\n7 | 8 | 9\n"
}

**Technologies used:**
* Python 3.x
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
