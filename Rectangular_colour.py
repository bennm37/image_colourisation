import matplotlib.pyplot as plt
import numpy as np

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

# Function to have a coloured rectangle on
def colourbox(istart,iend,jstart,jend):
    newimg=image
    size_y,size_x,null=image.shape
    grayimg=img_gray_3d
    for i in range(istart,iend):
        for j in range(jstart,jend):
            grayimg[i,j,:]=newimg[i,j,0:3] 
    return plt.imshow(grayimg,cmap='gray')

#Using the function
colourbox(150,200,150,200)
plt.show()
