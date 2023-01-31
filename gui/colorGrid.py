import matplotlib.pyplot as plt 
import numpy as np 
from matplotlib import colormaps as cm

size = 30
cmap = cm['gist_rainbow']
color = np.array(cmap(0.1)[:3])*255
color = color.astype(np.uint16)
t = np.linspace(0,1,size)
# grayscale = np.linspace(0,255,size,dtype=np.uint16)
# grayscale = np.dstack([grayscale]*3).reshape(size,3)
# grayscale = np.dstack([grayscale]*size).reshape(size,size,3)
colorscale = color[np.newaxis,:]*t[:,np.newaxis]
colorscale = colorscale[:,np.newaxis,:]*t[np.newaxis,:,np.newaxis]
colorscale = colorscale.astype(np.uint16)
white = np.array([255,255,255])
grayscale = white[np.newaxis,:]*t[:,np.newaxis]
grayscale = grayscale[:,np.newaxis,:]-grayscale[:,np.newaxis,:]*t[np.newaxis,:,np.newaxis]
grayscale = grayscale.astype(np.uint16)
# colorscale = np.array(color[np.newaxis,:]*t[:,np.newaxis]*255).astype(np.uint16)
# colorGrid = colorscale[:,np.newaxis,:]*t[np.newaxis,:,np.newaxis]
# plt.imshow(grayscale[::-1,:,:])
fig,ax = plt.subplots()
ax.imshow(grayscale[:,::-1]+colorscale[:,::-1],interpolation='bilinear')
ax.invert_yaxis()
plt.show()