import skvideo.io  
from coloriser import VideoColoriser
import numpy as np 
import matplotlib.pyplot as plt

videodata = skvideo.io.vread("videos/earthSpinning.mp4")  
truncVideoData = videodata[:10,:,:]

grayVideo = np.dot(truncVideoData[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
grayVideo = np.stack([grayVideo]*3,axis=-1)
duration, xSize, ySize,d = grayVideo.shape
# get random indices to eventually color in
NRandomPixelsMax = 100
randomIndices = np.random.default_rng().choice(
    duration * xSize * ySize, size=int(NRandomPixelsMax), replace=False
)
# allIndices = np.linspace(0,duration*xSize*ySize-1,duration*xSize*ySize,dtype=int)
# define the coordinate pairs which we will color;
# returns an array formatted as [[t0,x0,y0],[t1,x1,y1]...]
randomCoordinates = np.array([
    [index // (xSize*ySize), (index%(xSize*ySize))% xSize, (index%(xSize*ySize))//xSize]
    # for index in allIndices
    for index in randomIndices
])
someColorVideo = grayVideo.copy()
print(randomCoordinates.shape)
someColorVideo[randomCoordinates[:,0],randomCoordinates[:,1],randomCoordinates[:,2]] = truncVideoData[randomCoordinates[:,0],randomCoordinates[:,1],randomCoordinates[:,2]] 
print(np.all(someColorVideo==truncVideoData))
# fig,ax = plt.subplots(1,3)
# ax[0].imshow(someColorVideo[0,:,:])
# ax[0].axis('off')
# ax[1].imshow(truncVideoData[0,:,:])
# ax[1].axis('off')
# ax[2].imshow(grayVideo[0,:,:])
# ax[2].axis('off')
# plt.show()
colorCoordinates = randomCoordinates
colorValues = truncVideoData[randomCoordinates[:,0],randomCoordinates[:,1],randomCoordinates[:,2]] 
normalKernel = lambda x : np.exp(-x**2)
parameters = {"delta":0.01,"sigma1":100,"sigma2":100,"p":1,"kernel":normalKernel}
skvideo.io.vwrite("videos/earthSpinningSomeColor.mp4",someColorVideo)  
skvideo.io.vwrite("videos/earthSpinningGray.mp4",grayVideo)  
VC = VideoColoriser(grayVideo=grayVideo,colorCoordinates=randomCoordinates,colorValues=colorValues,parameters=parameters)
print("Starting Video Colorisation ...")
colorisedVideo = VC.kernelColorise()
print(f"{np.max(colorisedVideo)=}")
skvideo.io.vwrite("videos/earthSpinningColorised.mp4",colorisedVideo)  