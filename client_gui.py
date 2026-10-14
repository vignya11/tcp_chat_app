import socket
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("TCP Chat Application")
        self.master.geometry("500x600")
        self.master.configure(bg="#2C3E50")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = ""

        self.setup_ui()
        self.connect_to_server()

    def setup_ui(self):
        # Chat Display Area
        self.chat_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 12), state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Bottom Frame for Input
        self.bottom_frame = tk.Frame(self.master, bg="#2C3E50")
        self.bottom_frame.pack(padx=10, pady=5, fill=tk.X)

        self.msg_entry = tk.Entry(self.bottom_frame, font=("Arial", 14), bg="#FFFFFF", fg="#2C3E50", insertbackground="#2C3E50")
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.bottom_frame, text="Send", font=("Arial", 12, "bold"), bg="#3498DB", fg="#FFFFFF", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Protocol instructions
        self.info_label = tk.Label(self.master, text="Commands: /join <room> | /users | /msg <user> <text>", bg="#2C3E50", fg="#BDC3C7", font=("Arial", 9))
        self.info_label.pack(side=tk.BOTTOM, pady=5)

    def connect_to_server(self):
        # Prompt for username
        self.username = simpledialog.askstring("Username", "Please enter your username:", parent=self.master)
        if not self.username or not self.username.strip():
            messagebox.showerror("Error", "Username cannot be empty!")
            self.master.destroy()
            return

        try:
            self.client_socket.connect((HOST, PORT))
            
            # Start background thread to listen for messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", f"Could not connect to server at {HOST}:{PORT}\nMake sure server.py is running.")
            self.master.destroy()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == 'USERNAME_REQ':
                    self.client_socket.send(self.username.encode('utf-8'))
                elif message:
                    self.display_message(message)
                else:
                    self.display_message("[!] Disconnected from server.")
                    self.client_socket.close()
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.client_socket.close()
                break

    def send_message(self, event=None):
        message = self.msg_entry.get().strip()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.msg_entry.delete(0, tk.END)
                if message.startswith('/quit'):
                    self.master.destroy()
            except Exception as e:
                messagebox.showerror("Error", "Lost connection to the server.")
                self.master.destroy()

    def display_message(self, message):
        # GUI updates must happen on the main thread, but Tkinter handles this reasonably well for simple inserts
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n" if not message.endswith("\n") else message)
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def on_closing(self):
        try:
            self.client_socket.send('/quit'.encode('utf-8'))
            self.client_socket.close()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
