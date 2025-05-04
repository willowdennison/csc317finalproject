import cv2
import pickle

class Frame:
    
    #takes an image from cv2.imread, a pydub.AudioSegment, and a frame number
    #stores them in a Frame object to be dumped to a pickle file
    def __init__(self, img, audio, frameNum):
        
        self.img = img
        self.audio = audio
        self.frameNum = frameNum
        
    
    #saves frame object to pickle file at the given directory
    def dumpToPickle(self, dirPath):
        
        if '/' in dirPath:
            char = '/'
        else:
            char = '\\'
        
        filePath = dirPath + char + f'frame{self.frameNum}.pkl'
        pkl = open(filePath, 'wb')
        pickle.dump(self, pkl)
        
        pkl.close()
        
f = Frame()