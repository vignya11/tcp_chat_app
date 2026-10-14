# TCP Client-Server Chat Application

This is a Python-based TCP chat application built for a Computer Networks Project Based Learning (PBL) assignment. It demonstrates core networking concepts such as socket programming, concurrency, and custom application-layer protocols.

## Features

- **Multi-threaded Server**: Handles multiple clients concurrently without blocking, using Python's `threading` module.
- **Chat Rooms / Channels**: Users can switch rooms dynamically using `/join <RoomName>`. Server correctly routes traffic only to sockets in the target room.
- **Message Timestamps**: All messages are prepended with the server's local time for accurate logging.
- **Private Messaging**: Direct messaging functionality between specific users using `/msg` (works across different chat rooms).
- **Active User Tracking**: See who is currently online in your room using the `/users` command.
- **Graceful Disconnects**: If a client abruptly disconnects, the server handles it safely and notifies the rest of the chat.

## Architecture

The project is built on the standard OSI Model's Transport Layer (Layer 4) using **TCP (Transmission Control Protocol)**.
- `server.py`: Listens for incoming connections, spawns a new thread for each client, and acts as the central router for messages.
- `client.py`: A command-line client that connects to the server and uses two threads: one for capturing local keyboard input, and one for listening to incoming network packets from the server.
- `client_gui.py`: A graphical version of the client built using Tkinter, providing a user-friendly window for chatting instead of the terminal.

## How to Run

1. **Start the Server**
   Open a terminal and run the server script. It will listen on `127.0.0.1:5555` by default.
   ```bash
   python server.py
   ```

2. **Start the Clients**
   Open a *new* terminal window (or multiple windows) and run either the CLI or GUI client.
   ```bash
   # For the Graphical User Interface (Recommended)
   python client_gui.py
   
   # For the Command Line Interface
   python client.py
   ```

3. **Chatting**
   - Enter your desired username when prompted.
   - Start typing to send messages to the public room.
   - Try the commands like `/users` to see who is online.
   - Try sending a private message using `/msg <username> <your message>`.
   - Type `/quit` to leave the chat safely.

## Author
*Sultana*
