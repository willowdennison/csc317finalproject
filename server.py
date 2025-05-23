from socket import *
import threading
import os
import cv2
import pickle
import wave
from frame import Frame
from moviepy import VideoFileClip
import struct



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
    def sendFrame(frame:Frame, conn):
            
        data = frame.dumpToPickle()
        message_size = struct.pack('I', len(data))
        conn.send(message_size + data)
    
    
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
                    fileName = fileName.split('.')[0] + '(' + str(num) + ')' + '.mp4'
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
    
    
    #creates an mp3 file in the same folder as the given mp4 file, also calls createInfo
    def createMP3(fileName, directoryName, doPrint = True):
        
        videoPath = directoryName + fileName + '.mp4'
        audioPath = directoryName + fileName + '.wav'

        video = VideoFileClip(videoPath)

        video.audio.write_audiofile(audioPath)
        
        FileServer.createInfo(video, directoryName)
        
        if doPrint:
            print('MP3 File created at: ' + audioPath)

    
    #takes a segmentList, writes it into directoryPath as an mp4 file
    def decodeVideo(segmentList, fileName, directoryPath):
        
        filePath = directoryPath + fileName
        file = open(filePath, 'wb')

        for segment in segmentList:
            file.write(segment)
        
        file.close()
    
    
    #creates user, object called in a thread
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


    #returns the video frame requested
    def getVideoFrame(frameInput, videoPath):

        cap = cv2.VideoCapture(videoPath)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frameInput-1)
        _, frame = cap.read()

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        data = pickle.dumps(buffer)

        return data
    
    
    #returns the audio frames that play during the video frame requested
    def getAudioFrame(frameInput, audioPath, fps):
        
        wf = wave.open(audioPath, 'rb')
        frameRate = wf.getframerate()

        chunk = frameRate / int(float(fps))
        start = frameInput * chunk
        wf.setpos(int(start))
        audioFrame = wf.readframes(int(chunk))
    
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

        #print(f'started frame loop for {videoName}')

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
        self.stopQueue = False
        
        #print('starting to send frames')
        
        while not self.stopQueue and currentFrame <= int(endFrame):
            frame  = Frame(
                FileServer.getVideoFrame(currentFrame, path + videoName + '.mp4'), 
                FileServer.getAudioFrame(currentFrame, path + videoName + '.wav', fps), 
                currentFrame
            )
            
            FileServer.sendFrame(frame, self._conn)
            
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