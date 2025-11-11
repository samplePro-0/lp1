import socket

# Create TCP client socket
s = socket.socket()
s.connect(("localhost", 5000))

print("---- RPC MENU ----")
print("1. Add")
print("2. Subtract")

choice = input("Enter choice: ")
a = input("Enter first number: ")
b = input("Enter second number: ")

# Prepare message
message = choice + " " + a + " " + b

# Send to server
s.send(message.encode())

# Receive result
result = s.recv(1024).decode()
print("Result from server:", result)

s.close()
