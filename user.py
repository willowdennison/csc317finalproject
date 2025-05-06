from threading import Thread
from server import FileServer
from frame import Frame
import os

class User:

    
    def __init__(self, conn):
        self._conn = conn
        
        self.activeRequest = None
        
        self.userThread = Thread(target = self.recvLoop)
        self.userThread.start()
        
        self.stopQueue = False
    
    #thread for receiving messages, calls handleRequest with the message
    def recvLoop(self):
        while True:
            req = self._conn.recv(1024).decode()
            print(self.handleRequest(req))

    #sends frames to client starting at startFrame, and ending at endFrame
    def sendFrameLoop(self, conn, startFrame, endFrame, videoName):

        path = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'
        
        path = path + char + videoName + char

        FileServer.sendFile(path + 'info.txt', conn)

        currentFrame = startFrame
        self.stopQueue = True
        while not self.stopQueue and currentFrame <= endFrame:
            frame  = Frame(FileServer.getVideoFrame(currentFrame, path + '.mp4'), FileServer.getAudioFrame(currentFrame, path + '.mp3'), currentFrame)
            FileServer.sendFrame(frame, conn)
            currentFrame += 1

    #calls different functions based on what client sends
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
        
        if func == 'fn': #receives video from client
            fileName = req.split('\n')[1]
            FileServer.receiveVideo(conn, fileName)
            return 'File Downloaded'
        
        if func == 'list': #sends the directory to client
            conn.send(FileServer.listDir().encode())
            return 'Directory Sent'
        
        if func == 'quit': #closes the connection
            conn.close()
            return 'Connection Closed'
        
        if func == 'snd':
            conn.send(b'stop')
            return 'Message Sent'