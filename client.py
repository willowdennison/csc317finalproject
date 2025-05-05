from socket import*
import GUI
import threading
import queue
import time 
import os 
from videoStream import VideoStream



class Client:
    def __init__(self):
        self.gui = GUI.GUI(self)# needs to be moved below the connection logic, but after everything is debugged
        self._port = 821
        self.segmentLength = 1024 

        ip = input("Enter host IP")

        self.mainSocket = socket(AF_INET, SOCK_STREAM)
        print("Socket created")

        self.mainSocket.connect((ip, self._port))
        print("socket connected")

        self.interface = GUI.MainWindow(self)

        self.recvThread = None
        
        self.recvThreadRunning = False
        
        self.frameQueue = queue.Queue(maxsize=100)  
       
        self.activeRequest = None
       
        self.playbackEnabled = False
        
        self.videoStream = None
       
        self.currentVideo = None



     # sends a list command to the server and receives a list of available videos,recieves the list of vidoes and returns it as a strign 
    def listVideo (self):
        
         self.mainSocket.send('list\n'.encode())

         data = self.mainSocket.recv(1024).decode() 

         dirList = 'Vidoes avaiable on server:\n' + data
         
         return dirList


   # 
    def selectVideo(self, videoName, startFrame , endFrame=None):

        if self.recvThread is not None and self.recvThread.is_alive():
           
            self.recvThreadRunning = False 
            self.recvThread.join()

            msg = f"select\n{videoName}\n{startFrame}"
            if endFrame is not None:
                  msg += f"\n{endFrame}"
            self.mainSocket.send(msg.encode())

            info = self.mainSocket.recv(1024).decode()
            
            self.activeRequest = videoName
            self.frameQueue = queue.Queue(maxsize=100)
            self.recvThreadRunning = True
            
            #change to however this actually gets value from info
            self.videoStream = VideoStream(info['numFrames'], info['frameRate'], self.gui)
            
            if startFrame > 0 or endFrame:
                self.videoStream.currentRequest = (startFrame, endFrame)
            
            self.recvThread = threading.Thread( target = self.receive)
            self.recvThread.start()
   
    # plays and pauses the video stream
    def playPause(self):

        self.playbackEnabled = not self.playbackEnabled
       
        if self.playbackEnabled:
            
            self.videoStream.play()

     #sends a request to the server to pause the video stream
    def quit(self):
        
        self.mainSocket.send('quit\n'.encode())
       
        self.mainSocket.close()
        
        print('socket closed')

    def getCurrentTimeStamp(self):
        timeStamp = time.time()
        print('Current time stamp:', timeStamp)
        return timeStamp

        
        
        
    #goes to a specific time in the video stream
    def goToVideo(self, timeStamp , frameRate):
       
        frameNum = int(timeStamp * frameRate) # time stamp is in seconds
        
        if self.videoStream.frames[frameNum] is not None:
         
         self.videoStream.goTo(frameNum)

        else:
            self.selectVideo(self.currentVideo, frameNum)

            while self.frameQueue.qsize() == 0:
                time.sleep(0.01)

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
        
        self.mainSocket.send(fileName.encode())
        
        segmentList = self.encodeFile(file)
        
        time.sleep(0.01)

        for item in segmentList:
            self.mainSocket.send(item) 
            print(item)
    
        return filePath + ' uploaded'
    

    def recieve(self):
        while self.recvThreadRunning:

            frameObj = self.mainSocket.recv(1024)
            if not frameObj:
                break
            if not self.frameQueue.full():
                self.frameQueue.put(frameObj)
            else:
                self.mainSocket.send('Pause Video\n'.encode())

            if self.videoStream:
                self.videoStream.insertFrame(frameObj)

            while  self.videoStream.currentFrame  > 20 and not self.frameQueue.empty():
                self.frameQueue.get()

            if self.activeRequest != self.currentVideo:
                break 
    

    # takes a file object, transforms the file into a list of maximum length 1024 byte data segments, encoded to be sent over a socket
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
            
        return segments
    
    #decodes a segmentList from downloadFile() and saves it to fileName
    def decodeFile(self, segmentList, fileName):
        
        print(segmentList)
    
        filePath = os.getcwd()
        
        #check for file separator character and use the proper one
        if '\\' in filePath:
            char = '\\'
        else:
            char = '/'
        
        filePath = filePath + char + 'files' + char + fileName

        file = open(filePath, 'wb')
        
        for segment in segmentList:
            file.write(segment)
            
        file.close()
        
        file = open(filePath, 'rb')
        
        file.close()

if __name__ == "__main__":
    client = Client()