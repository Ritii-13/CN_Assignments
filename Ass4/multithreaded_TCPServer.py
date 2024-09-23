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

# Create a global variable for the server socket and a lock
serverSocket = None
shutdown_flag = False
shutdown_lock = threading.Lock()

def signal_handler(sig, frame):
    global shutdown_flag
    print('Signal received: Shutting down the server...')
    with shutdown_lock:
        shutdown_flag = True  # Set the flag to indicate shutdown
    if serverSocket:
        serverSocket.close()  # Close the server socket
    sys.exit(0)  # Exit the program

def threaded_client(connectionSocket):
    while True:
        with shutdown_lock:
            if shutdown_flag:  # Check if the server is shutting down
                print("Thread exiting due to shutdown flag.")
                break

        try:
            data = connectionSocket.recv(1024).decode()  # Receive and decode the data
            if not data:
                print("No data received; closing connection.")
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
                    print(f"Attempting to open file: {filename[1:]}")
                    with open(filename[1:], 'r') as f:
                        outputdata = f.read()
                    
                    # Send HTTP response header and content
                    response = "HTTP/1.1 200 OK\r\n\r\n" + outputdata
                    print("File found and response sent.")
                except FileNotFoundError:
                    # File not found response
                    print("File not found, sending 404 response.")
                    response = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
                
                connectionSocket.send(response.encode())  # Send the response
        except Exception as e:
            print(f"Error in thread: {e}")
            break

    connectionSocket.close()
    print("Connection closed.\n")

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

    threads = []  # List to keep track of threads

    while True:
        try:
            connectionSocket, addr = serverSocket.accept()
            print(f"Connected to: {addr}")
            thread = threading.Thread(target=threaded_client, args=(connectionSocket,))
            thread.start()
            threads.append(thread)  # Add thread to the list

            # Check for shutdown flag in the main loop
            with shutdown_lock:
                if shutdown_flag:
                    print("Main loop exiting due to shutdown flag.")
                    break
        except Exception as e:
            print(f"Error in main loop: {e}")
            break

    # Wait for all threads to finish before exiting
    print("Waiting for all threads to finish...")
    for thread in threads:
        thread.join()
    print("All threads have finished.")

    # Close the server socket (in case the loop is exited)
    serverSocket.close()
    print("Server socket closed.")

if __name__ == "__main__":
    main()
