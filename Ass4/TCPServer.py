from socket import *
import sys

serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 6789  
serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

while True:
    print('Ready to serve...')

    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024).decode()
        if not message:
            connectionSocket.close()
            continue

        filename = message.split()[1]
        with open(filename[1:]) as f:
            outputdata = f.read()

        print("Requested file: " + filename)

        response = "HTTP/1.1 200 OK\r\n\r\n" + outputdata
        connectionSocket.sendall(response.encode())

        print("Sent response to client")

    except IOError:
        # Send a 404 error message if the file is not found
        error_response = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
        connectionSocket.sendall(error_response.encode())
        print("File not found, sending 404 response.")

    finally:
        connectionSocket.close()
        print("Connection closed.")

serverSocket.close()
sys.exit()
