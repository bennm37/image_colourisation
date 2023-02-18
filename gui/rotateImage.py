import numpy as np 
import matplotlib.pyplot as plt

nx,ny = 500,500
circle = np.zeros((nx,ny,3))
R = 200
for i in range(nx):
    for j in range(ny):
        if (i-nx/2)**2+(j-nx/2)**2<R**2:
            circle[i,j,:] = [200,0,0]
circle = circle.astype(int)
fig,ax = plt.subplots()
ax.imshow(circle)
ax.axis('off')
plt.show()

nx,ny = 500,500
square = np.zeros((nx,ny,3))
L = 150
for i in range(nx):
    for j in range(ny):
        if abs(i-nx/2)<R and abs(j-nx/2)<R:
            square[i,j,:] = [150,0,0]
circle = circle.astype(int)
fig,ax = plt.subplots()
ax.imshow(square)
ax.axis('off')
plt.show()

def rotate_image(image,angle):
    nx,ny, = image.shape
    rotated_image = np.zeros(np.ceil(np.sqrt(2)*nx),np.ceil(np.sqrt(2)*ny))
    for i in range(nx):
        pass