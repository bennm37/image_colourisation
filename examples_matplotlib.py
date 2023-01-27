import matplotlib.pyplot as plt
import numpy as np

# load RGB image in numpy array
img = plt.imread('image.jpg')

# convert to grayscale
img_gray = np.dot(img[...,:3], [0.299, 0.587, 0.114])

# round to integers
img_gray = np.round(img_gray).astype(np.uint8)

# save grayscale image
plt.imsave('image_gray.jpg', img_gray, cmap='gray')

# show grayscale image
plt.imshow(img_gray, cmap='gray')

# show RGB image
plt.imshow(img)

# make grayscale image into a colured image
img_gray_3d = np.stack((img_gray,)*3, axis=-1)

# replace the pixels of the grayscale image with the pixels of the original image
percentage = 0.1
mask = np.random.rand(*img_gray.shape) < percentage
img_gray_3d[mask, :] = img[mask, :]

# save the new image
plt.imsave('image_coloured.jpg', img_gray_3d)



