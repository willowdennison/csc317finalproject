from threading import Thread
import time
from frame import Frame
import GUI
import pyaudio


class VideoStream:
    
    
    #takes the total number of frames in the video, the framerate in frames per second,
    #and the gui object to play video on
    def __init__(self, numFrames:int, fps:int):
        
        self.frameRate = fps
        self.position = 0
        
        #current start and end frame being requested, none meaning end frame
        self.currentRequest = (0, None)
        
        #array for frame images
        print(numFrames)
        self.frames = [None] * int(float(numFrames))
        p = pyaudio.PyAudio()
        self.audioStream = p.open(format=p.get_format_from_width(2), channels=2,rate=44100,output=True,frames_per_buffer=(round(44100/int(fps))))
        
        self.gui = GUI.VideoPlayer(self)
        
        #should the play loop be playing or buffering?
        self.play = False
        self.buffer = True
        
        #to end loop in thread
        self.runThread = True
        
        self.playLoop = Thread(target = self.playLoopThread)
        self.playLoop.start()
        
    
    #run loop to play frames to gui, check if it should be playing or buffering
    def playLoopThread(self):
        
        #time to wait between frames
        waitTime = 1.0 / self.frameRate
        lastFrameTime = time.time()
        
        while self.runThread:
            
            self.checkBuffer()
            
            if self.play and not self.buffer:
                
                self.audioStream.start_stream()
                
                #wait the appropriate time between frames
                if time.time() >= lastFrameTime + waitTime:
                    
                    lastFrameTime = time.time()
                    self.position += 1
                    
                    self.render(self.frames[self.position])
                    
                    self.cleanBuffer()
                    
            else:
                self.audioStream.stop_stream()
                    
    
    #checks if the frame 1 minute ahead of current position is available
    #if its available sets buffer to False, if not sets it to True
    def checkBuffer(self):
        
        framesRemaining = len(self.frames) - self.position
        
        if framesRemaining < self.frameRate:
            checkFrame = framesRemaining
        else:
            checkFrame = self.frameRate
            
        if self.frames[self.position] and self.frames[checkFrame]:
            self.buffer = False
        else:
            self.buffer = True
    
    
    #removes frames more than 1 minute earlier than the current position
    def cleanBuffer(self):
        
        #if 1 minute has passed, remove frame 1 minute ago
        if self.position >= (60 * self.frameRate):
            self.frames[self.position - (60 * self.frameRate)] = None
            
    
    #takes a frame and adds it to the frame list at the index of its frameNum
    def insertFrame(self, frame:Frame):
        self.audioStream.write(frame.audio)
        self.frames[frame.frameNum] = frame.img
    
    
    #renders frame image and audio to self.gui
    def render(self, img:bytes):
        
        if not self.audioStream.is_active:
            self.audioStream.start_stream()
        
        self.gui.showImage(img)
        
    
    #set self.play to true and tell videostream to play on gui
    def play(self):
        self.play = True
        
    
    #set self.play to false and tell videostream to pause on gui
    def pause(self):
        self.play = False
        
    
    #sets self.position to frameNum and starts playing from there
    def goTo(self, frameNum:int, endFrame:int = None):
        self.currentRequest = (frameNum, endFrame)
        self.position = frameNum