import matplotlib.pyplot as plt
from tkinter.messagebox import showinfo

import customtkinter as ctk
from matplotlib.figure import Figure

import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk  
import numpy as np

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.createWidgets()

    def createWidgets(self):
        fig=plt.figure(figsize=(6,4))
        ax = fig.add_subplot(111)
        plt.axis('off')
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=0,column=1)

        canvas.draw()

        self.displayButton=tk.Button(master=root, text="plot", command=lambda: self.displayImage(canvas,ax,fig))
        self.grayButton=tk.Button(master=root, text="gray", command=lambda: self.convertGray(canvas,ax,filename))
        self.saveButton=tk.Button(master=root, text="save", command=lambda: self.saveImage(canvas,fig))
        self.exitButton = tk.Button(root, text="Exit", command=root.destroy)

        self.displayButton.grid(row=0,column=3)
        self.grayButton.grid(row=1,column=3)
        self.saveButton.grid(row=1,column=3)
        self.exitButton.grid(row=2,column=3)

    def displayImage(self,canvas,ax,fig):
        ax.clear()         # clear axes from previous plot
        global filename
        filename = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
        filename = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
        ('jpg files', '*.jpg'), ('png files', '*.png'), ('all files', '*.*')))

        showinfo(
            title='Selected File',
            message=filename
        )

        if filename:
            img_arr = mpimg.imread(filename)
            ax.imshow(img_arr)
            plt.axis('off')
            canvas.draw()

    def saveImage(self,canvas,fig):
        fig.savefig('./image.png')
    def convertGray(self,canvas,ax,filename):
        print("hello")


root=tk.Tk()
root2 = ctk.CTk()
app=Application(master=root)
app.mainloop()