# import socket
# import sys

# def main():
#     if len(sys.argv) != 4:
#         print("Usage: client.py <server_host> <server_port> <filename>")
#         sys.exit(1)

#     server_host = sys.argv[1]
#     server_port = int(sys.argv[2])
#     filename = sys.argv[3]


#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     try:
      
#         client_socket.connect((server_host, server_port))
#         print(f"Connected to server at {server_host}:{server_port}")

       
#         request_line = f"GET /{filename} HTTP/1.1\r\n"
#         headers = f"Host: {server_host}\r\nConnection: close\r\n\r\n"
#         request = request_line + headers

      
#         client_socket.sendall(request.encode())
#         print("Sent request:")
#         print(request)

#         response = client_socket.recv(4096) 
#         print("Received response:")
#         print(response.decode())

#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()

# if __name__ == "__main__":
#     main()

import socket
import sys

class TCPClient:
    def __init__(self, host, port, filename):
        self.host = host
        self.port = port
        self.filename = filename
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def create_request(self):
        request_line = f"GET /{self.filename} HTTP/1.1\r\n"
        headers = f"Host: {self.host}\r\n Connection: close\r\n\r\n"
        return request_line + headers

    def send_request(self):
        request = self.create_request()
        self.client_socket.sendall(request.encode())
        print("Sent request:")
        print(request)

    def receive_response(self):
        response = self.client_socket.recv(4096)
        print("Received response:")
        print(response.decode())

    def close(self):
        self.client_socket.close()
        print("Connection closed.")

def main():
    if len(sys.argv) != 4:
        print("Usage: client.py <server_host> <server_port> <filename>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    client = TCPClient(server_host, server_port, filename)

    try:
        client.connect()        
        client.send_request()   
        client.receive_response()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close() 

if __name__ == "__main__":
    main()
