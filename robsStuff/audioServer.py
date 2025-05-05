import os
import pyaudio
import socket
import wave
import struct
import pickle


#os.system("ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format('test.mp4','audio.wav'))

#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind(('localhost', 208))
#server_socket.listen(1)
#print("Waiting for client connect")

#client_socket, addr = server_socket.accept()
#print("Connected to: ", addr)



CHUNK = 1764
wf = wave.open("audio.wav", 'rb')
p = pyaudio.PyAudio()
print('server listening')
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate(),input=True,frames_per_buffer=CHUNK)
out_stream = p.open(format=p.get_format_from_width(2),channels=2,rate=44100,output=True,frames_per_buffer=CHUNK)

i = 0

while True:
    data = wf.readframes(CHUNK)
    #print(len(data))
    out_stream.write(data)
    print(i)
    i+=1
    #print("frame")
    
    #a = pickle.dumps(data)
    #message = struct.pack("Q",len(a))+a
    #server_socket.sendall(message)



