import matplotlib.pyplot as plt

import customtkinter as tk


import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

tk.set_appearance_mode("dark")  # Modes: system (default), light, dark
class Application(tk.CTkFrame):
    def __init__(self, master=None):
        tk.CTkFrame.__init__(self,master)
        self.createWidgets()

    def createWidgets(self):
        fig=plt.figure(figsize=(6,4))
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)
        axes = [ax1,ax2,ax3,ax4]
        for i in axes:
            i.axis('off')
        # ax1.axis('off')
        # ax2.axis('off')
        # ax3.axis('off')
        # ax4.axis('off')
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=0,column=1)

        canvas.draw()

        self.plotButton=tk.CTkButton(master=root, text="plot", command=lambda: self.displayImage(canvas,axes))
        self.saveButton=tk.CTkButton(master=root, text="save", command=lambda: self.saveImage(canvas,fig))
        self.exitButton = tk.CTkButton(root, text="Exit", command=root.destroy)
        self.grayButton=tk.CTkButton(master=root, text="gray", command=lambda: self.convertGray(canvas, ax2, fileName))
        self.colorButton=tk.CTkButton(master=root, text="color", command=lambda: self.addColor(canvas, ax3, fileName))

        self.plotButton.grid(row=0,column=3)
        self.grayButton.grid(row=1,column=3)
        self.colorButton.grid(row=2,column=3)
        self.saveButton.grid(row=3,column=3)
        self.exitButton.grid(row=4,column=3)

    def displayImage(self,canvas,axes):
        for i in axes:
            i.clear()
            i.axis('off')
        ax = axes[0]
        #ax.clear()
        #fig.clf()# clear axes from previous plot
        global fileName
        fileName = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
        ('jpg files', '*.jpg'), ('jpeg files', '*.jpeg'), ('all files', '*.*')))
        global rawImage
        if fileName:
            rawImage = mpimg.imread(fileName)
            ax.imshow(rawImage)
            ax.axis('off')
            ax.set_title('Coloured Image')
            canvas.draw()
    def saveImage(self,canvas,fig):
        fig.savefig('./image.png')

    def convertGray(self,canvas,ax,filename):
        ax.clear()         # clear axes from previous plot
        # convert to grayscale
        global grayImage
        grayImage = np.dot(rawImage[..., :3], [0.299, 0.587, 0.114])

        # round to integers
        grayImage = np.round(grayImage).astype(np.uint8)

        # show grayscale image
        ax.imshow(grayImage, cmap='gray')
        ax.axis('off')
        ax.set_title('Gray Image')
        canvas.draw()

    def addColor(self,canvas,ax,filename):
        ax.clear()         # clear axes from previous plot
        grayImage3D = np.stack((grayImage,) * 3, axis=-1)
        #plt.imsave('image_gray_3d.jpg', img_gray_3d)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*grayImage.shape) < percentage
        grayImage3D[mask, :] = rawImage[mask, :]

        # save the new image
        #plt.imsave('images/image_coloured2.jpg', img_gray_3d)

        grayImage3D = np.stack((grayImage,) * 3, axis=-1)

        # grid colourization
        I = 100
        J = 100

        xSize, ySize = grayImage.shape

        for x in np.linspace(0, xSize, I, dtype=int, endpoint=False):
            for y in np.linspace(0, ySize, J, dtype=int, endpoint=False):
                grayImage3D[x, y, :] = rawImage[x, y, :]

        #plt.imsave('images/image_coloured_grid.jpg', img_gray_3d)
        ax.imshow(grayImage3D)
        ax.axis('off')
        ax.set_title('Image with Some Colour')
        canvas.draw()


root=tk.CTk()
app=Application(master=root)
app.mainloop()