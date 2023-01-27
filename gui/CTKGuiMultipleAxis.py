import matplotlib.pyplot as plt
import customtkinter as tk
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# TODO: make stuff look good
# TODO: get the clicky thing to work (not working on my machine -Z)


tk.set_appearance_mode("dark")


class Application(tk.CTkFrame):
    def __init__(self, master=None):
        tk.CTkFrame.__init__(self, master)
        self.createWidgets()

    def createWidgets(self):
        # fileName = None
        # rawImage = None
        fig = plt.figure(figsize=(6, 4)) #TODO: what size?

        self.ax1 = fig.add_subplot(221)
        self.ax2 = fig.add_subplot(222)
        self.ax3 = fig.add_subplot(223)
        self.ax4 = fig.add_subplot(224)
        self.axes = [self.ax1, self.ax2, self.ax3, self.ax4]

        for i in self.axes:
            i.axis('off')

        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.canvas.draw()

        self.plotButton = tk.CTkButton(master=root, text="Choose Image",command=self.displayImage)
                                      # command=lambda: self.displayImage(canvas, axes))
        self.grayButton = tk.CTkButton(master=root, text="Make Image Gray",command=self.convertGray)
                                      # command=lambda: self.convertGray(canvas, ax2, fig))
        self.colorButton = tk.CTkButton(master=root, text="Add Coloured Pixels",command=self.addColor)
 #                                       command=lambda: self.addColor(canvas, ax3))
        self.saveButton = tk.CTkButton(master=root, text="Save Images", command=lambda: self.saveImage(canvas, fig))
        self.exitButton = tk.CTkButton(root, text="Exit", command=root.destroy)

        self.plotButton.grid(row=0, column=3)
        self.grayButton.grid(row=1, column=3)
        self.colorButton.grid(row=2, column=3)
        self.saveButton.grid(row=3, column=3)
        self.exitButton.grid(row=4, column=3)

    # def displayButtonPress(self,displayImage, *args):
    #     rawImage,fileName = displayImage(*args)
    def displayImage(self):
        for i in self.axes:
            i.clear()
            i.axis('off')
        ax = self.axes[0]

        self.fileName = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
            ('jpg files', '*.jpg'), ('jpeg files', '*.jpeg'), ('all files', '*.*'))) #TODO: initialdir?

        if self.fileName:
            self.rawImage = mpimg.imread(self.fileName)
            #print(self.fileName)
            #print(rawImage)
            ax.imshow(self.rawImage)
            ax.axis('off')
            ax.set_title('Coloured Image')
            self.canvas.draw()
        return #rawImage,fileName

    def saveImage(self, canvas, fig):
        fig.savefig('./image.png')

    def convertGray(self):
        ax = self.ax2
        ax.clear()  # clear axes from previous plot
        # convert to grayscale
        self.grayImage = np.dot(self.rawImage[..., :3], [0.299, 0.587, 0.114])

        # round to integers
        self.grayImage = np.round(self.grayImage).astype(np.uint8)

        # show grayscale image
        ax.imshow(self.grayImage, cmap='gray')
        ax.axis('off')
        ax.set_title('Gray Image')
        self.canvas.draw()

    def addColor(self):
        ax = self.ax3
        ax.clear()  # clear axes from previous plot
        self.grayImage3D = np.stack((self.grayImage,) * 3, axis=-1)
        # plt.imsave('image_gray_3d.jpg', img_gray_3d)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*self.grayImage.shape) < percentage
        self.grayImage3D[mask, :] = self.rawImage[mask, :]

        # save the new image
        self.grayImage3D = np.stack((self.grayImage,) * 3, axis=-1)

        # grid colourization
        I = 100
        J = 100

        xSize, ySize = self.grayImage.shape

        for x in np.linspace(0, xSize, I, dtype=int, endpoint=False):
            for y in np.linspace(0, ySize, J, dtype=int, endpoint=False):
                self.grayImage3D[x, y, :] = self.rawImage[x, y, :]

        ax.imshow(self.grayImage3D)
        ax.axis('off')
        ax.set_title('Image with Some Colour')
        self.canvas.draw()


root = tk.CTk()
app = Application(master=root)
app.mainloop()