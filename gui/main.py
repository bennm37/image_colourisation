import tkinter as tk
from PIL import Image,ImageTk
from tkinter import filedialog
from scipy import ndimage
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter.messagebox import showinfo
from numpy import array, arange, sin, pi

root = tk.Tk()
root_panel = tk.Frame(root)
root_panel.pack(side="bottom", fill="both", expand="yes")

btn_panel = tk.Frame(root_panel, height=35)
btn_panel.pack(side='top', fill="both", expand="yes")
def showw(filename):
    img_arr = mpimg.imread(filename)
    imgplot = plt.imshow(img_arr)

    f = Figure()
    a = f.add_subplot(111)
    global im
    im = a.imshow(img_arr)
    global canvas
    canvas = FigureCanvasTkAgg(f, master=root)
    #canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
    canvas._tkcanvas.pack(side="top", fill="both", expand=1)
    canvas.get_tk_widget().delete("all")
#filename = fd.askopenfilename()



def open():
    filenamme = tk.filedialog.askopenfilename(initialdir='/GUI', title='Select A File', filetypes=(
    ('jpg files', '*.jpg'), ('png files', '*.png'), ('all files', '*.*')))
    if filenamme:
        img_arr = mpimg.imread(filenamme)
#        imgplot = plt.imshow(img_arr)
        f = Figure()
        a = f.add_subplot(111)
#        a.imshow(img_arr)
        my_image_lbl.image = a.imshow(img_arr)#ImageTk.PhotoImage(file=filenamme)
        my_image_lbl.config(image=my_image_lbl.image)


tk.Button(root, text='Open File Manager', command=open).pack()

my_image_lbl = tk.Label(root)
my_image_lbl.pack()


def select_file():
    filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
    )

    global filename
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/home/sulch/imageC/',
        filetypes=filetypes)

    showinfo(
        title='Selected File',
        message=filename
    )

    return str(filename)


exit_button = tk.Button(root, text="Exit", command=root.destroy)
exit_button.pack(pady=20)

filename = open_button = tk.Button(
    root,
    text='Open a File',
    command=select_file
)

show_button = tk.Button(
    root,
    text='show imagee',
    command=lambda: showw(filename)
)


open_button.pack(expand=True)
show_button.pack(expand=True)
root.mainloop()
print(filename)