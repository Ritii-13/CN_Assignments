import random
import time
from socket import *


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', 12000))  
print("The server is ready to receive heartbeats...")

while True:
    rand = random.randint(0, 10) 
    message, clientAddress = serverSocket.recvfrom(1024)  
    
    if rand < 4:
        continue

    decoded_message = message.decode()
    print(f"Received message: {decoded_message}")

    _, sequence_number, sent_time = decoded_message.split()  
    
  
    receive_time = time.time()
    time_diff = receive_time - float(sent_time)
    
 
    response_message = f"{sequence_number} {time_diff:.6f}"
    serverSocket.sendto(response_message.encode(), clientAddress)