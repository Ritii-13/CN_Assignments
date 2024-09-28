import socket
import threading

class WebServer:
    def __init__(self, host='', port=6789):
        self.host = host
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threads = [] 

        try:
            self.serverSocket.bind((self.host, self.port))
            self.serverSocket.listen(5)
            print(f"Server listening on {self.host}:{self.port}...")
        except socket.error as e:
            print(f"Socket error during binding/listening: {e}")
            self.serverSocket.close()
            raise

    def start(self):
        try:
            while True:
                try:
                    connectionSocket, addr = self.serverSocket.accept()
                    print(f"Connected to: {addr}")

                    thread = threading.Thread(target=self.threaded_client, args=(connectionSocket,))
                    thread.start()
                    self.threads.append(thread)

                except socket.error as e:
                    print(f"Socket error in main loop: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected error in main loop: {e}")
                    break
        except KeyboardInterrupt:
            print("Server is shutting down...")
        finally:
            self.serverSocket.close()
            for thread in self.threads:
                thread.join()
            print("Server shutting down.")

    def threaded_client(self, connectionSocket):
        try:
            while True:
                try:
                    data = connectionSocket.recv(1024).decode()
                    if not data:
                        print("No data received; closing connection.")
                        break

                    print("Received request.")

                    # Simple HTTP request handling
                    lines = data.splitlines()
                    if len(lines) > 0:
                        # Getting the requested file from the HTTP request
                        filename = lines[0].split()[1]
                        if filename == "/":
                            filename = "/HelloWorld.html"

                        # Attempting to open the requested file
                        try:
                            print(f"Attempting to open file: {filename[1:]}")
                            with open(filename[1:], 'r') as f:
                                outputdata = f.read()

                            # Sending HTTP response header and content
                            response = "HTTP/1.1 200 OK\r\nConnection: keep-alive\r\n\r\n" + outputdata
                            print("File found and response sent.")
                        except FileNotFoundError:
                            print("File not found, sending 404 response.")
                            response = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
                        except Exception as e:
                            print(f"Error while opening file: {e}")
                            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n<html><body><h1>500 Internal Server Error</h1></body></html>"

                        connectionSocket.send(response.encode())

                except socket.error as e:
                    print(f"Socket error in thread: {e}")
                    break
                except Exception as e:
                    print(f"Error in thread: {e}")
                    break
        finally:
            connectionSocket.close()
            print("Connection closed.\n")


if __name__ == "__main__":
    try:
        server = WebServer(host='0.0.0.0', port=6789)
        server.start()
    except Exception as e:
        print(f"Failed to start server: {e}")

