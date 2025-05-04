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
    
    
    def sendLoop(self):
        while True:
            if self.sendQueue[0]:
                self._conn.send(self.sendQueue.pop().encode())
    
    
    def recvLoop(self):
        while True:
            req = self._conn.recv(1024).decode()
            response = self._server.handleRequest(req)
            if response: 
                self.sendQueue.put(response)