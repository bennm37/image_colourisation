import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# Reading image using imread
image=plt.imread("images/image2.jpg")

# convert to grayscale
img_gray = np.dot(image[...,:3], [0.299, 0.587, 0.114])
# round to integers
img_gray = np.round(img_gray).astype(np.uint8)

img_gray_3d = np.stack((img_gray,)*3,axis=-1)

# show grayscale image
plt.imshow(img_gray_3d, cmap='gray')
plt.show()

grayimg=img_gray_3d
# Function to have a coloured rectangle on
def colourbox(istart,iend,jstart,jend):
    newimg=image
    size_y,size_x,null=image.shape
    for i in range(istart,iend):
        for j in range(jstart,jend):
            grayimg[i,j,:]=newimg[i,j,0:3] 
  #  return plt.imshow(grayimg,cmap='gray')
    return grayimg
img_gray_3d = np.stack((img_gray,)*3,axis=-1)

#Using the function
#colourbox(150,200,150,200)
#plt.imshow(grayimg)
#plt.show()

#Click to colour in the picture (will try to add more features)
grayimg=img_gray_3d
fig = plt.figure()
gs = GridSpec(2,3)
ax0 = fig.add_subplot(gs[0:2,0:2])
img = img_gray_3d
ax0.imshow(img)
nx,ny,d = img.shape
def onclick(event):
    global x,y
    if event.inaxes==ax0:
        x,y = event.xdata,event.ydata
        x,y = np.round(x).astype(int),np.round(y).astype(int)
        colourbox(y,y+20,x,x+20)
        img=grayimg
        ax0.imshow(img)
        print("clicked image")
        print("x,y is ", x,y)
    else:
        print("Please click on the image to colourise a section")
    fig.canvas.draw_idle()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
