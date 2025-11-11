import socket

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

# Create TCP server socket
s = socket.socket()
s.bind(("localhost", 5000))
s.listen(1)

print("RPC Server started... Waiting for client...")

conn, addr = s.accept()
print("Client connected:", addr)

# Receive data from client
data = conn.recv(1024).decode()
choice, a, b = data.split()
a = int(a)
b = int(b)

# Perform operation
if choice == "1":
    result = add(a, b)
elif choice == "2":
    result = sub(a, b)
else:
    result = "Invalid Operation"

# Send result back to client
conn.send(str(result).encode())

conn.close()
s.close()
