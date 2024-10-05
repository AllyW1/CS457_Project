Creator: Allison Whittern

# Tic-Tac-Toe Game

![image](https://github.com/user-attachments/assets/543d15a8-89b7-49b1-b6c6-8a08649d4519)

This is a simple Tic-Tac-Toe game implemented using Python and sockets. Made for CS457 at CSU.

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
- [Python documentation](https://docs.python.org/3/)
- [Python socket tutorial](https://realpython.com/python-sockets/)

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
-Include requirements.txt file (only need one per git repository)
  - This is done within a virtual python environment by running
  - pip freeze > requirements.txt
