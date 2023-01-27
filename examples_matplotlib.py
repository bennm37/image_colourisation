import matplotlib.pyplot as plt
import numpy as np

# load RGB image in numpy array
img = plt.imread('images/images/banana.jpeg')

# convert to grayscale
img_gray = np.dot(img[...,:3], [0.299, 0.587, 0.114])

# round to integers
img_gray = np.round(img_gray).astype(np.uint8)

# save grayscale image
plt.imsave('images/image_gray2.jpg', img_gray, cmap='gray')

# show grayscale image
plt.imshow(img_gray, cmap='gray')

# show RGB image
plt.imshow(img)

# make grayscale image into a coloured image
img_gray_3d = np.stack((img_gray,)*3, axis=-1)
plt.imsave('image_gray_3d.jpg', img_gray_3d)

# replace the pixels of the grayscale image with the pixels of the original image
percentage = 0.1
mask = np.random.rand(*img_gray.shape) < percentage
img_gray_3d[mask, :] = img[mask, :]

# save the new image
# plt.imsave('images/images/image_coloured2.jpg', img_gray_3d)

img_gray_3d = np.stack((img_gray,)*3, axis=-1)

# grid colourization
I = 100
J = 100

size_x, size_y = img_gray.shape

for x in np.linspace(0, size_x, I, dtype=int, endpoint=False):
    for y in np.linspace(0, size_y, J, dtype=int, endpoint=False):
        img_gray_3d[x, y, :] = img[x, y, :]

plt.imsave('images/image_coloured_grid.jpg', img_gray_3d)



