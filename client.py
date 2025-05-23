from socket import*
import GUI
import threading
import time 
import os 
from videoStream import VideoStream
import pickle
import struct



class Client:
    
    
    def __init__(self):

        self._port = 821
        
        self.segmentLength = 1024 

        self.mainSocket = socket(AF_INET, SOCK_STREAM)
        print('Socket created')

        self.mainSocket.connect(('192.168.0.100', self._port))
        print('socket connected')

        self.recvThreadRunning = False
       
        self.playbackEnabled = True
        
        self.videoStream = None
       
        self.currentVideo = None

        recvThread = threading.Thread(target = self.receive)
        recvThread.start()

        self.interface = GUI.GUI(self)


    # sends a list command to the server and receives a list of available videos,recieves the list of vidoes and returns it as a strign 
    def listVideo(self):
        
         self.mainSocket.send('list\n'.encode())

         data = self.mainSocket.recv(1024).decode() 

         dirList = 'Videos avaiable on server:\n' + data
         
         return dirList


    #Sends request to server to start sending frame objects from vidoeName
    def selectVideo(self, videoName, startFrame , endFrame = None):
        
        self.recvThreadRunning = False 

        time.sleep(0.01)

        msg = f'select\n{videoName}\n{startFrame}'
        
        if endFrame is not None:
            msg += f'\n{endFrame}'
        
        self.mainSocket.send(msg.encode())

        info = self.mainSocket.recv(1024).decode()
       
        info = info.split('\n')
        
        fps = info[0].split(':')[1]
        
        numFrames = info[1].split(':')[1]
        
        self.currentVideo = videoName
        
        self.recvThreadRunning = True
        self.videoStream = VideoStream(fps, startFrame)
            
        
        recvThread = threading.Thread(target = self.receive)
        
        recvThread.start()


    # plays and pauses the video stream
    def playPause(self):

        if self.playbackEnabled:
           
            self.videoStream.pause()
            
            self.playbackEnabled = False
        else:
            self.videoStream.play()
            
            self.playbackEnabled = True


    #sends a request to the server to clsoe the concection. 
    def quit(self):
        
        self.mainSocket.send('quit\n'.encode())
       
        self.mainSocket.close()
        
        print('socket closed')


    #gets the current time stamp in the video stream.
    def getCurrentTimeStamp(self):
       
        return self.videoStream.getTimeStamp()
        
        
    #goes to a specific timestamp  in the video stream
    def goToVideo(self, frameNum):
       
        self.mainSocket.send(f'select\n{self.currentVideo}\n{frameNum}'.encode())

        self.selectVideo(self.currentVideo, frameNum)

        self.videoStream.goTo(frameNum)
           
        self.playbackEnabled = True


    #Sends file path and file contents, gets filename from file path and adds header flag
    def uploadFile(self, filePath):

        if os.path.exists(filePath): 
            file = open(filePath, 'rb')
            
        else:
            raise FileNotFoundError
        
        if '/' in filePath:
            char = '/'
        else: 
            char = '\\'
        
        fileName = 'fn\n' + filePath.split(char)[-1]
        print(fileName)
        
        self.mainSocket.send(fileName.encode())
        
        segmentList = self.encodeFile(file)
        
        time.sleep(0.01)

        for item in segmentList:
            self.mainSocket.send(item)

        print('file sent')
        
        return filePath + ' uploaded'


    #receive exactly size  bytes from socket.
    def recv_exact(self,sock, size):
       
        data = b''
        
        while len(data) < size:
            packet = sock.recv(size - len(data))
           
            if not packet:
               return None
            
            data += packet
        
        return data


    # Receives video frames from the server and inserts them into the the video stream for playback.
    #Stops receiving frames if the video chnages or no data is changed. 
    def receive(self):
        
        originalVideo = self.currentVideo
        
        while self.recvThreadRunning:
            packedSize = self.mainSocket.recv(4)
            
            if not packedSize:
               break
           
            frameSize = struct.unpack('I', packedSize)[0]

            frame = self.recv_exact(self.mainSocket, frameSize)
            
            frameObj = pickle.loads(frame)

            if not frameObj:
               break

            if self.videoStream:
                self.videoStream.insertFrame(frameObj)

            if self.currentVideo != originalVideo:
                self.mainSocket.send('stp'.encode())
                break 
    

    #takes a file object, transforms the file into a list of maximum length 1024 byte data segments, encoded to be sent over a socket
    def encodeFile(self, file):
        
        file.seek(0, os.SEEK_END)
        
        fileLength = file.tell()
        
        file.seek(0)
        
        nSegments = int(fileLength / self.segmentLength) + (fileLength % self.segmentLength > 0)
        
        segments = []
        
        currentSegment = 0
        
        while currentSegment <= nSegments:
            segments.append(file.read(self.segmentLength))
            currentSegment += 1
       
        print('file encoded')
       
        return segments


if __name__ == '__main__':
    client = Client()
