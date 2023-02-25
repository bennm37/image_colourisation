import numpy as np
import glob
import os
from pathlib import Path
import matplotlib.image as mpimg
from gui.coloriserGUI import Coloriser
import matplotlib.pyplot as plt
from benderopt.base import OptimizationProblem, Observation
from benderopt.optimizer import optimizers
from hyperopt import hp
import h5py
import numexpr as ne
import pathlib
import pandas as pd

##

mainDirectory = pathlib.Path(__file__).parent.parent  # directory containing main files


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
    imageToRead = pathlib.Path(mainDirectory, folder_name, fileName)
    rawImage = plt.imread(imageToRead)
    grayImage = np.dot(rawImage[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
    grayImage = np.dstack([grayImage] * 3)
    xSize, ySize, d = grayImage.shape
    NRandomPixelsMax = 66
    # get random indices to eventually color in
    np.random.seed(seed=190427)
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


# fileName = "duck-256.jpg"
# rim, gim, cc, cv = getInit(fileName)
# normalKernel = lambda x: np.exp(-(x**2))
# gc = np.indices([gim.shape[0], gim.shape[1]]).reshape(2, gim.shape[0] * gim.shape[1]).T


def readImage(name):
    imageToRead = pathlib.Path(mainDirectory, folder_name, name)
    rawImage = plt.imread(imageToRead)
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
    finalDiff = (rDiff + gDiff + bDiff) / (actualImage.shape[0] * actualImage.shape[1])
    return finalDiff


def objectiveFunction(delta, sigma1, sigma2, rho):
    # print(parameters)
    parameters = {
        "delta": delta,  # 0.01,
        "sigma1": sigma1,  # 100,
        "sigma2": sigma2,  # 100,
        "p": rho,  # 1,
    }
    rawImage, grayImage, colorCoordinates, colorValues = getInit(file_name)
    c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
    colorImage = c.kernelColoriseColumnal()

    # colorImage, kd = c.kernelColorise()
    # noisyImage = generateNoisyImage(rawImage, parameters)
    costOnIteration = generateCosts(rawImage, colorImage)
    return costOnIteration, colorImage


##
# file_name = "knights-256.jpg"
# folder_name = "smolreal"
def optimise(file_name, runNo):
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
    maxIterations = 250
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
        # deltas.append(optimisationProblem.samples[i]["delta"])
        # sigma1s.append(optimisationProblem.samples[i]["sigma1"])
        # sigma2s.append(optimisationProblem.samples[i]["sigma2"])
        # rhos.append(optimisationProblem.samples[i]["rho"])
        # losses.append(loss)
        print(f"run {i}/{maxIterations}, loss={loss}, image #{runNo}")

    parameters = {}
    parameters["losses"] = optimisationProblem.sorted_observations[0].loss
    parameters["delta"] = optimisationProblem.best_sample["delta"]
    parameters["sigma1"] = optimisationProblem.best_sample["sigma1"]
    parameters["sigma2"] = optimisationProblem.best_sample["sigma2"]
    parameters["rho"] = optimisationProblem.best_sample["rho"]
    parameters["filename"] = file_name
    return parameters


##
if __name__ == "__main__":
    folder_name = "smolreal"
    resultsFolder = pathlib.Path(mainDirectory, "results")
    file_names = os.listdir(pathlib.Path(mainDirectory, folder_name))
    finalResults = pd.DataFrame()

    for i, file_name in enumerate(file_names):
        print(f"on {file_name}, run {i}/{len(file_names)}")
        resultsDict = optimise(file_name, i)
        resultsDF = pd.DataFrame([resultsDict])
        finalResults = pd.concat([finalResults, resultsDF], ignore_index=True)

    finalResults.to_csv("zella", index=False)
