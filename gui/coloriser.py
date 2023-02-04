import numpy as np 
import numpy.linalg as lag
import matplotlib.pyplot as plt

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
            KD = self.getK(self.colorCoordinates,self.colorCoordinates)
            n = self.colorCoordinates.shape[0]
            self.a_s = lag.solve(KD+self.delta*np.eye(n),self.colorValues[:,i])
            K2 = self.getK(self.grayCoordinates,self.colorCoordinates)
            # debugging
            # print(f"{KD.shape=}")
            # print(f"{n=}")
            # print(f"{self.getK(self.grayCoordinates,self.colorCoordinates).shape=}")
            # print(f"{K2 = }")
            layer_i = self.getK(self.grayCoordinates,self.colorCoordinates) @ self.a_s
            layer_i = layer_i.reshape(self.width,self.height)
            image[:,:,i] = layer_i
        return image.astype(np.uint16)
    
    def convNetColorise(self):
        pass

    def getK(self,X,Y):
        """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y 
        are lists of coordiantes of shape k x 2"""
        nx,ny = len(X),len(Y)
        # return np.random.rand(nx,ny)/1000
        distXY = lag.norm(X[:,np.newaxis]-Y[np.newaxis,:],axis=2)
        grayX = self.grayImage[X[:,0],X[:,1]]
        grayY = self.grayImage[Y[:,0],Y[:,1]]
        grayXY = np.abs(grayX[:,np.newaxis]-grayY[np.newaxis,:])
        return self.kernel(distXY/self.sigma1)*self.kernel(grayXY**self.p/self.sigma1)
