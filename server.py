from socket import *
import threading
import os
import subprocess
from user import User

class FileServer:

    def __init__(self):

        port = 821

        self.mainSocket = socket(AF_INET, SOCK_STREAM)
        print('Socket Connected')

        self.mainSocket.bind('', port)
        print('Socket Bound')

        self.mainSocket.listen(5)

        self.segmentLength = 1024

        connectThread = threading.Thread(Target = self.connect)
        connectThread.start()

    #runs in a thread to constantly connect clients and creates the user thread
    def connect(self):

        while True:

            conn, clientAddress = self.mainSocket.accept()
            print('Connected to: ', clientAddress)

            self.createUserThread(conn)

    #opens the file, if opens for writing, opens without checking if the path exists. Otherwise, if the file does not exist, raises FileNotFoundError
    def openFile(self, fileName, permissions):

        path  = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'

        path = path + char + 'files' + char + fileName #swap files with the folder for where videos are stored

        if 'w' in permissions:
            return open(path, permissions)
        
        if os.path.exists(path):
            return open(path, permissions)
        
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
    def listDir(self):

        dir = os.listdir('files')

        formattedDir = ''

        for item in dir:
            formattedDir = formattedDir + item + '\n'

        return formattedDir
    
    #receives a video in mulitple messages, runs decodeVideo with those messages in a list and then runs createMP3 with the file created from decodeVideo
    def receiveVideo(self, conn, fileName, doPrint = True):
        
        path  = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'

        directoryName = path + char + 'files' + char + fileName.split('.')[0]

        os.makedirs(directoryName, exists_ok = False)

        segmentList = []

        while True:
            data = conn.recv(1024)
            
            segmentList.append(data)

            if len(data) == 0:
                self.decodeVideo(segmentList, fileName, directoryName + char)

                if doPrint:
                    (f'{fileName} received, creating mp3 file')
                self.createMP3(fileName, directoryName)
    
    #creates an mp3 file in the same folder as the given mp4 file
    def createMP3(self, fileName, directoryName, doPrint = True):
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
        filePath = directoryPath + fileName + '.mp4'
        file = self.openFile(filePath, 'wb')

        for segment in segmentList:
            file.write(segment)
        
        file.close()
    
    #calls user
    def createUserThread(self, conn):
        user = User(conn)
