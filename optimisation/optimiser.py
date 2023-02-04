import matplotlib.pyplot as plt
from benderopt.base import OptimizationProblem, Observation
from benderopt.optimizer import optimizers
from benderopt import minimize
import numpy as np
from pathlib import Path
import matplotlib.image as mpimg


def gaussian(mean, sigma, rawImage, seed):
    np.random.seed(seed)
    gaussian = np.round(np.random.normal(mean, np.abs(sigma), rawImage.shape[0:2]))
    return gaussian


def generateNoisyImage(
    rawImage,
    parameters,
):
    rawImage = rawImage.astype(np.float64)
    mean = np.abs(np.real(parameters[0]))
    var = np.abs(np.real(parameters[1]))
    sigma = var**0.5
    noisyImage = np.zeros_like(rawImage)
    noisyImage[:, :, 0] = np.clip(
        rawImage[:, :, 0] + gaussian(mean, sigma, rawImage, 1), 0, 255
    )
    noisyImage[:, :, 1] = np.clip(
        rawImage[:, :, 1] + gaussian(mean, sigma, rawImage, 2), 0, 255
    )
    noisyImage[:, :, 2] = np.clip(
        rawImage[:, :, 2] + gaussian(mean, sigma, rawImage, 3), 0, 255
    )
    return noisyImage


def plotImages(rawImage, noisyImage, improvedImage):
    mainWindowFigure = plt.figure()
    rawImageWindow = mainWindowFigure.add_subplot(311)
    noiseImageWindow = mainWindowFigure.add_subplot(312)
    optimisedImageWindow = mainWindowFigure.add_subplot(313)
    noiseImageWindow.imshow(noisyImage)
    noiseImageWindow.axis("off")
    noiseImageWindow.set_title("noisy image")
    rawImageWindow.imshow(rawImage)
    optimisedImageWindow.imshow(improvedImage)
    optimisedImageWindow.axis("off")
    optimisedImageWindow.set_title("improved image")
    rawImageWindow.axis("off")
    rawImageWindow.set_title("raw image")
    plt.show()


def readImage(name):
    fileName = Path("..", "images", name)
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


def objectiveFunction(x, p):
    parameters = [x, p]
    # print(parameters)
    rawImage = readImage("image.jpg")
    noisyImage = generateNoisyImage(rawImage, parameters)
    costOnIteration = generateCosts(rawImage, noisyImage)
    return costOnIteration


optimizationProblemParameters = [
    {
        "name": "p",
        "category": "lognormal",
        "search_space": {
            "low": 1e-2,
            "high": 1e5,
            "mu": 1e2,
            "sigma": 1e2,
            # "step": 1e-7,
        },
    },
    {
        "name": "x",
        "category": "uniform",
        "search_space": {
            "low": 0,
            "high": 1,
        },
    },
]


RBFProblemParameters = [
    {
        "name": "sigma1",
        "category": "uniform",
        "search_space": {
            "low": 0,
            "high": 0.1,
        },
    },
    {
        "name": "sigma2",
        "category": "uniform",
        "search_space": {
            "low": 0,
            "high": 0.1,
        },
    },
    {
        "name": "delta",
        "category": "uniform",
        "search_space": {
            "low": 0,
            "high": 0.1,
        },
    },
    {
        "name": "rho",
        "category": "uniform",
        "search_space": {
            "low": 0,
            "high": 100,
        },
    },
]

maxIterations = 200
optimisationProblem = OptimizationProblem.from_list(optimizationProblemParameters)
parzenOptimiser = optimizers["parzen_estimator"](
    optimisationProblem
)  #'random' or 'parzen_estimator'
loss = 1e8
i = 0
while loss > 1e5:
    i += 1
    newParameterSuggestion = parzenOptimiser.suggest()
    loss = objectiveFunction(**newParameterSuggestion)
    parzenObservation = Observation.from_dict(
        {"loss": loss, "sample": newParameterSuggestion}
    )
    optimisationProblem.add_observation(parzenObservation)
    print(f"Run {i}")
    print(f"Loss: {loss}")

# objectiveFunction(
#     optimisationProblem.best_sample["x"], optimisationProblem.best_sample["p"]
# )
##
rawImage = readImage("image.jpg")
noisyImage = generateNoisyImage(rawImage, [1, 10000])
params = [
    optimisationProblem.best_sample["x"],
    optimisationProblem.best_sample["p"],
]

improvedImage = generateNoisyImage(rawImage, params)
plotImages(rawImage, noisyImage.astype(np.uint8), improvedImage.astype(np.uint8))
