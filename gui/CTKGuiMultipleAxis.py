import matplotlib.pyplot as plt
import customtkinter as tk
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# TODO: make stuff look good
# TODO: get the clicky thing to work (not working on my machine -Z)

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
        self.saveButton = tk.CTkButton(master=root, text="Save Images", command=lambda: self.saveImage(canvas, fig))
        self.exitButton = tk.CTkButton(root, text="Exit", command=root.destroy)

        self.plotButton.grid(row=0, column=3)
        self.grayButton.grid(row=1, column=3)
        self.colorButton.grid(row=2, column=3)
        self.saveButton.grid(row=3, column=3)
        self.exitButton.grid(row=4, column=3)

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
        return 

    def saveImage(self, canvas, fig): #TODO: fix this
        fig.savefig('./image.png')

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

    # add some colour to the grayscale image
    def addColor(self):
        ax = self.ax3
        grayImage = self.grayImage
        rawImage = self.rawImage

        ax.clear()  

        # made 3-dim grid array to hold RGb
        grayImage3D = np.stack((grayImage,) * 3, axis=-1)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*grayImage.shape) < percentage
        grayImage3D[mask, :] = rawImage[mask, :]

        grayImage3D = np.stack((grayImage,) * 3, axis=-1)

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



if __name__=="__main__":
    root = tk.CTk()
    app = Application(master=root)

    # run
    app.mainloop()
