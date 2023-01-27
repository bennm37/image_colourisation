import matplotlib.pyplot as plt
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
#        ax=fig.add_axes([0.1,0.1,0.8,0.8])
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=0,column=1)
        #canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
        #canvas.get_tk_widget().pack(side="top", fill="x", expand=0)
        #canvas._tkcanvas.pack(side="top", fill="x", expand=0)

        canvas.draw()

        self.plotButton=tk.Button(master=root, text="plot", command=lambda: self.displayImage(canvas,ax,fig))
        self.saveButton=tk.Button(master=root, text="save", command=lambda: self.saveImage(canvas,fig))
        self.exitButton = tk.Button(root, text="Exit", command=root.destroy)

        #self.plotbutton.pack(expand=True)
        #self.exit_button.pack(expand=True)

        self.plotButton.grid(row=0,column=3)
        self.saveButton.grid(row=2,column=3)
        self.exitButton.grid(row=3,column=3)

    def displayImage(self,canvas,ax,fig):
        ax.clear()         # clear axes from previous plot
        filenamme = tk.filedialog.askopenfilename(initialdir='../images/', title='Select A File', filetypes=(
        ('jpg files', '*.jpg'), ('png files', '*.png'), ('all files', '*.*')))
        if filenamme:
            img_arr = mpimg.imread(filenamme)
            ax.imshow(img_arr)
            plt.axis('off')
            canvas.draw()
    def saveImage(self,canvas,fig):
        fig.savefig('./image.png')



root=tk.Tk()
app=Application(master=root)
app.mainloop()