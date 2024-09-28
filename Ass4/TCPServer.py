from socket import *
import sys

# Stream instead of datagram in TCP
serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 6789  
serverSocket.bind(('0.0.0.0', serverPort))
serverSocket.listen(1)


while True:
    print('Ready to serve...')

    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024).decode()

        if not message:
            connectionSocket.close()
            continue

        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()

        # for part 1
        # connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        # for i in range(0, len(outputdata)):
        #     connectionSocket.send(outputdata[i].encode())
        
        # For client in part 3 next 2 lines and comment out above code
        response = "HTTP/1.1 200 OK\r\n\r\n" + outputdata
        connectionSocket.send(response.encode())

        print(response)

        connectionSocket.send("\r\n".encode())
        f.close()
        connectionSocket.close()
        
    except IOError:
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        connectionSocket.close()

serverSocket.close()
sys.exit()  
