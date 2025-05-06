from socket import *
import threading
import os
import cv2
import pickle
import wave
from frame import Frame
from moviepy import VideoFileClip

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

            FileServer.createUserThread(conn)
      
        
    #DOES NOT CHECK FOR FILE PATH MISSING for efficiency, will only be run if we know exactly where each frame is located b/c it will stop 
    #sending files if something goes wrong and crash the client and the thread
    def sendFrame(self, frame, conn):

        segmentList = self.encodeFile(frame)

        for item in segmentList:
            conn.send(item)
    
    
    #sends a file, fileName, to the client, in max length 1024 byte segments
    def sendFile(self, fileName, conn):

        path  = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'

        path = path + char + 'files' + char + fileName

        try:
            file = open(fileName, 'rb')
        
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
    def receiveVideo(conn, fileName, doPrint = True):
        
        path  = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'

        directoryName = path + char + 'files' + char + fileName.split('.')[0]
        
        try:
            os.makedirs(directoryName, exist_ok = False)

        except FileExistsError:

            num = 1
            dirMade = False

            while not dirMade:

                try:
                    os.makedirs(directoryName + '(' + str(num) + ')', exist_ok = False)
                    dirMade = True
                    fileName = fileName.split('.')[0] + '(' + str(num) + ')'
                    directoryName = directoryName + '(' + str(num) + ')'
                    
                except FileExistsError:
                    
                    num += 1

        directoryName = directoryName + char

        segmentList = []

        while True:
            data = conn.recv(1024)
            
            segmentList.append(data)
            if doPrint:
                print(data)

            if len(data) < 1024:
                FileServer.decodeVideo(segmentList, fileName, directoryName)

                if doPrint:
                    print(f'{fileName} received, creating mp3 file')
                    
                FileServer.createMP3(fileName.split('.')[0], directoryName)


                if doPrint:
                    print(f'{fileName} info created')
                return
    
    
    #creates an mp3 file in the same folder as the given mp4 file
    def createMP3(fileName, directoryName, doPrint = True):
        
        print('createMP3')
        
        videoPath = directoryName + fileName + '.mp4'
        audioPath = directoryName + fileName + '.mp3'

        video = VideoFileClip(videoPath)

        video.audio.write_audiofile(audioPath)
        
        FileServer.createInfo(video, directoryName)
        
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
    def decodeVideo(segmentList, fileName, directoryPath):
        filePath = directoryPath + fileName + '.mp4'
        file = open(filePath, 'wb')

        for segment in segmentList:
            file.write(segment)
        
        file.close()
        
        print('end decodeVideo')
    
    
    #calls user
    def createUserThread(conn):
        User(conn)
   
    
    #creates info.txt, containing the fps and the total number of frames in format:
    #fps:___\nframes:___
    def createInfo(video, dirName):

        info = open(dirName + 'info.txt', 'w')
        

        fps = video.fps
        duration = video.duration
        count = round(duration * fps)
        
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
    
    #gets the audio frames that play during the video frame requested
    def getAudioFrame(frameInput, audioPath, fps):
        wf = wave.open(audioPath, 'rb')
        frameRate = wf.getframerate()

        chunk = frameRate / fps
        start = frameInput * chunk
        wf.setpos(start)
        audioFrame = wf.readframes(chunk)
    
        return(audioFrame)
        
        
class User:

    
    def __init__(self, conn):
        self._conn = conn
        
        self.activeRequest = None
        
        self.userThread = threading.Thread(target = self.recvLoop)
        self.userThread.start()
        
        self.stopQueue = False
    
    
    #thread for receiving messages, calls handleRequest with the message
    def recvLoop(self):
        while True:
            req = self._conn.recv(1024).decode()
            response = self.handleRequest(req)
            
            if response:
                print(response)


    #sends frames to client starting at startFrame, and ending at endFrame
    def sendFrameLoop(self, startFrame, endFrame, videoName):

        print(f'started frame loop for {videoName}')

        path = os.getcwd()

        if '/' in path:
            char = '/'
        else:
            char = '\\'
        
        path = path + char + 'files' + char + videoName + char

        info = open(path + 'info.txt')

        infoText = info.read()
        info.close() 
        
        self._conn.send(infoText.encode())

        fps = infoText.split('\n')[0].split(':')[1]
        
        currentFrame = startFrame
        self.stopQueue = True
        while not self.stopQueue and currentFrame <= endFrame:
            frame  = Frame(
                FileServer.getVideoFrame(currentFrame, path + videoName + '.mp4'), 
                FileServer.getAudioFrame(currentFrame, path + videoName + '.mp3', fps), 
                currentFrame
            )
            FileServer.sendFrame(frame, self._conn)
            print(f'frame {currentFrame} sent')
            currentFrame += 1


    #calls different functions based on what client sends
    def handleRequest(self, req, doPrint = True):

        if '/' in os.getcwd():
            char = '/'
        else:
            char = '\\'

        func = req.split('\n')[0]
        
        if func == 'select': #calls after the client wants to send the file starting at the var 'frame' frame
            filePath = req.split('\n')[1]
            startFrame = int(req.split('\n')[2])
            try:
                endFrame = int(req.split('\n')[3])
            except IndexError:
                p = os.getcwd() + char + 'files' + char + filePath + char + 'info.txt'
                info = open(p, 'r')
                endFrame = info.read().split('\n')[1].split(':')[1]
                info.close()
            self.sendFrameLoop(startFrame, endFrame, filePath)
            return f'Started playing function at frame {startFrame}'
        
        if func == 'stp': #calls after the client wants server to stop sending the file
            self.stopQueue = True
            return 'Stopped sending'
        
        if func == 'fn': #receives video from client
            fileName = req.split('\n')[1]
            print(fileName)
            FileServer.receiveVideo(self._conn, fileName, doPrint)
            return 'File Downloaded'
        
        if func == 'list': #sends the directory to client
            self._conn.send(FileServer.listDir().encode())
            return 'Directory Sent'
        
        if func == 'quit': #closes the connection
            self._conn.close()
            return 'Connection Closed'
        
        if func == 'snd':
            self._conn.send('snd received'.encode())
            return 'Message Sent'



if __name__ == '__main__':
    FileServer()