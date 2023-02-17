import numpy as np
from pathlib import Path
import matplotlib.image as mpimg
from gui.coloriserGUI import Coloriser
import matplotlib.pyplot as plt
from benderopt.base import OptimizationProblem, Observation
from benderopt.optimizer import optimizers
import h5py
import numexpr as ne


def plotImages(rawImage, noisyImage, improvedImage):
    mainWindowFigure = plt.figure()
    extraFigure = plt.figure()
    rawImageWindow = mainWindowFigure.add_subplot(111)
    optimisedImageWindow = extraFigure.add_subplot(111)
    rawImageWindow.imshow(rawImage)
    optimisedImageWindow.imshow(improvedImage)
    optimisedImageWindow.axis("off")
    optimisedImageWindow.set_title("improved image")
    rawImageWindow.axis("off")
    rawImageWindow.set_title("raw image")
    plt.show()


def getInit(fileName):
    # fileName = "chipmunk.jpg"
    rawImage = plt.imread(f"./images/{fileName}")
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
    someColorImage = grayImage.copy()
    someColorImage[randomCoordinates[:, 0], randomCoordinates[:, 1]] = rawImage[
        randomCoordinates[:, 0], randomCoordinates[:, 1]
    ]
    #

    colorCoordinates = randomCoordinates
    colorValues = rawImage[randomCoordinates[:, 0], randomCoordinates[:, 1]]
    return rawImage, grayImage, colorCoordinates, colorValues


fileName = "orange-flower.jpg"
rim, gim, cc, cv = getInit(fileName)
normalKernel = lambda x: np.exp(-(x**2))
# gc = np.indices([gim.shape[0], gim.shape[1]]).reshape(2, gim.shape[0] * gim.shape[1]).T


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


def objectiveFunction(delta, sigma1, sigma2, rho):
    # print(parameters)
    parameters = {
        "delta": delta,  # 0.01,
        "sigma1": sigma1,  # 100,
        "sigma2": sigma2,  # 100,
        "p": rho,  # 1,
        "kernel": normalKernel,
    }
    rawImage = readImage(fileName)
    c = Coloriser(gim, cc, cv, parameters)
    colorImage = c.kernelColoriseColumnal()
    # colorImage, kd = c.kernelColorise()
    # noisyImage = generateNoisyImage(rawImage, parameters)
    costOnIteration = generateCosts(rawImage, colorImage)
    return costOnIteration, colorImage


##
RBFProblemParameters = [
    {
        "name": "delta",
        "category": "loguniform",
        "search_space": {
            "low": 1e-7,
            "high": 1e-1,
            "step": 1e-6,
        },
    },
    {
        "name": "sigma1",
        "category": "uniform",
        "search_space": {
            "low": 1,
            "high": 150,
            "step": 1,
        },
    },
    {
        "name": "sigma2",
        "category": "uniform",
        "search_space": {
            "low": 1,
            "high": 150,
            "step": 1,
        },
    },
    {
        "name": "rho",
        "category": "uniform",
        "search_space": {
            "low": 0.1,
            "high": 2,
            "step": 0.1,
        },
    },
]

maxIterations = 100
optimisationProblem = OptimizationProblem.from_list(RBFProblemParameters)
parzenOptimiser = optimizers["parzen_estimator"](
    optimisationProblem
)  #'random' or 'parzen_estimator'
for i in range(maxIterations):
    newParameterSuggestion = parzenOptimiser.suggest()
    loss = objectiveFunction(**newParameterSuggestion)[0]
    parzenObservation = Observation.from_dict(
        {"loss": loss, "sample": newParameterSuggestion}
    )
    optimisationProblem.add_observation(parzenObservation)
    print(f"Run {i}")
    print(f"Loss: {loss}")


##
parameters = {
    "delta": 1e-6,  # 0.01,
    "sigma1": 11,  # 100,
    "sigma2": 51,  # 100,
    "p": 0.7,  # 1,
    "kernel": normalKernel,
}
rawImage = readImage(fileName)
c = Coloriser(gim, cc, cv, parameters)
colorImage = c.kernelColoriseColumnal()
generateCosts(rawImage, colorImage)
##
plotImages(rim, gim, gim)
##
