import time
import threading
import random
import socket


# Configuration parameters
T1, T2 = 1, 3  # Time interval bounds for packet generation
T3, T4 = 1, 2  # Delay bounds for packet processing


# Configuration parameters
MAX_SEQ = 7
TIMEOUT_DURATION = 5
DROP_PROBABILITY = 0.1
WINDOW_SIZE_SENT = 7
WINDOW_SIZE_RECV = 1
TOT_PACKETS = 100

# Socket setup for sending and receiving
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# client_socket.bind(('127.0.0.1', 6002))  # Client (sending) on port 5001
try:
    server_socket.bind(('127.0.0.1', 5002))  # Server (receiving) on port 6001
    print("Entity 1 server on port 5002")
except OSError:
    print("Unable to bind server socket. Is the port already in use?")

# Statistics tracking
class Statistics:
    def __init__(self):
        self.total_sent = 0
        self.total_received = 0
        self.total_acks_recieved = 0
        self.total_acks_sent = 0
        self.total_dropped = 0
        self.total_retransmitted = 0
        self.total_delay = 0

    def print_stats(self):
        print("\n--- Entity 2 Transmission Statistics ---")
        print(f"Total Frames Sent: {self.total_sent}")
        print(f"Total Frames Received: {self.total_received}")
        print(f"Total ACKs Received: {self.total_acks_recieved}")
        print(f"Total ACKs Sent: {self.total_acks_sent}")
        print(f"Total Frames Dropped: {self.total_dropped}")
        print(f"Total Frames Retransmitted: {self.total_retransmitted}")
        print(f"Average delay per packet: {self.total_delay/self.total_received}")
        print(f"Average Retransmission time: {self.total_delay/self.total_retransmitted}")

stats = Statistics()

queue = []
# Frame class
class Frame:    
    def __init__(self, seq=0, ack=0, timestamp=None):
        self.seq = seq
        self.ack = ack
        self.timestamp = timestamp or time.time()
       
    def to_string(self):
        return f"{self.seq} {self.ack}"

    def packet_generator(self):
        for _ in range(TOT_PACKETS):
            time_to_wait = random.uniform(T1, T2)
            time.sleep(time_to_wait)
            packet= self.seq + self.ack
            #add packet to queue
            queue.append(packet)

    @staticmethod
    def from_string(data):
        parts = data.split()
        if len(parts) == 2:
            # If only seq and ack are present, set timestamp to 0
            seq, ack = parts
            timestamp = 0
        else:
            # If all three parts are present, unpack them normally
            seq, ack, timestamp = parts
        return Frame(int(seq), int(ack), float(timestamp))


# Timeout manager for retransmissions
class TimeoutManager:
    def __init__(self):
        self.timers = {}

    def start_timer(self, frame_num, callback):
        if frame_num in self.timers:
            self.cancel_timer(frame_num)
        timer = threading.Timer(TIMEOUT_DURATION, callback, [frame_num])
        self.timers[frame_num] = timer
        timer.start()

    def cancel_timer(self, frame_num):
        if frame_num in self.timers:
            self.timers[frame_num].cancel()
            del self.timers[frame_num]

timeout_manager = TimeoutManager()

# State variables
next_frame_to_send = 0
frame_expected = 0
ack_expected = 0
n_buffered = 0

# Helper function to check if a sequence number is within the window
def between(a, b, c):
    return ((a <= b < c) or (c < a <= b) or (b < c < a))

# Packet drop simulation
def should_drop_packet():
    return random.random() < DROP_PROBABILITY

# Function to send a frame
def send_frame(frame_num):
    time_to_wait = random.uniform(T1, T2)
    time.sleep(time_to_wait) 

    if should_drop_packet():
        print(f"\tEntity 1: Frame {frame_num} dropped.")
        stats.total_dropped += 1
        timeout_manager.start_timer(frame_num, retransmit_frame)
        return

    # Create frame with timestamp
    frame = Frame(seq=frame_num, ack=(frame_expected + MAX_SEQ) % (MAX_SEQ + 1), timestamp=time.time())
    client_socket.sendto(frame.to_string().encode(), ('127.0.0.1', 6002))
    print(f"\tEntity 1 sent frame: Seq={frame.seq}, Ack={frame.ack}, Timestamp={frame.timestamp}")
    stats.total_sent += 1
    timeout_manager.start_timer(frame_num, retransmit_frame)

# Function to retransmit a frame on timeout
def retransmit_frame(frame_num):
    print(f"\tEntity 1: Timeout occurred, retransmitting frame starting from {frame_num}")
    frame = frame_num
    while frame != next_frame_to_send:
        send_frame(frame)
        stats.total_retransmitted += 1
        frame = (frame + 1) % (MAX_SEQ + 1) 

# Client thread function for sending packets and managing the sliding window
def client_thread():
    global next_frame_to_send, ack_expected, n_buffered
    while stats.total_sent < TOT_PACKETS:
        if n_buffered < WINDOW_SIZE_SENT:
            send_frame(next_frame_to_send)
            next_frame_to_send = (next_frame_to_send + 1) % (MAX_SEQ + 1)
            n_buffered += 1
            time.sleep(random.uniform(T3, T4))

        # Receiving ACKs
        try:
            ack_data, _ = client_socket.recvfrom(1024)
            frame = Frame.from_string(ack_data.decode())
            print(f"Entity 1 received ACK for Seq={frame.ack}, Timestamp={frame.timestamp}")

            while between(ack_expected, frame.ack, next_frame_to_send):
                timeout_manager.cancel_timer(ack_expected)
                ack_expected = (ack_expected + 1) % (MAX_SEQ + 1)
                n_buffered -= 1
                stats.total_acks_received += 1

        except socket.timeout:
            print("")

# Server thread function for receiving packets and sending ACKs
def server_thread():
    global frame_expected
    while stats.total_received < TOT_PACKETS:
        try:
            data, _ = server_socket.recvfrom(1024)
            frame = Frame.from_string(data.decode())
            print(f"Entity 1 received frame: Seq={frame.seq}, Ack={frame.ack}, Timestamp={frame.timestamp}")

            if frame.seq == frame_expected:
                print(f"Entity 1: Frame {frame.seq} received in order at {time.time()}.")
                frame_expected = (frame_expected + 1) % (MAX_SEQ + 1)
                stats.total_received += 1

                # Send an ACK for the received frame
                ack_frame = Frame(seq=0, ack=frame.seq, timestamp=time.time())
                server_socket.sendto(ack_frame.to_string().encode(), ('127.0.0.1', 5002))
                print(f"\tEntity 1 sent ACK for Seq={frame.seq}, Timestamp={ack_frame.timestamp}")
                stats.total_acks_sent += 1

        except socket.timeout:
            print("Entity 1: Socket timed out while waiting for frame.")

# Set timeout for client socket
client_socket.settimeout(5)

# Start client and server threads
client = threading.Thread(target=client_thread)
server = threading.Thread(target=server_thread)

client.start()
server.start()

client.join()
server.join()

# Print statistics after communication
stats.print_stats()