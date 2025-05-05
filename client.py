from socket import*
#import GUI
import threading
import queue
import time 


class Client:
    def __init__(self):

        self._port = 821

        ip = input("Enter host IP")

        self.mainSocket = socket(AF_INET, SOCK_STREAM)
        print("Socket created")

        self.mainSocket.connect((ip, self._port))
        print("socket connected")

       # self.interface = GUI.MainWindow(self)

        self.recvThread = None
        
        self.recvThreadRunning= False
        
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

            self.activeRequest = videoName
            self.frameQueue = queue.Queue(max=100)
            self.recvThreadRunning = True
            
            self.recvThread = threading.Thread( target = self.receive)
            self.recvThread.start()

    def playPause(self):

        self.playbackEnabled = not self.playbackEnabled
       
        if self.playbackEnabled:
            
            self.videoStream.play()

    
    def quit(self):
        
        self.mainSocket.send('quit\n'.encode())
       
        self.mainSocket.close()
        
        print('socket closed')

    
    def goTo(self, timeStamp, frameRate):
        frameNum = int(timeStamp * frameRate)

        if frameNum in self.videoStream.bufferdFrames():
            self.videoStream.jumpToFrame(frameNum)

        else:
            self.selectVideo(self.currentVideo, frameNum)

            while self.frameQueue.qsize() == 0:
                time.sleep(0.01)

            self.videoStream.jumpToFrame(frameNum)
            self.playbackEnabled = True
