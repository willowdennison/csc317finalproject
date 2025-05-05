import cv2
import time
import pickle
import struct
import socket
import pydub


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 208))




videoPath = "test.mp4"
cap = cv2.VideoCapture(videoPath)
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video FPS: {fps}")

try:
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("Not Ret")
            break

        frame = cv2.resize(frame, (640, 480))
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        data = pickle.dumps(buffer)
        message_size = struct.pack("I", len(data))
        client_socket.sendall(message_size + data)

        #cv2.imshow("Sender", frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break


        time_to_sleep = max(0, (1 / fps) - (time.time() - start_time))
        time.sleep(time_to_sleep)

except KeyboardInterrupt:
    print("Sender stopped")

finally:
    cap.release()
    cv2.destroyAllWindows()