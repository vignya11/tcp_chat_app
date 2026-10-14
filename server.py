import socket
import threading
import sys

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 5555         # Port to listen on

# Dictionary to keep track of connected clients
# Format: {client_socket: {'username': 'John', 'room': 'General'}}
clients = {}

def broadcast(message, room_name, sender_socket=None):
    """Send a message to all clients in a specific room."""
    for client_socket, info in list(clients.items()):
        if info['room'] == room_name and client_socket != sender_socket:
            try:
                client_socket.send(message)
            except:
                remove_client(client_socket)

def handle_client(client_socket):
    """Handle communication with a single client."""
    try:
        # Ask for a username upon connection
        client_socket.send("USERNAME_REQ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        
        # 5. New clients should join a default room called "General" automatically on connect
        current_room = 'General'
        clients[client_socket] = {'username': username, 'room': current_room}
        
        print(f"[+] {username} joined room '{current_room}'.")
        
        # 2. When a client joins, everyone in that room should see a system message like "*** <username> joined the room ***"
        welcome_msg = f"*** {username} joined the room ***\n"
        broadcast(welcome_msg.encode('utf-8'), current_room, client_socket)
        
        # Send room confirmation to the user
        client_socket.send(f"System: You joined the '{current_room}' room.\n".encode('utf-8'))

        while True:
            # Receive messages from the client
            message = client_socket.recv(1024)
            if not message:
                break
                
            decoded_msg = message.decode('utf-8').strip()
            
            # Check for commands
            if decoded_msg.startswith('/users'):
                # 6. Keep the existing /users command working, but update it to show only users in the sender's current room
                users_in_room = [info['username'] for sock, info in clients.items() if info['room'] == current_room]
                user_list = f"Users in '{current_room}': " + ", ".join(users_in_room) + "\n"
                client_socket.send(user_list.encode('utf-8'))
                
            elif decoded_msg.startswith('/join '):
                # 1. A /join <roomname> command that moves a client into a named room
                parts = decoded_msg.split(' ', 1)
                if len(parts) == 2:
                    new_room = parts[1].strip()
                    if new_room != current_room:
                        # 3. When a client leaves a room (by joining another room), the old room should see "*** <username> left the room ***"
                        leave_msg = f"*** {username} left the room ***\n"
                        broadcast(leave_msg.encode('utf-8'), current_room, client_socket)
                        
                        # Update room
                        current_room = new_room
                        clients[client_socket]['room'] = current_room
                        
                        # 2. When a client joins, everyone in that room should see "*** <username> joined the room ***"
                        join_msg = f"*** {username} joined the room ***\n"
                        broadcast(join_msg.encode('utf-8'), current_room, client_socket)
                        
                        # Confirm to user
                        client_socket.send(f"System: You moved to the '{current_room}' room.\n".encode('utf-8'))
                else:
                    client_socket.send(f"Usage: /join <roomname>\n".encode('utf-8'))
                    
            elif decoded_msg.startswith('/msg '):
                # 7. Do not change how /msg (private messaging) works — private messages should still work across rooms
                parts = decoded_msg.split(' ', 2)
                if len(parts) >= 3:
                    target_user = parts[1]
                    private_msg = parts[2]
                    send_private_msg(target_user, private_msg, username, client_socket)
                else:
                    client_socket.send(f"Usage: /msg <username> <message>\n".encode('utf-8'))
                    
            else:
                # 4. Regular messages should only broadcast to other clients in the SAME room
                formatted_message = f"[{username}]: {decoded_msg}\n"
                broadcast(formatted_message.encode('utf-8'), current_room, client_socket)
                print(f"({current_room}) {formatted_message.strip()}")
                
    except ConnectionResetError:
        pass
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        remove_client(client_socket)

def send_private_msg(target_user, message, sender_name, sender_socket):
    """Send a private message to a specific user, regardless of their room."""
    target_socket = None
    for sock, info in clients.items():
        if info['username'] == target_user:
            target_socket = sock
            break
            
    if target_socket:
        formatted_message = f"[PRIVATE from {sender_name}]: {message}\n"
        try:
            target_socket.send(formatted_message.encode('utf-8'))
            sender_socket.send(f"[PRIVATE to {target_user}]: {message}\n".encode('utf-8'))
        except:
            remove_client(target_socket)
    else:
        sender_socket.send(f"User '{target_user}' not found.\n".encode('utf-8'))

def remove_client(client_socket):
    """Clean up when a client disconnects."""
    if client_socket in clients:
        info = clients[client_socket]
        username = info['username']
        room = info['room']
        print(f"[-] {username} disconnected from '{room}'.")
        
        del clients[client_socket]
        client_socket.close()
        
        # 3. When a client leaves a room (by disconnecting), the old room should see "*** <username> left the room ***"
        broadcast(f"*** {username} left the room ***\n".encode('utf-8'), room)

def start_server():
    """Start the TCP server and listen for connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[*] Server listening on {HOST}:{PORT}")
        print("[*] Waiting for connections...")
        
        while True:
            client_socket, client_address = server.accept()
            print(f"[*] New connection from {client_address[0]}:{client_address[1]}")
            
            thread = threading.Thread(target=handle_client, args=(client_socket,))
            thread.daemon = True
            thread.start()
            
    except KeyboardInterrupt:
        print("\n[*] Server shutting down.")
        server.close()
        sys.exit(0)
    except Exception as e:
        print(f"[!] Server error: {e}")
        server.close()

if __name__ == "__main__":
    start_server()
