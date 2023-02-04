import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

#Tried this code on a picture with n coloured points and got Kd which was of size (nxn)

#Identify the coordinates of the coloured pixels to store them 
colpix_x=[] #coloured pixel x coordinate
colpix_y=[]
#img is the gray image with a certain domain D of coloured pixels
ny,nx,rgb=img.shape
for i in range(ny):
    for j in range(nx):
        if (img[i,j,:] != img_gray_3d[i,j,:]).all():
            colpix_x=np.append(colpix_x,j)
            colpix_y=np.append(colpix_y,i)

#number of coloured pixels
n=np.size(colpix_y)

def phi(r):
    return np.exp(-(r**2))

#Find gray values in the domain D
#Take 1 layer of the stacked gray image
img_gray=img_gray_3d[:,:,0]
img_gray_domain_vals=img_gray[colpix_y.astype(int),colpix_x.astype(int)]

#Construct the kernel matrix for the domain
KernelD = np.zeros([n,n])
sigma1=100
sigma2=100
p=1/2
for k in range(n):
    KernelD[:,k] = np.multiply(phi(np.sqrt((colpix_x[k]-colpix_x[:])**2+
                            (colpix_y[k]-colpix_y[:])**2)/sigma1),
                               phi(np.abs(img_gray[int(colpix_y[k]),int(colpix_x[k])]
                                          -img_gray_domain_vals)**p)/sigma2)
    
print(KernelD)
