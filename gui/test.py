import matplotlib.image as mpimg
import numpy as np
x = mpimg.imread('../images/fresco.png')
y = mpimg.imread('../images/car.png')
# x = x.astype(np.uint16)
print(x[:,:,:3]*255)
