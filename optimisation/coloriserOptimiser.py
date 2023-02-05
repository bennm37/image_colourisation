import numpy as np
import numpy.linalg as lag
import numba as nb
import scipy as sp

import matplotlib.pyplot as plt


@nb.njit
def ker(x):
    # return sp.linalg.expm(-np.square(x))
    return np.exp(-(x**2))


@nb.njit
def kernelColorise(
    width,
    height,
    colorCoordinates,
    grayCoordinates,
    delta,
    colorValues,
    grayImage,
    sigma1,
    sigma2,
    p,
):
    image = np.zeros((width, height, 3))
    KD = 0
    # for i in np.arange(3):
    def getK(X, Y, grayImage, sigma1, sigma2, p):
        """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y
        are lists of coordiantes of shape k x 2"""
        # nx, ny = len(X), len(Y)
        # return np.random.rand(nx,ny)/1000
        # X[:, np.newaxis] - Y[np.newaxis, :] gives:
        # [(X_x1-Y_x1,X_y1-Y_y1),(X_x2-Y_x2,X_y2-Y_y2)...]
        # distXY = lag.norm(X[:, np.newaxis] - Y[np.newaxis, :], axis=2)
        # distXY = lag.norm(np.expand_dims(X, -1) - np.expand_dims(Y, 0), axis=2)
        # distXY = np.sqrt(np.sum(np.square(X[:, np.newaxis] - Y[np.newaxis, :]), axis=2))
        distXY = np.sqrt(
            np.sum(
                np.square(
                    np.expand_dims(X, -1) - np.expand_dims(Y, 0),
                ),
                axis=2,
            )
        )
        grayX = np.zeros_like(grayImage)
        grayY = np.zeros_like(grayImage)
        for i in range(len(X)):
            grayX = grayImage[int(X[i, 0]), int(X[i, 1])]
            grayY = grayImage[int(Y[i, 0]), int(Y[i, 1])]
        # grayX = grayImage[X[:, 0], X[:, 1]]
        # grayY = grayImage[Y[:, 0], Y[:, 1]]
        grayXY = np.subtract(
            np.expand_dims(grayX, -1) - np.expand_dims(grayY, 0)
        )  # grayX[:, np.newaxis] - grayY[np.newaxis, :])

        return ker(distXY / sigma1) * 1  # ker(grayXY**p / sigma2)

    KD = getK(colorCoordinates, colorCoordinates, grayImage, sigma1, sigma2, p).astype(
        np.ndarray
    )
    # n = colorCoordinates.shape[0]
    # a_s = lag.solve(np.add(KD, delta * np.eye(n)), colorValues[:, i])
    # # K2 = self.getK(self.grayCoordinates, self.colorCoordinates)
    # # debugging
    # # print(f"{KD.shape=}")
    # # print(f"{n=}")
    # # print(f"{self.getK(self.grayCoordinates,self.colorCoordinates).shape=}")
    # # print(f"{K2 = }")
    # layer_i = (
    #     getK(grayCoordinates, colorCoordinates, grayImage, sigma1, sigma2, p) @ a_s
    # )
    # layer_i = layer_i.reshape(width, height)
    # image[:, :, i] = layer_i
    return image.astype(np.uint16), KD


#
# @nb.jit
# def getK(X, Y, grayImage, sigma1, sigma2, p):
#     """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y
#     are lists of coordiantes of shape k x 2"""
#     # nx, ny = len(X), len(Y)
#     # return np.random.rand(nx,ny)/1000
#     # X[:, np.newaxis] - Y[np.newaxis, :] gives:
#     # [(X_x1-Y_x1,X_y1-Y_y1),(X_x2-Y_x2,X_y2-Y_y2)...]
#     # distXY = lag.norm(X[:, np.newaxis] - Y[np.newaxis, :], axis=2)
#     # distXY = lag.norm(np.expand_dims(X, -1) - np.expand_dims(Y, 0), axis=2)
#     # distXY = np.sqrt(np.sum(np.square(X[:, np.newaxis] - Y[np.newaxis, :]), axis=2))
#     distXY = np.sqrt(
#         np.sum(
#             np.square(
#                 np.expand_dims(X, -1) - np.expand_dims(Y, 0),
#             ),
#             axis=2,
#         )
#     )
#     grayX = grayImage[X[:, 0], X[:, 1]]
#     grayY = grayImage[Y[:, 0], Y[:, 1]]
#     grayXY = np.abs(grayX[:, np.newaxis] - grayY[np.newaxis, :])
#
#     return ker(distXY / sigma1) * ker(grayXY**p / sigma2)


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
        # self.kernel = parameters["kernel"]

    def kernelColor(self):
        return kernelColorise(
            self.width,
            self.height,
            self.colorCoordinates,
            self.grayCoordinates,
            self.delta,
            self.colorValues,
            self.grayImage,
            self.sigma1,
            self.sigma2,
            self.p,
        )

    # def kGet(self, X, Y):
    #     return getK(X, Y, self.grayImage, self.sigma1, self.sigma2, self.p)

    # @nb.jit(nopython=True)
    # def kernelColorise(self):
    #     image = np.zeros((self.width, self.height, 3))
    #     KD = 0
    #     for i in range(3):
    #         KD = self.getK(self.colorCoordinates, self.colorCoordinates)
    #         n = self.colorCoordinates.shape[0]
    #         self.a_s = lag.solve(
    #             np.add(KD, self.delta * np.eye(n)), self.colorValues[:, i]
    #         )
    #         # K2 = self.getK(self.grayCoordinates, self.colorCoordinates)
    #         # debugging
    #         # print(f"{KD.shape=}")
    #         # print(f"{n=}")
    #         # print(f"{self.getK(self.grayCoordinates,self.colorCoordinates).shape=}")
    #         # print(f"{K2 = }")
    #         layer_i = self.getK(self.grayCoordinates, self.colorCoordinates) @ self.a_s
    #         layer_i = layer_i.reshape(self.width, self.height)
    #         image[:, :, i] = layer_i
    #     return image.astype(np.uint16), KD
    #
    #
    # @nb.njit
    # def getK(self, X, Y):
    #     """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y
    #     are lists of coordiantes of shape k x 2"""
    #     nx, ny = len(X), len(Y)
    #     # return np.random.rand(nx,ny)/1000
    #     # X[:, np.newaxis] - Y[np.newaxis, :] gives:
    #     # [(X_x1-Y_x1,X_y1-Y_y1),(X_x2-Y_x2,X_y2-Y_y2)...]
    #     # distXY = lag.norm(X[:, np.newaxis] - Y[np.newaxis, :], axis=2)
    #     distXY = np.sqrt(np.sum(np.square(X[:, np.newaxis] - Y[np.newaxis, :]), axis=2))
    #     grayX = self.grayImage[X[:, 0], X[:, 1]]
    #     grayY = self.grayImage[Y[:, 0], Y[:, 1]]
    #     grayXY = np.abs(grayX[:, np.newaxis] - grayY[np.newaxis, :])
    #
    #     return ker(distXY / self.sigma1) * ker(grayXY**self.p / self.sigma1)
    #     # return self.kernel(distXY / self.sigma1) * self.kernel(
    #     #     grayXY**self.p / self.sigma1
    #     # )

    def convNetColorise(self):
        pass
