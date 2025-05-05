from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage

class GUI:

    def __init__(self, clnt):
        self.client=clnt
        root=Tk()

        root.geometry("1200x500")
        root.title("You2be")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        #sets default window size to 700w x 500h, with a name

        #instantiating all stringvars here, so they can be accessed by labels & functions called by buttons
        self.msgQueueMaxLength=10
        self.msgQueue=[]
        self.videoName = StringVar()
        self.uploadPath = StringVar()

        #creating a frame on the root so grid can assign elements to different col/rows
        self.commandFrame = ttk.Frame(root, padding="3 3 12 12")
        self.commandFrame.grid(column=0, row=0, sticky=(N))

        ttk.Button(self.commandFrame, text="List All Videos", command=self.listAvailableVideos).grid(column=0,columnspan=2, row=0, sticky=W)

        ttk.Button(self.commandFrame, text="Select", command=self.selectVideo).grid(column=0, row=1, sticky=W)
        ttk.Label(self.commandFrame,  text="Select Video").grid(column=1, row=1, sticky=W)
        videoNameEntry = ttk.Entry(self.commandFrame, width=20, textvariable=self.videoName)
        videoNameEntry.grid(column=0,columnspan=2, row=2, sticky=(W, E))

        ttk.Button(self.commandFrame, text="Upload", command=self.uploadVideo).grid(column=0, row=3, sticky=W)
        ttk.Label(self.commandFrame,  text="Upload Video").grid(column=1, row=3, sticky=W)
        uploadEntry = ttk.Entry(self.commandFrame, width=20, textvariable=self.uploadPath)
        uploadEntry.grid(column=0,columnspan=2, row=4, sticky=(W, E))


        img=PhotoImage()
        self.photoGrid=ttk.Label(self.commandFrame, text="video here", width=100).grid(column=2,columnspan=4, row=1,rowspan=4)
        

        self.consoleLabel=ttk.Label(self.commandFrame, text="console square", font=("Consolas",10), background='Gray')
        self.consoleLabel.grid(column=6, columnspan=4, row=1, rowspan=4, sticky=(S))

        #mainloop is an internal while loop provided by tkinter
        root.mainloop()


    def listAvailableVideos(self):
        self.client.listVideo()


    def selectVideo(self):
        self.client.selectVideo(self.videoName, 0)


    def playPauseButton(self):
        self.client.playPause()

    
    def goBack(self):
        self.client.goToVideo(self.client.getCurrentTimestamp()-10)


    def goForward(self):
        self.client.goToVideo(self.client.getCurrentTimestamp()+10)


    def uploadVideo(self):
        self.client.uploadVideo(self.uploadPath)


    def quit(self):
        self.client.quit()


    def setFrame(self, img):
        #img=PhotoImage(file='lajsf.png')
        self.photoGrid.config(image=img)


    #prints messages to a small console in the GUI, basically a convenient print()
    #limited to 5 messages because of window space
    def consoleLog(self,newMsg):
        self.msgQueue.append(newMsg)
        if len(self.msgQueue) > self.msgQueueMaxLength :
            self.msgQueue.pop(0)

        txt=""
        for msg in self.msgQueue:
            txt=  txt + "\n" + msg

        self.consoleLabel.config(text=txt)

