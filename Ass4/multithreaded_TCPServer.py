# from socket import *
# import threading
# import sys

# # Function to handle each client's request
# def handle_client(connectionSocket):
#     try:
#         # Receive the request from the client
#         #each client has a different port to receive message
#         message = connectionSocket.recv(1024).decode() 
#         # print(f"Request from {connectionSocket.getpeername()}: {message}")
#         if not message:
#             connectionSocket.close()
#             return
        
#         filename = message.split()[1]
#         f = open(filename[1:])
#         outputdata = f.read()

#         # Send HTTP response header and file content
#         connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
#         for i in range(0, len(outputdata)):
#             connectionSocket.send(outputdata[i].encode())

#         connectionSocket.send("\r\n".encode())
#     except IOError:
#         # Send 404 response for file not found
#         connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
#         connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
    
#     # Close the connection socket
#     connectionSocket.close()


# serverSocket = socket(AF_INET, SOCK_STREAM)


# serverPort = 6789  
# serverSocket.bind(('', serverPort))
# serverSocket.listen(5)  

# print('Multi-threaded server is ready to serve...')

# while True:
   
#     connectionSocket, addr = serverSocket.accept()
#     print(f"Connection established with {addr}")

    
#     client_thread = threading.Thread(target=handle_client, args=(connectionSocket,))
#     client_thread.start()


# serverSocket.close()
# sys.exit()
import socket
import threading
import sys
import signal

# Create a global variable for the server socket
serverSocket = None

def signal_handler(sig, frame):
    print('Shutting down the server...')
    
    if serverSocket:
        serverSocket.close()  # Close the server socket
    sys.exit(0)  # Exit the program

def threaded_client(connectionSocket):
    while True:
        try:
            data = connectionSocket.recv(1024).decode()  # Receive and decode the data
            if not data:
                break

            # Print the received request for debugging
            print(f"Received request: {data}")

            # Simple HTTP request handling
            lines = data.splitlines()
            if len(lines) > 0:
                # Get the requested file from the HTTP request
                filename = lines[0].split()[1]
                if filename == "/":
                    filename = "/HelloWorld.html"  # Default file

                # Attempt to open the requested file
                try:
                    with open(filename[1:], 'r') as f:
                        outputdata = f.read()
                    
                    # Send HTTP response header and content
                    response = "HTTP/1.1 200 OK\r\n\r\n" + outputdata
                except FileNotFoundError:
                    # File not found response
                    response = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
                
                connectionSocket.send(response.encode())  # Send the response
        except Exception as e:
            print("Error:", e)
            break

    connectionSocket.close()

def main():
    global serverSocket

    host = ""
    port = 6789
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    print(f"Server listening on port {port}...")

    # Register the signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            connectionSocket, addr = serverSocket.accept()
            print(f"Connected to: {addr}")
            threading.Thread(target=threaded_client, args=(connectionSocket,)).start()
        except Exception as e:
            print("Error:", e)
            break

    # Close the server socket (in case the loop is exited)
    serverSocket.close()

if __name__ == "__main__":
    main()
