import numpy as np
import numpy.linalg as lag
import numexpr as ne
import matplotlib.pyplot as plt


class Coloriser:
    def __init__(self, grayImage, colorCoordinates, colorValues, parameters):
        """grayImage should be of shape width x height x 3, colorCoordinates n x 2 ,
        colorValues n x 3"""
        self.width, self.height, d = grayImage.shape
        self.grayImage = grayImage[:, :, 0]
        self.grayCoordinates = (
            np.indices([self.width, self.height]).reshape(2, self.width * self.height).T
        )
        self.colorCoordinates = colorCoordinates
        self.colorValues = colorValues
        self.delta = parameters["delta"]
        self.sigma1 = parameters["sigma1"]
        self.sigma2 = parameters["sigma2"]
        self.p = parameters["p"]
        self.kernel = parameters["kernel"]

    def kernelColorise(self):
        image = np.zeros((self.width, self.height, 3))
        for i in range(3):
            KD = self.getK(self.colorCoordinates, self.colorCoordinates)
            n = self.colorCoordinates.shape[0]
            self.a_s = lag.solve(KD + self.delta * np.eye(n), self.colorValues[:, i])
            # K2 = self.getK(self.grayCoordinates, self.colorCoordinates)
            # debugging
            # print(f"{KD.shape=}")
            # print(f"{n=}")
            # print(f"{self.getK(self.grayCoordinates,self.colorCoordinates).shape=}")
            # print(f"{K2 = }")
            layer_i = self.getK(self.grayCoordinates, self.colorCoordinates) @ self.a_s
            layer_i = layer_i.reshape(self.width, self.height)
            image[:, :, i] = layer_i
        return image.astype(np.uint16)

    def convNetColorise(self):
        pass

    def getK(self, X, Y):
        """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y
        are lists of coordiantes of shape k x 2"""
        nx, ny = len(X), len(Y)
        # return np.random.rand(nx,ny)/1000
        distXY = lag.norm(X[:, np.newaxis] - Y[np.newaxis, :], axis=2)
        grayX = self.grayImage[X[:, 0], X[:, 1]]
        grayY = self.grayImage[Y[:, 0], Y[:, 1]]
        grayXY = np.abs(grayX[:, np.newaxis] - grayY[np.newaxis, :])
        return self.kernel(distXY / self.sigma1) * self.kernel(
            grayXY**self.p / self.sigma2
        )

    def getColK(self, x, y, col):
        # returns the col'th column of a K matrix
        # !IMPORTANT: fixes floats
        colXY = x[:] - y[col]
        # print(colXY.shape)
        # TODO: einsum or numexpr?
        # distXYSquared = np.einsum(
        #     "ij,ij->i",
        #     colXY,
        #     colXY,
        #     optimize="optimal",
        # )
        distXYSquared = ne.evaluate("sum(colXY**2,1)")
        grayX = self.grayImage[x[:, 0], x[:, 1]].astype(np.float64)
        grayY = self.grayImage[y[:, 0], y[:, 1]].astype(np.float64)
        grayAbsDiff = np.abs((grayX[:] - grayY[col]))
        # print("going to get grayxykernelised")
        grayXYKernelised = ne.evaluate(
            "exp( -( (grayDiff ** power)/s2 )**2 )",
            local_dict={"grayDiff": grayAbsDiff, "power": self.p, "s2": self.sigma2},
        )
        # grayXY = ne.evaluate("abs(grayX[:] - grayY[col])")
        # grayXYKernelised = self.kernel(() ** self.p / self.sigma2)
        # s1 = self.sigma1
        # print("going to get distxykernelised")
        distXYKernelised = ne.evaluate(
            "exp(-distSquared / (s1)**2)",
            local_dict={"distSquared": distXYSquared, "s1": self.sigma1},
        )
        return ne.evaluate("distXYKernelised * grayXYKernelised")
        # return np.exp(-distXYSquared / self.sigma1**2) * self.kernel(
        #     grayXY**self.p / self.sigma2
        # )

    def getKD(self, x):
        KD = np.zeros((x.shape[0], x.shape[0]))
        for col in range(0, x.shape[0]):
            KD[:, col] = self.getColK(x, x, col)[:]
        return KD

    def getLayerI(self, x, y):
        layerI = np.zeros((x.shape[0], y.shape[0]))
        for i in range(0, y.shape[0]):
            # print(f"on layer {i}")
            layerI[:, i] = self.getColK(x, y, i)[:]
        return layerI

    def kernelColoriseFIXED(self):
        # TODO: Migrate over to fixed versions
        image = np.zeros((self.width, self.height, 3))
        KD = self.getKD(self.colorCoordinates)
        for i in range(3):
            print(f"on iter {i}")
            n = self.colorCoordinates.shape[0]
            self.a_s = lag.solve(
                KD + self.delta * np.eye(n), self.colorValues[:, i].astype(np.float64)
            )
            # K2 = self.getK(self.grayCoordinates, self.colorCoordinates)
            # debugging
            # print(f"{KD.shape=}")
            # print(f"{n=}")
            # print(f"{self.getK(self.grayCoordinates,self.colorCoordinates).shape=}")
            # print(f"{K2 = }")
            print("getting layer")
            layer_i = (
                self.getLayerI(self.grayCoordinates, self.colorCoordinates) @ self.a_s
            )
            # layer_i = self.getK(self.grayCoordinates, self.colorCoordinates) @ self.a_s
            layer_i = layer_i.reshape(self.width, self.height)
            image[:, :, i] = layer_i
        return image.astype(np.uint64)

    # def getColK(self,X,Y):
