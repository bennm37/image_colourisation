from coloriser import Coloriser
import numpy as np 
import matplotlib.pyplot as plt

rawImage = plt.imread("images/apple.jpeg")
grayImage = np.dot(rawImage[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
grayImage = np.dstack([grayImage]*3)
print(np.max(grayImage))
xSize, ySize,d = grayImage.shape
NRandomPixelsMax = 500

# get random indices to eventually color in
randomIndices = np.random.default_rng().choice(
    xSize * ySize, size=int(NRandomPixelsMax), replace=False
)
# define the coordinate pairs which we will color;
# returns an array formatted as [[x0,y0],[x1,y1]...]
randomCoordinates = np.array([
    [index % xSize, index // xSize]
    for index in randomIndices
])
someColorImage = grayImage.copy()
someColorImage[randomCoordinates[:,0],randomCoordinates[:,1]] = rawImage[randomCoordinates[:,0],randomCoordinates[:,1]] 

# print(grayImage[randomCoordinates[:,0],randomCoordinates[:,1]])
# print(np.sum(np.all(grayImage==[255,0,0],axis=2)))
# fig,ax = plt.subplots(1,2)
# ax[0].imshow(grayImage)
# ax[0].axis('off')
# ax[1].imshow(someColorImage)
# ax[1].axis('off')
# plt.show()

colorCoordinates = randomCoordinates
colorValues = rawImage[randomCoordinates[:,0],randomCoordinates[:,1]]
normalKernel = lambda x : np.exp(-x**2)
parameters = {"delta":0.01,"sigma1":100,"sigma2":100,"p":1,"kernel":normalKernel}
c = Coloriser(grayImage,colorCoordinates,colorValues,parameters)
colorisedImage = c.kernelColorise()
print(f"{np.max(colorisedImage)=}")
print(f"{np.min(colorisedImage)=}")
print(f"{colorisedImage.dtype=}")

# pixel histogram 
fig,ax = plt.subplots()
redPixelValues = colorisedImage[:,:,0].flatten()
ax.hist(redPixelValues,bins=100)
ax.set(xlim=(0,300))
plt.show()

fig,ax = plt.subplots(1,2)
ax[0].imshow(someColorImage)
ax[0].axis('off')
ax[1].imshow(colorisedImage)
ax[1].axis('off')
plt.show()