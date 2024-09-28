from socket import *
import sys

try:
    serverSocket = socket(AF_INET, SOCK_STREAM)
    
    serverPort = 6789  
    serverSocket.bind(('0.0.0.0', serverPort))
    serverSocket.listen(1)
    print(f"Server is running on port {serverPort}...")

except socket.error as e:
    print(f"Socket error: {e}")
    sys.exit()


while True:
    print('Ready to serve...')

    try:
        connectionSocket, addr = serverSocket.accept()
        print(f"Connection established with {addr}")

        try:
            message = connectionSocket.recv(1024).decode()
            if not message:
                raise ValueError("No message received or connection closed by client.")

            print(f"Message received")

            filename = message.split()[1]
            try:
                with open(filename[1:], 'r') as f:
                    outputdata = f.read()

                # # for part 1
                # connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
                # for i in range(0, len(outputdata)):
                #     connectionSocket.send(outputdata[i].encode())
                
                # For client in part 3 next 2 lines and comment out above code
                response = "HTTP/1.1 200 OK\r\n\r\n" + outputdata
                connectionSocket.send(response.encode())

                connectionSocket.send("\r\n".encode())
                print(f"File {filename[1:]} served successfully.")
            
            except FileNotFoundError:
                print(f"File not found: {filename[1:]}")
                connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

        except ValueError as ve:
            print(f"Error: {ve}")
        
        except Exception as e:
            print(f"An error occurred while processing the request: {e}")

        finally:
            connectionSocket.close()

    except KeyboardInterrupt:
        print("Server is shutting down...")
        serverSocket.close()
        sys.exit()

    except Exception as e:
        print(f"An error occurred in the connection handling: {e}")
        connectionSocket.close()
