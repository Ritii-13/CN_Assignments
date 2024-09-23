from socket import *
import sys

# Stream instead of datagram in TCP
serverSocket = socket(AF_INET, SOCK_STREAM)


serverPort = 6789  # can be changed
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print('Ready to serve...')

while True:
    # Accept the connection
    connectionSocket, addr = serverSocket.accept()

    try:
        # Receive the request from the client
        message = connectionSocket.recv(1024).decode()
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()

        # Use this part for part 1
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        
        # For client in part 3 to work use this code (next 2 lines) and comment out above code
        # response = "HTTP/1.1 200 OK\r\n\r\n" + outputdata
        # connectionSocket.send(response.encode())

        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
        
    except IOError:
        # Send 404 response for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        connectionSocket.close()

serverSocket.close()
sys.exit()  # Terminate the program after sending the data
