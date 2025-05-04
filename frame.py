import pickle

class Frame:
    
    #takes an image from cv2.imread, a pydub.AudioSegment, and a frame number
    #stores them in a Frame object to be dumped to a pickle file
    def __init__(self, img, audio, frameNum):
        
        self.img = img
        self.audio = audio
        self.frameNum = frameNum
        
    
    #returns self encoded as pickle object, in bytes, ready to send
    def dumpToPickle(self):
        
        return pickle.dumps(self)
        
f = Frame()