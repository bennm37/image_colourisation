import matplotlib.pyplot as plt

# from benderopt.base import OptimizationProblem, Observation
# from benderopt.optimizer import optimizers
import numpy as np
from pathlib import Path
import matplotlib.image as mpimg
from gui.coloriser import Coloriser
import h5py
import numexpr as ne
from sys import getsizeof


def linalg_norm(a):
    sq_norm = ne.evaluate("sum(a**2,2)")
    del a
    return sq_norm


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
    return rawImage, grayImage, colorCoordinates, colorValues


# rim, gim, cc, cv = getInit("chipmunk.jpg")
# gc = np.indices([gim.shape[0], gim.shape[1]]).reshape(2, gim.shape[0] * gim.shape[1]).T
# gim2 = gim[:, :, 0]
delta, sigma1, sigma2, p = 0.01, 100, 100, 1
kernel = lambda x: np.exp(-(x**2))
# normalKernel = lambda x: np.exp(-(x**2))
params = {
    "delta": delta,
    "sigma1": sigma1,
    "sigma2": sigma1,
    "p": p,
    "kernel": lambda x: np.exp(-(x**2)),
}


def colorise(grayImage, colorCoordinates, colorValues, parameters):
    """grayImage should be of shape width x height x 3, colorCoordinates n x 2 ,
    colorValues n x 3"""
    width, height, d = grayImage.shape
    grayImage = grayImage[:, :, 0]
    grayCoordinates = np.indices([width, height]).reshape(2, width * height).T
    colorCoordinates = colorCoordinates
    colorValues = colorValues
    delta = parameters["delta"]
    sigma1 = parameters["sigma1"]
    sigma2 = parameters["sigma2"]
    p = parameters["p"]
    kernel = parameters["kernel"]

    image = np.zeros((width, height, 3))
    for i in range(3):
        KD = getK(colorCoordinates, colorCoordinates, grayImage)
        n = colorCoordinates.shape[0]
        a_s = np.linalg.solve(KD + delta * np.eye(n), colorValues[:, i])
        # K2 = self.getK(self.grayCoordinates, self.colorCoordinates)
        # debugging
        # print(f"{KD.shape=}")
        # print(f"{n=}")
        # print(f"{self.getK(self.grayCoordinates,self.colorCoordinates).shape=}")
        # print(f"{K2 = }")
        layer_i = getK(grayCoordinates, colorCoordinates, grayImage) @ a_s
        layer_i = layer_i.reshape(width, height)
        image[:, :, i] = layer_i
    return image.astype(np.uint16)


def getK(X, Y, grayImage):
    """Generates the kernel matrix for 2 lists of indicies X and Y. X and Y
    are lists of coordiantes of shape k x 2"""
    nx, ny = len(X), len(Y)
    # return np.random.rand(nx,ny)/1000
    print("doing norm")
    distXY = np.linalg.norm(
        X[:, np.newaxis].astype(np.int32) - Y[np.newaxis, :].astype(np.int32), axis=2
    )
    print("finished norm")
    grayX = grayImage[X[:, 0], X[:, 1]]
    grayY = grayImage[Y[:, 0], Y[:, 1]]
    grayXY = np.abs(
        grayX[:, np.newaxis].astype(np.int32) - grayY[np.newaxis, :].astype(np.int32)
    )
    return kernel(distXY / sigma1) * kernel(grayXY**p / sigma2)


def saveDifferences(fileName):
    rim, gim, cc, cv = getInit(fileName)
    gc = (
        np.indices([gim.shape[0], gim.shape[1]])
        .reshape(2, gim.shape[0] * gim.shape[1])
        .T
    )
    rim = None
    gim = None
    # gim2 = gim[:, :, 0]
    gc2 = gc[:, np.newaxis].astype(np.int32)
    cc2 = cc[np.newaxis, :].astype(np.int32)
    gc = None
    cc = None
    t = ne.evaluate("gc2-cc2")
    print("generatred t")
    gc2 = None
    cc2 = None
    print("working on x")
    x = linalg_norm(t)
    print("generated x")
    t = None
    return x
    # ne.evaluate("gc2-cc2")  # np.split(ne.evaluate("gc2-cc2"), 1000)
    # np.save("diffArray.npy", ne.evaluate("gc2 - cc2")=)
    # return np.einsum(
    #     "ijk,ijk->ij",
    #     ne.evaluate("gc2 - cc2"),
    #     ne.evaluate("gc2-cc2"),
    #     optimize="optimal",
    # )


x = saveDifferences("chipmunk.jpg")
# q = np.empty((1500000, 500))
# x = linalg_norm(t)
# del t
##
for i in range(0, len(t)):
    print(i)
    workingmat = t[0]
    del t[0]
    # print("deleted")
    np.save(
        f"./tmp/run{i}",
        np.einsum("ijk,ijk->ij", workingmat, workingmat, optimize="optimal"),
    )

# t = ne.evaluate("gc2-cc2")
##
# np.save("test_large_array_save.dat", t, allow_pickle=False)
##
# for i in range(0, x.shape[0]):
with h5py.File("test.h5", "a") as hf:
    dset = hf.create_dataset("voltage284", data=t, chunks=True)
    ##
with h5py.File("test.h5", "r") as f:
    # Print all root level object names (aka keys)
    # these can be group or dataset names
    print("Keys: %s" % f.keys())
    # get first object name/key; may or may NOT be a group
    a_group_key = list(f.keys())[0]

    # get the object type for a_group_key: usually group or dataset
    print(type(f[a_group_key]))

    # If a_group_key is a group name,
    # this gets the object names in the group and returns as a list
    data = list(f[a_group_key])

    # If a_group_key is a dataset name,
    # this gets the dataset values and returns as a list
    data = list(f[a_group_key])
    # preferred methods to get dataset values:
    ds_obj = f[a_group_key]  # returns as a h5py dataset object
    ds_arr = f[a_group_key][()]  # returns as a numpy array
##
tt = cc[np.newaxis, :].astype(np.int32)
##
z = np.subtract(t, tt)
print("done")
##
t = getK(gc, cc, gim2)
print("done!")

##
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
        "kernel": normalKernel,
    }
    rawImage = readImage(fileName)
    c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
    colorImage = c.kernelColorise()
    # colorImage, kd = c.kernelColorise()
    # noisyImage = generateNoisyImage(rawImage, parameters)
    costOnIteration = generateCosts(rawImage, colorImage)
    return costOnIteration, colorImage


##

import cProfile
import pstats

parameters = {
    "delta": 1e-4,  # 0.01,
    "sigma1": 90,  # 100,
    "sigma2": 104,  # 100,
    "p": 0.5,  # 1,
    "kernel": normalKernel,
}
rawImage = readImage(fileName)

with cProfile.Profile() as pr1:
    c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
    colorImage = c.kernelColorise()
stats1 = pstats.Stats(pr1)
stats1.sort_stats(pstats.SortKey.TIME)
stats1.print_stats()

##
with cProfile.Profile() as pr:
    c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
    colorImage2 = c.kernelColorise()
stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()
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
            "low": 60,
            "high": 150,
            "step": 1,
        },
    },
    {
        "name": "sigma2",
        "category": "uniform",
        "search_space": {
            "low": 60,
            "high": 150,
            "step": 1,
        },
    },
    {
        "name": "rho",
        "category": "uniform",
        "search_space": {
            "low": 0.1,
            "high": 1,
            "step": 0.1,
        },
    },
]

maxIterations = 200
optimisationProblem = OptimizationProblem.from_list(RBFProblemParameters)
parzenOptimiser = optimizers["parzen_estimator"](
    optimisationProblem
)  #'random' or 'parzen_estimator'
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


##
parameters = {
    "delta": 1e-4,  # 0.01,
    "sigma1": 149,  # 100,
    "sigma2": 108,  # 100,
    "p": 0.2,  # 1,
    "kernel": normalKernel,
}
rawImage = readImage(fileName)
c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
colorImage = c.kernelColorise()
generateCosts(rawImage, colorImage)
##
plotImages(grayImage, rawImage, colorImage)
##
