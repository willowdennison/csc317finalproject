import socket
import pyaudio
import struct
import pickle



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 208))
print("Connected")

p = pyaudio.PyAudio()
CHUNK = 1024
stream = p.open(format=p.get_format_from_width(2),channels=2,rate=44100,output=True,frames_per_buffer=CHUNK)



#stole this. idk how it work or what it do
data = b""
payload_size = struct.calcsize("Q")
while True:
    try:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024)
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        stream.write(frame)
    except:
        print("breaking")
        break

