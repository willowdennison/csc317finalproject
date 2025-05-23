from threading import Thread
import time
from frame import Frame
import pyaudio
import cv2
from queue import Queue


class VideoStream:
    
    
    #takes the total number of frames in the video, the framerate in frames per second,
    #and the gui object to play video on
    def __init__(self, fps:int, position):
        
        self.frameRate = int(float(fps))
        self.position = position
        
        #current start and end frame being requested, none meaning end frame
        self.currentRequest = (0, None)
        
        #array for frame images
        self.frameQueue = Queue()

        p = pyaudio.PyAudio()
        self.audioStream = p.open(format = p.get_format_from_width(2), channels=2, rate=44100, output=True, frames_per_buffer = (round(44100/int(float(fps)))), start = False)
            
        #should the play loop be playing or buffering?
        self.playVideo = True
        self.buffer = True
        
        #to end loop in thread
        self.runThread = True
        
        self.playLoop = Thread(target = self.playLoopThread)
        self.playLoop.start()
        self.audioQueue = Queue()
        
    
    #run loop to play frames to gui, check if it should be playing or buffering
    def playLoopThread(self):
        
        self.audioStream.start_stream()

        #time to wait between frames
        waitTime = 1.0 / self.frameRate
        lastFrameTime = time.time()
        
        while self.runThread:
                        
            if self.playVideo:
                
                #wait the appropriate time between frames
                if time.time() >= lastFrameTime + waitTime:
                    
                    lastFrameTime = time.time()
                    
                    killLoop = self.render()

                    if killLoop:
                        #END THE STREAM HERE
                        break
                    
    
    #takes a frame and adds it to the frame list at the index of its frameNum
    def insertFrame(self, frame:Frame):
        
        self.audioQueue.put(frame.audio)
        self.frameQueue.put(frame.img)
         
    
    #renders frame image and audio to self.gui
    def render(self):
        
        checkFrame = self.frameRate * 2

        if self.frameQueue.qsize() <= checkFrame:
            self.buffer = True
            print('buffering...')
            
        elif self.frameQueue.qsize() >= checkFrame * 3:
            self.buffer = False

        if not self.buffer:
            if self.audioStream.is_active():
                self.audioStream.write(self.audioQueue.get())
            
            img = self.frameQueue.get()
            
            frame=cv2.imdecode(img, cv2.IMREAD_COLOR)
            cv2.imshow('WORK PLEASE', frame)

            self.position += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                return True
            
        return False
        
    
    #set self.play to true and tell videostream to play on gui
    def play(self):
        self.playVideo = True
        
    
    #set self.play to false and tell videostream to pause on gui
    def pause(self):
        self.playVideo = False
        
    
    #sets self.position to frameNum and starts playing from there
    def goTo(self, frameNum:int, endFrame:int = None):
        
        self.audioQueue = Queue()
        self.frameQueue = Queue()
        
        self.currentRequest = (frameNum, endFrame)
        self.position = frameNum
    
    
    #gets the current time stamp
    def getTimeStamp(self):
        return self.position / self.frameRate
