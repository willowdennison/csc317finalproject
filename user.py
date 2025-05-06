from threading import Thread
from server import FileServer
from frame import Frame

class User:

    
    def __init__(self, conn):
        self._conn = conn
        
        self.activeRequest = None
        
        self.userThread = Thread(target = self.recvLoop)
        self.userThread.start()
        
        self.stopQueue = False
    
    
    #loop to recieve messages from client and send them to request handler
    def recvLoop(self):
        while True:
            req = self._conn.recv(1024).decode()
            print(self.handleRequest(req))


    #takes a conn, start
    def sendFrameLoop(self, conn, startFrame, endFrame, filePath):

        currentFrame = startFrame
        self.stopQueue = False
        while not self.stopQueue and currentFrame <= endFrame:
            frame  = Frame(self.getVideoFrame(currentFrame, filePath), self.getAudioFrame(currentFrame, filePath), currentFrame)
            FileServer.sendFrame(frame, conn)
            currentFrame += 1


    def handleRequest(self, req, conn):

        func = req.split('\n')[0]
        
        if func == 'select': #calls after the client wants to send the file starting at the var 'frame' frame
            filePath = req.split('\n')[1]
            startFrame = int(req.split('\n')[2])
            try:
                endFrame = int(req.split('\n')[3])
            except IndexError:
                endFrame = None
            self.sendFrameLoop(conn, startFrame, endFrame, filePath)
            return 'Started playing function at the {frame} frame'
        
        if func == 'stp': #calls after the client wants server to stop sending the file
            self.stopQueue = True
            return 'Stopped sending'
        
        if func == 'fn':
            fileName = req.split('\n')[1]
            FileServer.receiveVideo(conn, fileName)
            return 'File Downloaded'
        
        if func == 'list':
            conn.send(FileServer.listDir().encode())
            return 'Directory Sent'
        
        if func == 'quit':
            conn.close()
            return 'Connection Closed'