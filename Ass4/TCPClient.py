import socket
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: client.py <server_host> <server_port> <filename>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
      
        client_socket.connect((server_host, server_port))
        print(f"Connected to server at {server_host}:{server_port}")

       
        request_line = f"GET /{filename} HTTP/1.1\r\n"
        headers = f"Host: {server_host}\r\nConnection: close\r\n\r\n"
        request = request_line + headers

      
        client_socket.sendall(request.encode())
        print("Sent request:")
        print(request)

        response = client_socket.recv(4096) 
        print("Received response:")
        print(response.decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
