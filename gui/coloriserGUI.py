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
        # TODO: einsum or numexpr?
        # distXYSquared = np.einsum(
        #     "ij,ij->i",
        #     colXY,
        #     colXY,
        #     optimize="optimal",
        # )

        colXY = x[:] - y[col]
        distXYKernelised = ne.evaluate(
            "exp(-distSquared / (s1)**2)",
            local_dict={
                "distSquared": ne.evaluate("sum(colXY**2,1)"),
                "s1": self.sigma1,
            },
        )

        grayX = self.grayImage[x[:, 0], x[:, 1]].astype(np.float64)
        grayY = self.grayImage[y[:, 0], y[:, 1]].astype(np.float64)
        grayAbsDiff = np.abs((grayX[:] - grayY[col]))
        grayXYKernelised = ne.evaluate(
            "exp( -( (grayDiff ** power)/s2 )**2 )",
            local_dict={"grayDiff": grayAbsDiff, "power": self.p, "s2": self.sigma2},
        )
        return ne.evaluate("distXYKernelised * grayXYKernelised")

    def getKD(self, x):
        KD = np.zeros((x.shape[0], x.shape[0]))
        for col in range(0, x.shape[0]):
            KD[:, col] = self.getColK(x, x, col)[:]
        return KD

    def getLayerI(self, x, y):
        layerI = np.zeros((x.shape[0], y.shape[0]))
        for col in range(0, y.shape[0]):
            layerI[:, col] = self.getColK(x, y, col)[:]
        return layerI

    def kernelColoriseColumnal(self):
        image = np.zeros((self.width, self.height, 3))
        KD = self.getKD(self.colorCoordinates)
        n = self.colorCoordinates.shape[0]
        print(
            "Generating template image layer...\n(Note: This process may take several minutes for large (> 1000 * 1000) images."
        )
        layerITemplate = self.getLayerI(self.grayCoordinates, self.colorCoordinates)
        for i in range(3):
            self.a_s = lag.solve(
                KD + self.delta * np.eye(n), self.colorValues[:, i].astype(np.float64)
            )
            layer_i = layerITemplate @ self.a_s
            layer_i = layer_i.reshape(self.width, self.height)
            image[:, :, i] = layer_i
        return image.astype(np.uint64)
