import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import threading

class GUI:

    def __init__(self, clnt):
        self.client = clnt
        root = Tk()

        #sets default window size and name
        root.geometry("1200x500")
        root.title("You2be")


        #instantiating all stringvars here, so they can be accessed by labels & functions called by buttons
        self.msgQueueMaxLength = 10
        self.msgQueue = []
        self.videoName = StringVar()
        self.uploadPath = StringVar()

        #creating a frame on the root so grid can assign elements to different col/rows
        self.commandFrame = ttk.Frame(root, padding = "3 3 12 12")
        self.commandFrame.grid(column = 0, row = 0)

        #creating and placing all buttons, inputs, the image and the debugging console
        ttk.Button(self.commandFrame, text = "List All Videos", command = self.listAvailableVideos).grid(column = 0,columnspan = 2, row = 0, sticky = W)

        ttk.Button(self.commandFrame, text = "Select", command = self.selectVideo).grid(column = 0, row = 1, sticky = W)
        ttk.Label(self.commandFrame, text = "Select Video").grid(column = 1, row = 1, sticky = W)
        videoNameEntry = ttk.Entry(self.commandFrame, width = 20, textvariable = self.videoName)
        videoNameEntry.grid(column = 0, columnspan = 2, row = 2, sticky = (W, E))

        ttk.Button(self.commandFrame, text = "Upload", command = self.uploadVideo).grid(column = 0, row = 3, sticky = W)
        ttk.Label(self.commandFrame, text = "Upload Video").grid(column = 1, row = 3, sticky = W)
        uploadEntry = ttk.Entry(self.commandFrame, width = 20, textvariable = self.uploadPath)
        uploadEntry.grid(column = 0, columnspan = 2, row = 4, sticky = (W, E))

        #image1 = Image.open("sun.png")
        #test = ImageTk.PhotoImage(image1)
        self.mainImage = tkinter.Label()#image = test)
        self.mainImage.grid(column = 0, columnspan = 4, row = 0, rowspan = 4, sticky = (N))

        ttk.Button(self.commandFrame, text = "<- 10s", command = self.goBackward).grid(column = 2, row = 5, sticky = E)
        ttk.Button(self.commandFrame, text = "Play/Pause", command = self.playPauseButton).grid(column = 3, row = 5)
        ttk.Button(self.commandFrame, text = "10s ->", command = self.goForward).grid(column = 4, row = 5, sticky = W)


        self.consoleLabel = ttk.Label(self.commandFrame, text = "console square", font = ("Consolas",10), background = 'Gray')
        self.consoleLabel.grid(column = 6, columnspan = 4, row = 1, rowspan = 4, sticky = (S))

        #mainloop is an internal while loop provided by tkinter
        guiThread = threading.Thread(target = root.mainloop)
        guiThread.start()


    #calls the client's function to get all available videos
    def listAvailableVideos(self):
        self.consoleLog(self.client.listVideo())


    #calls the client's function to start streaming a video
    def selectVideo(self):
        self.consoleLog("Trying to play " + self.videoName.get())
        self.client.selectVideo(self.videoName.get(), 0)


    #calls the client's function to pause current video
    def playPauseButton(self):
        self.consoleLog("Tried to Play/Pause")
        self.client.playPause()


    #calls the client's function to move playback frame backwards by 10 seconds(frames*fps)
    def goBackward(self):
        self.consoleLog("Tried backward 10")
        self.client.goToVideo(self.client.getCurrentTimestamp() - 10)


    #calls the client's function to move playback frame forwards by 10 seconds(frames*fps)
    def goForward(self):
        self.consoleLog("Tried forward 10")
        self.client.goToVideo(self.client.getCurrentTimestamp() + 10)


    #calls client function to upload a video from a given path
    def uploadVideo(self):
        self.consoleLog(self.client.uploadFile(self.uploadPath.get()))


    #calls client function to stop the program, release RAM, etc
    def quit(self):
        self.client.quit()


    #available for client to call to make video appear in GUI
    def showImage(self, img):
        self.mainImage.config(image = img)


    #prints messages to a small console in the GUI, basically a convenient print()
    #limit on messages because of window space
    def consoleLog(self, newMsg):
        self.msgQueue.append(newMsg)
        if len(self.msgQueue) > self.msgQueueMaxLength :
            self.msgQueue.pop(0)

        txt = ""
        for msg in self.msgQueue:
            txt = txt + "\n" + msg

        self.consoleLabel.config(text = txt)

