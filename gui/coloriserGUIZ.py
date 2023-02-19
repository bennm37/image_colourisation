import numpy as np
import numpy.linalg as lag
import numexpr as ne
import matplotlib.pyplot as plt

## My version


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

    def kernelColoriseColumnal(self):
        image = np.zeros((self.width, self.height, 3))
        KD = self.getKD(self.colorCoordinates)
        n = self.colorCoordinates.shape[0]
        layerITemplate = self.getLayerI(self.grayCoordinates, self.colorCoordinates)
        for i in range(3):
            self.a_s = lag.solve(
                KD + self.delta * np.eye(n), self.colorValues[:, i].astype(np.float64)
            )
            layer_i = layerITemplate @ self.a_s
            layer_i = layer_i.reshape(self.width, self.height)
            image[:, :, i] = layer_i
        return np.clip(image, 0, 255).astype(
            np.uint8
        )  # ensure range of output image is between 0, 255

    def kernelColoriseColumnalLarge(self):
        print("Generating kernel...\n(Note: This process may take several minutes.)")
        image = np.zeros((self.width, self.height, 3))
        KD = self.getKD(self.colorCoordinates)
        n = self.colorCoordinates.shape[0]
        for i in range(3):
            print(f"Starting layer {i+1}")
            self.a_s = lag.solve(KD + self.delta * np.eye(n), self.colorValues[:, i])
            layerI = np.zeros((self.grayCoordinates.shape[0]))
            for col in range(n):
                layerI += (
                    self.getColK(self.grayCoordinates, self.colorCoordinates, col)
                    * self.a_s[col]
                )
            layerI = layerI.reshape(self.width, self.height)
            image[:, :, i] = layerI
        return np.clip(image, 0, 255).astype(
            np.uint8
        )  # ensure range of output image is between 0, 255

    def convNetColorise(self):
        pass

    def getColK(self, x, y, col):
        # TODO: einsum or numexpr?
        # distXYSquared = np.einsum(
        #     "ij,ij->i",
        #     colXY,
        #     colXY,
        #     optimize="optimal",
        # )

        # normalised
        # colXY = x[:] - y[col]
        colXY = (x[:] - y[col]) / np.array([self.width, self.height])
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
