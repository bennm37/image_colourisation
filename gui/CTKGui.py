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
        ax = fig.add_subplot(111)
        plt.axis('off')
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=0,column=1)

        canvas.draw()

        self.plotButton=tk.CTkButton(master=root, text="plot", command=lambda: self.displayImage(canvas,ax,fig))
        self.saveButton=tk.CTkButton(master=root, text="save", command=lambda: self.saveImage(canvas,fig))
        self.exitButton = tk.CTkButton(root, text="Exit", command=root.destroy)
        self.grayButton=tk.CTkButton(master=root, text="gray", command=lambda: self.convertGray(canvas,ax,filename))
        self.colorButton=tk.CTkButton(master=root, text="color", command=lambda: self.addColor(canvas,ax,filename))

        self.plotButton.grid(row=0,column=3)
        self.grayButton.grid(row=1,column=3)
        self.colorButton.grid(row=2,column=3)
        self.saveButton.grid(row=3,column=3)
        self.exitButton.grid(row=4,column=3)

    def displayImage(self,canvas,ax,fig):
        ax.clear()         # clear axes from previous plot
        global filename
        filename = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
        ('jpg files', '*.jpg'), ('jpeg files', '*.jpeg'), ('all files', '*.*')))

        if filename:
            img_arr = mpimg.imread(filename)
            ax.imshow(img_arr)
            plt.axis('off')
            canvas.draw()
    def saveImage(self,canvas,fig):
        fig.savefig('./image.png')

    def convertGray(self,canvas,ax,filename):
        ax.clear()         # clear axes from previous plot
        global img
        img = plt.imread(filename)

        # convert to grayscale
        global img_gray
        img_gray = np.dot(img[..., :3], [0.299, 0.587, 0.114])

        # round to integers
        img_gray = np.round(img_gray).astype(np.uint8)

        # show grayscale image
        ax.imshow(img_gray, cmap='gray')
        plt.axis('off')
        canvas.draw()

    def addColor(self,canvas,ax,filename):
        ax.clear()         # clear axes from previous plot
        img_gray_3d = np.stack((img_gray,)*3, axis=-1)
        #plt.imsave('image_gray_3d.jpg', img_gray_3d)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*img_gray.shape) < percentage
        img_gray_3d[mask, :] = img[mask, :]

        # save the new image
        #plt.imsave('images/image_coloured2.jpg', img_gray_3d)

        img_gray_3d = np.stack((img_gray,)*3, axis=-1)

        # grid colourization
        I = 100
        J = 100

        size_x, size_y = img_gray.shape

        for x in np.linspace(0, size_x, I, dtype=int, endpoint=False):
            for y in np.linspace(0, size_y, J, dtype=int, endpoint=False):
                img_gray_3d[x, y, :] = img[x, y, :]

        #plt.imsave('images/image_coloured_grid.jpg', img_gray_3d)
        ax.imshow(img_gray_3d)
        plt.axis('off')
        canvas.draw()


root=tk.CTk()
app=Application(master=root)
app.mainloop()