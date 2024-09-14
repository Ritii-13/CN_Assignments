import time
from socket import *


serverName = '127.0.0.1'  # (localhost)
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)  

RTTs = []
tot_packets = 10
lost_packets = 0

for i in range(1, tot_packets + 1):
    send_time = time.time()
    message = f"Ping {i} {send_time}"

    try:
        clientSocket.sendto(message.encode(), (serverName, serverPort))
        start_time = time.time()
        response, serverAddress = clientSocket.recvfrom(1024)
        end_time = time.time()

        rtt = end_time - start_time
        RTTs.append(rtt)

        print(f"Reply from {serverName}: {response.decode()}")
        print(f"RTT: {rtt:.6f} seconds")

    except timeout:
        print("Request timed out")
        lost_packets += 1

if RTTs:
    min_rtt = min(RTTs)
    max_rtt = max(RTTs)
    avg_rtt = sum(RTTs) / len(RTTs)
else:
    min_rtt = max_rtt = avg_rtt = None

print(f"\n--- Ping statistics ---")
print(f"Packets: Sent = {tot_packets}, Received = {tot_packets - lost_packets}, Lost = {lost_packets} ({(lost_packets / tot_packets) * 100}% packet loss)")
if RTTs:
    print(f"RTTs: Min = {min_rtt:.6f}s, Max = {max_rtt:.6f}s, Avg = {avg_rtt:.6f}s")

clientSocket.close()
