from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage

class GUI:

    def __init__(self):
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

        #creating a frame on the root so grid can assign elements to different col/rows
        self.commandFrame = ttk.Frame(root, padding="3 3 12 12")
        self.commandFrame.grid(column=0, row=0, sticky=(N))

        ttk.Button(self.commandFrame, text="List All Videos", command=self.listAvailableVideos).grid(column=0,columnspan=2, row=0, sticky=W)

        ttk.Button(self.commandFrame, text="Select", command=self.selectVideo).grid(column=0, row=3, rowspan=2, sticky=W)
        ttk.Label(self.commandFrame,  text="Select Video").grid(column=1, row=3, sticky=(W, E))
        renameOldFileEntry = ttk.Entry(self.commandFrame, width=30, textvariable=self.videoName)
        renameOldFileEntry.grid(column=2, row=3, sticky=(W, E))


        img=PhotoImage()
        self.photoGrid=ttk.Label(self.commandFrame,image = img).grid(column=1, row=3, sticky=(W, E))
        

        self.consoleLabel=ttk.Label(self.commandFrame, text="console square", font=("Consolas",10), background='Gray')
        self.consoleLabel.grid(column=3, columnspan=2, row=0, rowspan=6, sticky=(S))

        #mainloop is an internal while loop provided by tkinter
        root.mainloop()


    def listAvailableVideos(self):
        pass



    def selectVideo(self):
        pass


    def playPauseButton(self):
        pass

    
    def goBack(self):
        pass


    def goForward(self):
        pass


    def uploadVideo(self):
        pass


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


if __name__ == "__main__":
    main=GUI()
    #MainWindow(ClientTest.fileClient())#debug only, create a mainWindow in client and pass self
