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
        fig=plt.figure(figsize=(8,8))
        ax=fig.add_axes([0.1,0.1,0.8,0.8])
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=0,column=1)
        canvas.draw()

        self.plotbutton=tk.Button(master=root, text="plot", command=lambda: self.plot(canvas,ax))
        self.plotbutton.grid(row=0,column=0)
        self.exit_button = tk.Button(root, text="Exit", command=root.destroy)
        self.exit_button.grid(row=0,column=1)

    def plot(self,canvas,ax):
        ax.clear()         # clear axes from previous plot
        filenamme = tk.filedialog.askopenfilename(initialdir='/GUI', title='Select A File', filetypes=(
        ('png files', '*.png'), ('jpg files', '*.jpg'), ('all files', '*.*')))
        if filenamme:
            img_arr = mpimg.imread(filenamme)
            ax.imshow(img_arr)
            canvas.draw()


root=tk.Tk()
app=Application(master=root)
app.mainloop()