from threading import Thread
from queue import Queue
from server import FileServer

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
        
        self.stopQueue = True
    
    
    #i dont know if this will work for sending video frames unless we straight up add them to the queue
    def sendLoop(self):
        while True:
            if not self.sendQueue.empty():
                self._conn.send(self.sendQueue.pop().encode())
    
    
    def recvLoop(self):
        while True:
            req = self._conn.recv(1024).decode()
            response = self._server.handleRequest(req)
            
            #if response is a video request with frames
                #self.activeRequest = (startFrame, endFrame)
            
            if response: 
                self.sendQueue.put(response)

    def sendFrameLoop(self, conn, startFrame, endFrame):
        currentFrame = startFrame
        while not self.stopQueue and currentFrame <= endFrame:
            
            pass