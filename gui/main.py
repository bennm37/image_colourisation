import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import customtkinter as tk
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

# TODO: make stuff look good

# dark theme
tk.set_appearance_mode("dark")



class Application(tk.CTkFrame):
    # work in OOP
    def __init__(self, master=None):
        tk.CTkFrame.__init__(self, master)
        self.createWidgets()

    def createWidgets(self):
        fig = plt.figure(figsize=(6, 4)) #TODO: what size?
        self.ax1 = fig.add_subplot(221)
        self.ax2 = fig.add_subplot(222)
        self.ax3 = fig.add_subplot(223)
        self.ax4 = fig.add_subplot(224)
        self.axes = [self.ax1, self.ax2, self.ax3, self.ax4]

        for i in self.axes:
            i.axis('off')

        # define the canvas upon which we place the images
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.canvas.draw()




        # define the buttons
        self.plotButton = tk.CTkButton(master=root, text="Choose Image",command=self.displayImage)
        self.grayButton = tk.CTkButton(master=root, text="Make Image Gray",command=self.convertGray)
        self.colorButton = tk.CTkButton(master=root, text="Add Coloured Pixels",command=self.addColor)
        self.manuallyColourButton = tk.CTkButton(master=root, text="Manually Colour", command=self.popupWindow)
        self.saveButton = tk.CTkButton(root, text="Save", command=self.savePicture)
        self.exitButton = tk.CTkButton(root, text="Exit", command=root.destroy)
        # draw_stuff = DrawStuff(self,self.filepath)
        # self.button1 = tk.CTkButton(master=root,text="draw line", command=draw_stuff.draw_line)

        self.plotButton.grid(row=0, column=3)
        self.grayButton.grid(row=1, column=3)
        self.colorButton.grid(row=2, column=3)
        self.manuallyColourButton.grid(row=3, column=3)
        self.saveButton.grid(row=4, column=3)
        self.exitButton.grid(row=5, column=3)
        # self.button1.grid(row=5,column=3)

    # select an image and show it
    def displayImage(self):
        # clear all axes; new image to be loaded
        for i in self.axes:
            i.clear()
            i.axis('off')
        ax = self.axes[0]

        # load file
        fileName = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
            ('jpg files', '*.jpg'), ('jpeg files', '*.jpeg'), ('all files', '*.*'))) #TODO: initialdir?
        
        # save file name to be referenced
        self.fileName = fileName

        if fileName:
            rawImage = mpimg.imread(fileName)
            self.rawImage = rawImage
            ax.imshow(rawImage)
            ax.axis('off')
            ax.set_title('Coloured Image')
            self.canvas.draw()
        return self.fileName

    def savePicture(self):
        self.canvas.figure.savefig('./image.png')

    # convert image to grayscale
    def convertGray(self):
        ax = self.ax2
        ax.clear()  

        # convert to grayscale
        grayImage = np.dot(self.rawImage[..., :3], [0.299, 0.587, 0.114])

        # round to integers
        grayImage = np.round(grayImage).astype(np.uint8)

        # show grayscale image
        ax.imshow(grayImage, cmap='gray')
        ax.axis('off')
        ax.set_title('Gray Image')
        self.canvas.draw()
        self.grayImage = grayImage

    def dimensionalise(self,rawImage,grayImage):
        grayImage3D = np.stack((grayImage,) * 3, axis=-1)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*grayImage.shape) < percentage
        grayImage3D[mask, :] = rawImage[mask, :]

        grayImage3D = np.stack((grayImage,) * 3, axis=-1)
        return grayImage3D

    # add some colour to the grayscale image
    def addColor(self):
        ax = self.ax3
        grayImage = self.grayImage
        rawImage = self.rawImage

        ax.clear()
        grayImage3D = self.dimensionalise(rawImage,grayImage)

        # grid colourization
        I = 100
        J = 100

        xSize, ySize = grayImage.shape

        for x in np.linspace(0, xSize, I, dtype=int, endpoint=False):
            for y in np.linspace(0, ySize, J, dtype=int, endpoint=False):
                grayImage3D[x, y, :] = self.rawImage[x, y, :]

        self.grayImage3D = grayImage3D
        ax.imshow(grayImage3D)
        ax.axis('off')
        ax.set_title('Image with Some Colour')
        self.canvas.draw()

    def popupWindow(self):
        popup = tk.CTkToplevel(self)
        fig2 = plt.figure(figsize=(6, 4)) #TODO: what size?
        popup.ax = fig2.add_subplot(111)
        popup.ax.axis('off')
        popupCanvas = FigureCanvasTkAgg(fig2,master=popup)

        popupCanvas.get_tk_widget().grid(row=0, column=1)
        popupCanvas.draw()

        gs = GridSpec(2, 3)
        popup.ax01 = fig2.add_subplot(gs[0:2, 0:2])
        popup.ax11 = fig2.add_subplot(gs[0, 2])
        popup.ax21 = fig2.add_subplot(gs[1, 2])
        manualImage = self.dimensionalise(self.rawImage,self.grayImage)
        # img = np.array(plt.imread(self.grayImage))
        colourWheel = plt.imread("images/color_wheel.jpeg")
        selectedColour = np.ones([2, 2, 3]) * 0
        popup.ax01.imshow(manualImage)
        popup.ax11.imshow(colourWheel)
        popup.ax01.axis('off')
        popup.ax11.axis('off')
        popup.ax21.axis('off')
        popup.ax21.imshow(selectedColour)
        nx, ny, d = manualImage.shape
        sc = [0, 0, 0]
        def onclick(event):
            global sc
            print("clicked")
            if event.inaxes==popup.ax01:
                x,y = event.xdata,event.ydata
                x,y = np.round(x).astype(int),np.round(y).astype(int)
                manualImage[y:y+5,x:x+5,:] = sc
                popup.ax01.clear()
                popup.ax01.imshow(manualImage)
                self.ax4.imshow(manualImage)
                popup.ax01.axis('off')
            if event.inaxes == popup.ax11:
                x,y = event.xdata,event.ydata
                x,y = np.round(x).astype(int),np.round(y).astype(int)
                sc = colourWheel[y,x]
                print("selected color is ", sc)
                selected_color = np.tile(sc,(2,2,1))
                popup.ax21.imshow(selected_color)
                popup.ax21.axis('off')
                print(selected_color.shape)
            fig2.canvas.draw_idle()

        cid = fig2.canvas.mpl_connect('button_press_event', onclick)

        self.ax4.set_title('Image with Manual Colour')
        popupCloseButton = tk.CTkButton(popup, text="Close Window", command=popup.destroy)
        saveImageButton = tk.CTkButton(popup, text="Write to Main", command=self.saveImage)

        popupCloseButton.grid(row=1, column=0)
        saveImageButton.grid(row=2, column=0)

    def saveImage(self):
        self.canvas.draw()

if __name__=="__main__":
    root = tk.CTk()
    app = Application(master=root)
    app.mainloop()
