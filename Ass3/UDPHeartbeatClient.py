import time
from socket import *

class UDPHeartbeatClient:
    tot_packets = 1000 
    missed_heartbeats = 0  
    consecutive_misses = 0  
    total_sent = 0


    def __init__ (self, serverName, serverPort):
        self.serverName = serverName
        self.serverPort = serverPort
        self.clientSocket = socket(family = AF_INET, type = SOCK_DGRAM)
        self.clientSocket.settimeout(1) 

    def ping(self, tot_packets):
        for i in range(1, tot_packets + 1):
            send_time = time.time()
            self.total_sent += 1

            message = f"Ping {i} {send_time}"

            try:
             
                self.clientSocket.sendto(message.encode(), (self.serverName, self.serverPort))
                
                response, serverAddress = self.clientSocket.recvfrom(1024)
                recv_time = time.time()

                response_message = response.decode()
                sequence_number, time_diff = response_message.split()
                time_diff = float(time_diff)

                print(f"Received heartbeat response {sequence_number}: Time difference = {time_diff:.6f} seconds")

                self.consecutive_misses = 0

            except timeout:
               
                self.consecutive_misses += 1
                self.missed_heartbeats += 1
                print(f"Heartbeat {i}: Request timed out")

            if self.consecutive_misses == 3:
                print("Server is down! 3 consecutive heartbeat responses were missed.")
                break

    def print_stats(self):
        print(f"\n--- Heartbeat statistics ---")
        print(f"Packets: Sent = {self.total_sent}, Received = {self.total_sent - self.missed_heartbeats}, Lost = {self.missed_heartbeats} ({(self.missed_heartbeats / self.total_sent) * 100}% packet loss)")

    def close(self):
        self.clientSocket.shutdown(SHUT_RDWR)
        self.clientSocket.close()

serverName = '127.0.0.1'
serverPort = 12000

client = UDPHeartbeatClient(serverName, serverPort)
client.ping(client.tot_packets)
client.print_stats()
client.close()
