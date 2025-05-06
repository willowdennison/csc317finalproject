from socket import *
import threading
import os
import subprocess
import cv2
import pickle
from frame import Frame

class FileServer:


    def __init__(self):

        port = 821

        self.mainSocket = socket(AF_INET, SOCK_STREAM)
        print('Socket Connected')

        self.mainSocket.bind(('', port))
        print('Socket Bound')

        self.mainSocket.listen(5)

        self.segmentLength = 1024

        connectThread = threading.Thread(target = self.connect)
        connectThread.start()


    #runs in a thread to constantly connect clients and creates the user thread
    def connect(self):

        while True:

            conn, clientAddress = self.mainSocket.accept()
            print('Connected to: ', clientAddress)

            self.createUserThread(conn)


    #opens the file, if opens for writing, opens without checking if the path exists. Otherwise, if the file does not exist, raises FileNotFoundError
    def openFile(fileName, permissions):

        # path  = os.getcwd()

        # if '/' in path:
        #     char = '/'
        # else:
        #     char = '\\'

        # path = path + char + 'files' + char + fileName #swap files with the folder for where videos are stored

        if 'w' in permissions:
            return open(fileName, permissions)
        
        if os.path.exists(fileName):
            return open(fileName, permissions)
        
        else:
            raise(FileNotFoundError)
      
        
    #DOES NOT CHECK FOR FILE PATH MISSING for efficiency, will only be run if we know exactly where each frame is located b/c it will stop 
    #sending files if something goes wrong and crash the client and the thread
    def sendFrame(self, frame, conn):

        segmentList = self.encodeFile(frame)

        for item in segmentList:
            conn.send(item)
    
    
    #sends a file, fileName, to the client, in max length 1024 byte segments
    def sendFile(self, fileName, conn):
        
        try:
            file = self.openFile(fileName, 'rb')
        
        except FileNotFoundError:
            conn.send('Error 404: File not found'.encode())
            return
        
        segmentList = self.encodeFile(file)
        
        for item in segmentList:
            conn.send(item)
    
    
    #gives a list of the names of the files/directories in the folder
    def listDir():

        dir = os.listdir('files')

        formattedDir = ''

        for item in dir:
            formattedDir = formattedDir + item + '\n'

        return formattedDir
    
    
    #receives a video in mulitple messages, runs decodeVideo with those messages in a list and then runs createMP3 with the file created from decodeVideo
    def receiveVideo(self, conn, fileName, doPrint = True):
        
        print(fileName)
        
        path  = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'

        directoryName = path + char + 'files' + char + fileName.split('.')[0]

        try:
            os.makedirs(directoryName, exist_ok = False)
        
        except:
            pass

        segmentList = []

        while True:
            data = conn.recv(1024)
            
            segmentList.append(data)

            if len(data) < 1024:
                self.decodeVideo(segmentList, fileName, directoryName + char)

                if doPrint:
                    print(f'{fileName} received, creating mp3 file')
                self.createMP3(fileName, directoryName)

                self.createInfo(fileName, directoryName)
                if doPrint:
                    print(f'{fileName} info created')
                    
                return


    #creates an mp3 file in the same folder as the given mp4 file
    def createMP3(fileName, directoryName, doPrint = True):
        print(fileName)
        videoPath = directoryName + fileName + '.mp4'
        audioPath = directoryName + fileName + '.mp3'

        command = "ffmpeg -i {} -vn -ar 44100 -ac 1 -b:a 192k {}".format(videoPath, audioPath)

        subprocess.call(command, shell=True)
        
        if doPrint:
            print("MP3 File created at: " + audioPath)


    #gets a file ready for sending by splitting the message into multiple messages, returns a list of byte-wise strings
    def encodeFile(self, file):
        file.seek(0, os.SEEK_END)

        fileLength = file.tell()

        file.seek(0)

        nSegments = int(fileLength / self.segmentLength) + (fileLength % self.segmentLength > 0)

        segments = []
        
        for _ in range(nSegments):

            segments.append(file.read(self.segmentLength))
        
        return segments
    
    
    #takes a segmentList, writes it into directoryPath as an mp4 file
    def decodeVideo(self, segmentList, fileName, directoryPath):
        filePath = directoryPath + fileName
        file = FileServer.openFile(filePath, 'wb')

        for segment in segmentList:
            file.write(segment)
        
        file.close()
    
    
    #calls user
    def createUserThread(self, conn):
        User(conn, self)
    
    
    #uses frameRate and frameNumber to get the time stamp in milliseconds
    def getTimeStamp(frameRate, frameNumber):
        seconds = frameNumber / frameRate
        return seconds * 1000
    
    
    #creates info.txt, containing the fps and the total number of frames in format:
    #fps:___\nframes:___
    def createInfo(fileName, dirName):

        info = open(dirName + 'info.txt', 'w')
        
        cap = cv2.VideoCapture(dirName + fileName)
        fps = cap.get(cv2.CAP_PROP_FPS)
        count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        info.write(f'fps:{fps}\nframes:{count}')
        info.close()


    def getVideoFrame(frameInput, videoPath):

        cap = cv2.VideoCapture(videoPath)

        print(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        cap.set(cv2.CAP_PROP_POS_FRAMES, frameInput-1)
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        data = pickle.dumps(buffer)

        return data
    
    
class User:

    
    def __init__(self, conn, server):
        self._conn = conn
        self.server = server
        
        self.activeRequest = None
        
        self.userThread = threading.Thread(target = self.recvLoop, args=(conn,))
        self.userThread.start()
        
        self.stopQueue = False
    
    #thread for receiving messages, calls handleRequest with the message
    def recvLoop(self, conn):
        while True:
            req = self._conn.recv(1024).decode()
            print(self.handleRequest(req, conn))

    #sends frames to client starting at startFrame, and ending at endFrame
    def sendFrameLoop(self, conn, startFrame, endFrame, videoName):

        path = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'
        
        path = path + char + videoName + char

        self.server.sendFile(path + 'info.txt', conn)

        currentFrame = startFrame
        self.stopQueue = True
        while not self.stopQueue and currentFrame <= endFrame:
            frame  = Frame(self.server.getVideoFrame(currentFrame, path + '.mp4'), self.server.getAudioFrame(currentFrame, path + '.mp3'), currentFrame)
            self.server.sendFrame(frame, conn)
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
            self.server.receiveVideo(conn, fileName)
            return 'File Downloaded'
        
        if func == 'list': #sends the directory to client
            conn.send(FileServer.listDir().encode())
            return 'Directory Sent'
        
        if func == 'quit': #closes the connection
            conn.close()
            return 'Connection Closed' 


    
if __name__ == '__main__':
    FileServer()