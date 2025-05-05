import pickle
from pydub import AudioSegment
from numpy import ndarray

class Frame:
    
    #takes an image from cv2.imread encoded in bytes, a pydub.AudioSegment encoded in bytes, and a frame number
    #stores them in a Frame object to be dumped to a pickle file
    def __init__(self, img:bytes, audio:bytes, frameNum:int):
        
        self.img = img
        self.audio = audio
        self.frameNum = frameNum
        
    
    #returns self encoded as pickle object, in bytes, ready to send
    def dumpToPickle(self):
        
        return pickle.dumps(self)