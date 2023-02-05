import matplotlib.pyplot as plt
from benderopt.base import OptimizationProblem, Observation
from benderopt.optimizer import optimizers
import numpy as np
from pathlib import Path
import matplotlib.image as mpimg
from optimisation.coloriserOptimiser import Coloriser

fileName = "apple.jpeg"
rawImage = plt.imread(f"images/{fileName}")
grayImage = np.dot(rawImage[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
grayImage = np.dstack([grayImage] * 3)
xSize, ySize, d = grayImage.shape
NRandomPixelsMax = 500
# get random indices to eventually color in
randomIndices = np.random.default_rng().choice(
    xSize * ySize, size=int(NRandomPixelsMax), replace=False
)

# define the coordinate pairs which we will color;
# returns an array formatted as [[x0,y0],[x1,y1]...]
randomCoordinates = np.array(
    [[index % xSize, index // xSize] for index in randomIndices]
)
# someColorImage = grayImage.copy()
# someColorImage[randomCoordinates[:, 0], randomCoordinates[:, 1]] = rawImage[
#     randomCoordinates[:, 0], randomCoordinates[:, 1]
# ]

colorCoordinates = randomCoordinates
colorValues = rawImage[randomCoordinates[:, 0], randomCoordinates[:, 1]]
# parameters = {
# normalKernel = lambda x: np.exp(-(x**2))
#     "delta": 0.01,
#     "sigma1": 100,
#     "sigma2": 100,
#     "p": 1,
#     "kernel": normalKernel,
# }

#
def readImage(name):
    fileName = Path(".", "images", name)
    rawImage = mpimg.imread(fileName)
    rawImage = np.round(rawImage).astype(np.uint8)
    return rawImage


# given 2 images generates cost
def generateCosts(rawImage, noisyImage):
    actualImage = rawImage.astype(np.float64)
    guessImage = noisyImage.astype(np.float64)
    differences = np.abs(actualImage - guessImage)
    rDiff = np.sum(differences[:, :, 0] * 0.299)
    gDiff = np.sum(differences[:, :, 1] * 0.587)
    bDiff = np.sum(differences[:, :, 2] * 0.114)
    finalDiff = rDiff + gDiff + bDiff
    return finalDiff


def objectiveFunction(sigma1, sigma2, rho):
    # print(parameters)
    parameters = {
        "delta": 1e-4,  # 0.01,
        "sigma1": sigma1,  # 100,
        "sigma2": sigma2,  # 100,
        "p": rho,  # 1,
        # "kernel": normalKernel,
    }
    rawImage = readImage(fileName)
    c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
    colorImage, kd = c.kernelColor()
    # colorImage, kd = c.kernelColorise()
    # noisyImage = generateNoisyImage(rawImage, parameters)
    costOnIteration = generateCosts(rawImage, colorImage)
    return costOnIteration, colorImage, kd


##

import cProfile
import pstats

with cProfile.Profile() as pr:
    finalCost, ccc, x = objectiveFunction(106, 90, 0.3)

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()
##
RBFProblemParameters = [
    # {
    #     "name": "delta",
    #     "category": "loguniform",
    #     "search_space": {
    #         "low": 1e-7,
    #         "high": 1e-1,
    #         "step": 1e-6,
    #     },
    # },
    {
        "name": "sigma1",
        "category": "uniform",
        "search_space": {
            "low": 90,
            "high": 110,
            "step": 1,
        },
    },
    {
        "name": "sigma2",
        "category": "uniform",
        "search_space": {
            "low": 80,
            "high": 110,
            "step": 1,
        },
    },
    {
        "name": "rho",
        "category": "uniform",
        "search_space": {
            "low": 0,
            "high": 0.6,
            "step": 0.1,
        },
    },
]

maxIterations = 200
optimisationProblem = OptimizationProblem.from_list(RBFProblemParameters)
parzenOptimiser = optimizers["parzen_estimator"](
    optimisationProblem
)  #'random' or 'parzen_estimator'
loss = 1e8
i = 0
for i in range(60):
    newParameterSuggestion = parzenOptimiser.suggest()
    loss = objectiveFunction(**newParameterSuggestion)[0]
    parzenObservation = Observation.from_dict(
        {"loss": loss, "sample": newParameterSuggestion}
    )
    optimisationProblem.add_observation(parzenObservation)
    print(f"Run {i}")
    print(f"Loss: {loss}")
##
def plotImages(rawImage, noisyImage, improvedImage):
    mainWindowFigure = plt.figure()
    rawImageWindow = mainWindowFigure.add_subplot(211)
    optimisedImageWindow = mainWindowFigure.add_subplot(212)
    rawImageWindow.imshow(rawImage)
    optimisedImageWindow.imshow(improvedImage)
    optimisedImageWindow.axis("off")
    optimisedImageWindow.set_title("improved image")
    rawImageWindow.axis("off")
    rawImageWindow.set_title("raw image")
    plt.show()


##


##
# r = readImage(fileName)
# plotImages(r, r, ccc)
import scipy as sp

a = randomCoordinates[0:2]
b = 2 * a
an = a[:, np.newaxis]
bn = b[np.newaxis, :]
c = an - bn
a.shape
##
kd = objectiveFunction(100, 100, 0.5)[2]
##
def tester():
    grayX = np.zeros([len(colorCoordinates), 3])
    grayY = np.zeros([len(colorCoordinates), 3])
    for i in range(len(colorCoordinates)):
        grayX[i] = grayImage[int(colorCoordinates[i, 0]), int(colorCoordinates[i, 1])]
        grayY[i] = grayImage[int(colorCoordinates[i, 0]), int(colorCoordinates[i, 1])]
    # grayX = grayImage[X[:, 0], X[:, 1]]
    # grayY = grayImage[Y[:, 0], Y[:, 1]]
    print(type(grayY))
    grayXY = np.abs(
        np.expand_dims(grayX, -1) - np.expand_dims(grayY, 0)
    )  # grayX[:, np.newaxis] - grayY[np.newaxis, :])
    return grayX, grayY


import cProfile
import pstats

g, t = tester()

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()
