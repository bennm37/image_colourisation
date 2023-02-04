import numpy as np 
import numpy.linalg as lag
import matplotlib.pyplot as plt

# def colourise(grayscaleValues,aspectRatio,colorPositions,colorValues,parameters):
#     m = grayscaleValues.shape[0]
#     n = colorValues.shape[0]
#     for i in range(3):
#         KD = getK(grayscaleValues,aspectRatio,colorPositions,colorValues[:,:,i],parameters)
#         delta = parameters["delta"]
#         a_s = lag.solve(colorValues,KD+delta*np.eye(n))
#         image = getK()


# Getting data in the style of main.py
rawImage = plt.imread("images/apple.jpeg")
grayImage = np.dot(rawImage[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
grayImage = np.dstack([grayImage]*3)
print(np.max(grayImage))
xSize, ySize,d = grayImage.shape
NRandomPixelsMax = 10000

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

print(grayImage[randomCoordinates[:,0],randomCoordinates[:,1]])
print(np.sum(np.all(grayImage==[255,0,0],axis=2)))
fig,ax = plt.subplots(1,2)
ax[0].imshow(grayImage)
ax[0].axis('off')
ax[1].imshow(someColorImage)
ax[1].axis('off')
plt.show()


colorCoordinates = randomCoordinates
colorValues = rawImage[randomCoordinates[:,0],randomCoordinates[:,1]]

class Colouriser:
    def __init__(self,grayImage,colorCoordinates,colorValues,parameters):
        self.aspectRatio = grayImage.shape
        self.grayImageVector = grayImage.flatten()
        self.colorCoordinates = colorCoordinates
        self.colorValues = colorValues
    
    def kernelColorise(self):
        image = np.zeros((self.aspectRatio[0],self.aspectRatio[1],3))
        for i in range(3):
            image[i] = 

    def convNetColorise(self):
        pass

    def getK(self,X,Y):
        """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y 
        refer to the flattened coordiantes of the image."""
        nx,ny = len(X),len(Y)
        return np.ones((nx,ny))
        