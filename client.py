import socket
import threading
import sys

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

def receive_messages(client_socket):
    """Continuously listen for incoming messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'USERNAME_REQ':
                # The server is asking for our username
                pass
            elif message:
                # Print the received message to the terminal
                print(f"\r{message}")
                # Reprint the prompt after receiving a message
                print("> ", end="", flush=True)
            else:
                # Empty message usually means the server closed the connection
                print("\n[!] Disconnected from the server.")
                client_socket.close()
                sys.exit(0)
        except Exception as e:
            print(f"\n[!] Error receiving message: {e}")
            client_socket.close()
            sys.exit(1)

def start_client():
    """Connect to the server and handle user input."""
    # Choose a username
    username = input("Enter your username: ")
    while not username.strip():
        username = input("Username cannot be empty. Enter your username: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((HOST, PORT))
        print(f"[*] Connected to chat server at {HOST}:{PORT}")
        
        # Wait for the server to ask for the username
        initial_msg = client.recv(1024).decode('utf-8')
        if initial_msg == 'USERNAME_REQ':
            client.send(username.encode('utf-8'))
        else:
            print(initial_msg)
            
    except ConnectionRefusedError:
        print(f"[!] Could not connect to the server at {HOST}:{PORT}. Is it running?")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Connection error: {e}")
        sys.exit(1)

    # Start a thread to listen for messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    print("=====================================================")
    print("Welcome to the Chat Room!")
    print("Commands: ")
    print("  /join <room>        - Join or create a new room")
    print("  /users              - See who is online in your room")
    print("  /msg <user> <msg>   - Send a private message")
    print("  /quit               - Exit the chat")
    print("=====================================================\n")

    # Main thread handles user input
    try:
        while True:
            # Wait for user input
            message = input("> ")
            
            if not message.strip():
                continue
                
            if message == '/quit':
                print("Exiting chat...")
                client.close()
                sys.exit(0)
                
            # Send the message to the server
            client.send(message.encode('utf-8'))
            
    except KeyboardInterrupt:
        print("\nExiting chat...")
        client.close()
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error: {e}")
        client.close()
        sys.exit(1)

if __name__ == "__main__":
    start_client()
