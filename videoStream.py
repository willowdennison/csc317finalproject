from threading import Thread
import time
from frame import Frame
import pyaudio
import cv2
from queue import Queue


class VideoStream:
    
    
    #takes the total number of frames in the video, the framerate in frames per second,
    #and the gui object to play video on
    def __init__(self, fps:int):
        
        self.frameRate = int(float(fps))
        self.position = 0
        
        #current start and end frame being requested, none meaning end frame
        self.currentRequest = (0, None)
        
        #array for frame images
        self.frameQueue = Queue()

        p = pyaudio.PyAudio()
        self.audioStream = p.open(format=p.get_format_from_width(2), channels=2,rate=44100,output=True,frames_per_buffer=(round(44100/int(float(fps)))),start = False)
            
        #should the play loop be playing or buffering?
        self.play = True
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
            
            self.checkBuffer()
            
            if self.play and not self.buffer:
                
                #self.audioStream.start_stream()
                
                #wait the appropriate time between frames
                if time.time() >= lastFrameTime + waitTime:
                    
                    lastFrameTime = time.time()
                    self.position += 1
                    
                    killLoop = self.render()

                    if killLoop:
                        #END THE STREAM HERE
                        break
                    
                    
            else:
                pass
                #self.audioStream.stop_stream()
                    
    
    #checks if the frame 5 seconds ahead of current position is available
    #if its available sets buffer to False, if not sets it to True
    def checkBuffer(self):
        checkFrame = self.frameRate * 5
            
        if self.frameQueue.qsize() <= checkFrame:
            self.buffer = False
        elif self.frameQueue.qsize() >= checkFrame * 3:
            self.buffer = True
            
    
    #takes a frame and adds it to the frame list at the index of its frameNum
    def insertFrame(self, frame:Frame):
        self.audioQueue.put(frame.audio)
        self.frameQueue.put(frame.img)
         
    
    #renders frame image and audio to self.gui
    def render(self):
        if self.audioStream.is_active():
            self.audioStream.write(self.audioQueue.get())
        
        img = self.frameQueue.get()
        
        frame=cv2.imdecode(img, cv2.IMREAD_COLOR)
        cv2.imshow("WORK PLEASE", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return True
        return False
        
    
    #set self.play to true and tell videostream to play on gui
    def play(self):
        self.play = True
        
    
    #set self.play to false and tell videostream to pause on gui
    def pause(self):
        self.play = False
        
    
    #sets self.position to frameNum and starts playing from there
    def goTo(self, frameNum:int, endFrame:int = None):
        
        self.audioQueue = Queue()
        self.frameQueue = Queue()
        
        self.currentRequest = (frameNum, endFrame)
        self.position = frameNum