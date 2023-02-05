import numpy as np 
import numpy.linalg as lag
import matplotlib.pyplot as plt
from numba import njit 
class Coloriser:
    def __init__(self,grayImage,colorCoordinates,colorValues,parameters):
        """grayImage should be of shape width x height x 3, colorCoordinates n x 2 , 
        colorValues n x 3"""
        self.width,self.height,d = grayImage.shape
        self.grayImage = grayImage[:,:,0]
        self.grayCoordinates = np.indices([self.width,self.height]).reshape(2,self.width*self.height).T
        self.colorCoordinates = colorCoordinates
        self.colorValues = colorValues
        self.delta = parameters["delta"]
        self.sigma1 = parameters["sigma1"]
        self.sigma2 = parameters["sigma2"]
        self.p = parameters["p"]
        self.kernel = parameters["kernel"]
    
    def kernelColorise(self):
        image = np.zeros((self.width,self.height,3))
        for i in range(3):
            KD = getK(self.colorCoordinates,self.colorCoordinates,self.grayImage,self.sigma1,self.sigma2,self.p,kerneltype="exp")
            n = self.colorCoordinates.shape[0]
            self.a_s = lag.solve(KD+self.delta*np.eye(n),self.colorValues[:,i])
            # K2AG = getKAllGray(self.colorCoordinates,self.grayImage,self.sigma1,self.sigma2,self.p,kerneltype="exp")
            K2 = getK(self.grayCoordinates,self.colorCoordinates,self.grayImage,self.sigma1,self.sigma2,self.p,kerneltype="exp")
            # assert(K2AG.shape==K2.shape)
            # assert(np.allclose(K2AG,K2))
            layer_i = K2 @ self.a_s
            layer_i = layer_i.reshape(self.width,self.height)
            image[:,:,i] = layer_i
        return image.astype(np.uint16)
    
    def convNetColorise(self):
        pass
@njit
def expkernel(x):
    return np.exp(-x**2)

@njit
def compactkernel(x):
    if x>1:
        return 0
    else:
        return (4*x+1)*(1-x)**4

@njit 
def norm(X):
    return np.sqrt(X[0]**2+X[1]**2)

# @njit
# def getK(X,Y,grayImage,sigma1,sigma2,p):
#     """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y 
#     are lists of coordiantes of shape k x 2"""
#     # distXY = lag.norm(X[:,np.newaxis]-Y[np.newaxis,:],axis=2)
#     distXY = grayImage.copy()
#     grayX = np.zeros()
#     for i in range(len(X)):
#         grayX[i] = grayImage[X[i,0],X[i,1]]
#     grayY = grayImage[Y[:,0],Y[:,1]]
#     grayXY = np.abs(grayX[:,np.newaxis]-grayY[np.newaxis,:])
#     return expkernel(distXY/sigma1)*expkernel(grayXY**p/sigma2)

@njit
def getK(X,Y,grayImage,sigma1,sigma2,p,kerneltype="exp"):
    """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y 
    are lists of coordiantes of shape k x 2"""
    nx,ny = len(X),len(Y)
    K = np.zeros((nx,ny))
    for i in range(nx):
        for j in range(ny):
            distXY = norm(X[i]-Y[j])
            grayXY = np.abs(grayImage[X[i,0],X[i,1]]-grayImage[Y[j,0],Y[j,1]])
            if kerneltype =="exp":
                K[i,j] = expkernel(distXY/sigma1)*expkernel(grayXY**p/sigma2)
            if kerneltype == "compact":
                K[i,j] = compactkernel(distXY/sigma1)*compactkernel(grayXY**p/sigma2)
    return K
        
@njit
def getKAllGray(Y,grayImage,sigma1,sigma2,p,kerneltype="compact"):
    """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y 
    are lists of coordiantes of shape k x 2"""
    gx,gy = grayImage.shape
    nx,ny = gx*gy,len(Y)
    K = np.zeros((nx,ny))
    for point in Y:
        x,y = point
        for i in range(max(x-sigma1,0),min(x+sigma1,gx)):
            for j in range(max(y-sigma1,0),min(y+sigma1,gy)):
                distXY = norm([x-i,y-j])
                grayXY = np.abs(grayImage[x,y]-grayImage[i,j])
                if kerneltype == "compact":
                    K[i,j] = compactkernel(distXY/sigma1)*compactkernel(grayXY**p/sigma2)
                else:
                    K[i,j] = expkernel(distXY/sigma1)*expkernel(grayXY**p/sigma2)
    return K