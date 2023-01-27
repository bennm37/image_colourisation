import matplotlib.pyplot as plt 
import numpy as np
from matplotlib.gridspec import GridSpec
from utils import grayscale


fig = plt.figure()
gs = GridSpec(2,3)
ax0 = fig.add_subplot(gs[0:2,0:2])
ax1 = fig.add_subplot(gs[0,2])
ax2 = fig.add_subplot(gs[1,2])
img = plt.imread("images/fresco.png")
img = grayscale(img)
wheel = plt.imread("images/color_wheel.jpeg")
selected_color = np.ones([2,2,3])*0
ax0.imshow(img)
ax1.imshow(wheel)
ax0.axis('off')
ax1.axis('off')
ax2.axis('off')
ax2.imshow(selected_color)
nx,ny,d = img.shape
sc = [0,0,0]
def onclick(event):
    global sc
    print("clicked")
    if event.inaxes==ax0:
        x,y = event.xdata,event.ydata
        x,y = np.round(x).astype(int),np.round(y).astype(int)
        img[y:y+100,x:x+100,:] = sc
        print("clicked image")
        ax0.clear()
        ax0.imshow(img)
        ax0.axis('off')
    if event.inaxes == ax1:
        x,y = event.xdata,event.ydata
        x,y = np.round(x).astype(int),np.round(y).astype(int)
        sc = wheel[y,x]
        print("selected color is ", sc)
        selected_color = np.tile(sc,(2,2,1))
        ax2.imshow(selected_color)
        ax2.axis('off')
        print(selected_color.shape)
    fig.canvas.draw_idle()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
