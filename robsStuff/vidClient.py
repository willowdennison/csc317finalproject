import socket
import cv2
import pickle
import struct

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 208))
server_socket.listen(1)
print("Waiting for client connect")

client_socket, addr = server_socket.accept()
print("Connected to: ", addr)

try:
    while True:
        packed_size = client_socket.recv(4)
        if not packed_size:
            break
        frame_size = struct.unpack("I", packed_size)[0]

        frame_data = recv_exact(client_socket, frame_size)
        if frame_data is None:
            break
        frame = cv2.imdecode(pickle.loads(frame_data),cv2.IMREAD_COLOR)
        cv2.imshow("rec", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


except Exception as e:
    print("Error: ", e)
finally:
    cv2.destroyAllWindows()
    client_socket.close()
    server_socket.close()
    print("Connection closed")
