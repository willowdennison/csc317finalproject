from threading import Thread
from queue import Queue
from server import FileServer
from frame import Frame

class User:
    
    def __init__(self, conn, server:FileServer):
        self._conn = conn
        self._server = server
        
        self.activeRequest = None
        self.sendQueue = Queue()
        
        self.sendThread = Thread(target = self.sendLoop)
        self.sendThread.start()
        
        self.recvThread = Thread(target = self.recvLoop)
        self.recvThread.start()
        
        self.stopQueue = False
    
    
    #i dont know if this will work for sending video frames unless we straight up add them to the queue
    def sendLoop(self):
        while True:
            if not self.sendQueue.empty():
                self._conn.send(self.sendQueue.pop().encode())
    
    
    def recvLoop(self):
        while True:
            req = self._conn.recv(1024).decode()
            response = self.handleRequest(req)
            
            #if response is a video request with frames
                #self.activeRequest = (startFrame, endFrame)
            
            if response: 
                self.sendQueue.put(response)

    def sendFrameLoop(self, conn, startFrame, endFrame, filePath):

        currentFrame = startFrame
        self.stopQueue = True
        while not self.stopQueue and currentFrame <= endFrame:
            frame  = Frame(self.getVideoFrame(currentFrame, filePath), self.getAudioFrame(currentFrame, filePath), currentFrame)
            FileServer.sendFrame(self, frame, conn)
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
            self.sendFrameLoop(self, conn, startFrame, endFrame, filePath)
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