import time
from socket import *

class UDPPingerClient:
    tot_packets = 10
    lost_packets = 0
    RTTs = []
    min_rtt = max_rtt = avg_rtt = None

    def __init__ (self, serverName, serverPort):
        self.serverName = serverName
        self.serverPort = serverPort
        self.clientSocket = socket(family = AF_INET, type = SOCK_DGRAM, proto=0, fileno=None)
        self.clientSocket.settimeout(1)

    def calculateRTT(self, end_time, start_time):
        return  end_time - start_time
    
    def ping(self, tot_packets):
        for i in range(1, tot_packets + 1):
            send_time = time.time()
            message = f"Ping {i} {send_time}"

            try:
                self.clientSocket.sendto(message.encode(), (self.serverName, self.serverPort))
                start_time = time.time()
                response, serverAddress = self.clientSocket.recvfrom(4096)
                end_time = time.time()

                rtt = self.calculateRTT(end_time, start_time)
                self.RTTs.append(rtt)

                print(f"Reply from {self.serverName}, address: {serverAddress}: {response.decode()}")
                print(f"RTT: {rtt:.6f} seconds")

            except timeout:
                print("Request timed out")
                self.lost_packets += 1

        if self.RTTs:
            self.min_rtt = min(self.RTTs)
            self.max_rtt = max(self.RTTs)
            self.avg_rtt = sum(self.RTTs) / len(self.RTTs)

    def print_stats(self):
        print(f"\n--- Ping statistics ---")
        print(f"Packets: Sent = {self.tot_packets}, Received = {self.tot_packets - self.lost_packets}, Lost = {self.lost_packets} ({(self.lost_packets / self.tot_packets) * 100}% packet loss)")
        if self.RTTs:
            print(f"RTTs: Min = {self.min_rtt:.6f}s, Max = {self.max_rtt:.6f}s, Avg = {self.avg_rtt:.6f}s")

    def close(self):
        self.clientSocket.shutdown(SHUT_RDWR)
        self.clientSocket.close()


serverName = '127.0.0.1'
serverPort = 12000

client = UDPPingerClient(serverName, serverPort)

client.ping(client.tot_packets)
client.print_stats()
client.close()


# def calculateRTT(end_time, start_time):
#     return  end_time - start_time

# serverName = '127.0.0.1' 
# serverPort = 12000
# clientSocket = socket(family = AF_INET, type = SOCK_DGRAM, proto=0, fileno=None)
# clientSocket.settimeout(1)  

# RTTs = []
# tot_packets = 10
# lost_packets = 0

# for i in range(1, tot_packets + 1):
#     send_time = time.time()
#     message = f"Ping {i} {send_time}"

#     try:
#         clientSocket.sendto(message.encode(), (serverName, serverPort))
#         start_time = time.time()
#         response, serverAddress = clientSocket.recvfrom(4096)
#         end_time = time.time()

#         rtt = calculateRTT(end_time, start_time)
#         RTTs.append(rtt)

#         print(f"Reply from {serverName}: {response.decode()}")
#         print(f"RTT: {rtt:.6f} seconds")

#     except timeout:
#         print("Request timed out")
#         lost_packets += 1

# if RTTs:
#     min_rtt = min(RTTs)
#     max_rtt = max(RTTs)
#     avg_rtt = sum(RTTs) / len(RTTs)
# else:
#     min_rtt = max_rtt = avg_rtt = None

# print(f"\n--- Ping statistics ---")
# print(f"Packets: Sent = {tot_packets}, Received = {tot_packets - lost_packets}, Lost = {lost_packets} ({(lost_packets / tot_packets) * 100}% packet loss)")
# if RTTs:
#     print(f"RTTs: Min = {min_rtt:.6f}s, Max = {max_rtt:.6f}s, Avg = {avg_rtt:.6f}s")

# clientSocket.shutdown(SHUT_RDWR)
# clientSocket.close()
