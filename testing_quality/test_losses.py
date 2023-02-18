import os
from gui.coloriserGUI import Coloriser
import numexpr as ne
import glob

# Zella's Magic
import matplotlib.pyplot as plt

# from benderopt.base import OptimizationProblem, Observation
# from benderopt.optimizer import optimizers
import numpy as np
import pathlib
import matplotlib.image as mpimg

mainDirectory = pathlib.Path(__file__).parent.parent  # directory containing main files
##


class test_coloriser_taxi(Coloriser):
    # initialize class as usual
    def __init__(self, grayImage, colorCoordinates, colorValues, parameters):
        super().__init__(grayImage, colorCoordinates, colorValues, parameters)

    # override the method to compute K
    # use Manhattan distance
    def getColK(self, x, y, col):

        colXY_taxi = self.taxi_norm(x[:], y[col])
        dist_kernel = ne.evaluate(
            "exp(-colXY_taxi / (s1)**2)",
            local_dict={
                "colXY_taxi": colXY_taxi,
                "s1": self.sigma1,
            },
        )

        grayX = self.grayImage[x[:, 0], x[:, 1]].astype(np.float64)
        grayY = self.grayImage[y[:, 0], y[:, 1]].astype(np.float64)

        grayXY_dist = abs(grayX[:] - grayY[col])
        gray_kernel = ne.evaluate(
            "exp(-grayXY_dist / (s2)**2)",
            local_dict={
                "grayXY_dist": grayXY_dist,
                "s2": self.sigma2,
            },
        )

        return ne.evaluate("dist_kernel * gray_kernel")

    @staticmethod
    def taxi_norm(x, y):
        return np.sum(np.abs(x - y), axis=1)


class test_coloriser_normalized(Coloriser):
    # initialize class as usual
    def __init__(self, grayImage, colorCoordinates, colorValues, parameters):
        super().__init__(grayImage, colorCoordinates, colorValues, parameters)

    # override the method to compute K
    # normalize the lenght of the vectors
    def getColK(self, x, y, col):

        # normalize the vectors to the lenght and width of the image
        colXY = (x[:] - y[col]) / np.array([self.width, self.height])

        # colXY = x[:] - y[col]
        distXYKernelised = ne.evaluate(
            "exp(-distSquared / (s1)**2)",
            local_dict={
                "distSquared": ne.evaluate("sum(colXY**2,1)"),
                "s1": self.sigma1,
            },
        )

        grayX = self.grayImage[x[:, 0], x[:, 1]].astype(np.float64)
        grayY = self.grayImage[y[:, 0], y[:, 1]].astype(np.float64)
        grayXY_dist = abs(grayX[:] - grayY[col])
        gray_kernel = ne.evaluate(
            "exp(-grayXY_dist / (s2)**2)",
            local_dict={
                "grayXY_dist": grayXY_dist,
                "s2": self.sigma2,
            },
        )

        return ne.evaluate("distXYKernelised * gray_kernel")


def readImage(name):
    fileName = pathlib.Path(".", "allims", name)
    rawImage = mpimg.imread(fileName)
    rawImage = np.round(rawImage).astype(np.uint8)
    return rawImage


def generateCosts(rawImage, noisyImage):
    actualImage = rawImage.astype(np.float64)
    guessImage = noisyImage.astype(np.float64)
    differences = np.abs(actualImage - guessImage)
    rDiff = np.sum(differences[:, :, 0] * 0.299)
    gDiff = np.sum(differences[:, :, 1] * 0.587)
    bDiff = np.sum(differences[:, :, 2] * 0.114)
    finalDiff = rDiff + gDiff + bDiff
    return finalDiff / (rawImage.shape[0] * rawImage.shape[1])


def getInit(fileName):
    imageToRead = pathlib.Path(mainDirectory, folder_name, fileName)
    rawImage = plt.imread(imageToRead)
    print(imageToRead)
    if rawImage.dtype == "float32":
        if fileName.endswith(".jpg") or fileName.endswith(".jpeg"):
            rawImage = (rawImage * 255).astype(np.uint8)
    if fileName.endswith(".png"):
        # remove transparency, convert to white
        if rawImage.shape[2] == 4:
            for i in np.argwhere(rawImage[:, :, 3] != 1):
                rawImage[i[0], i[1], :] = 1.0
        rawImage = rawImage[:, :, :3] * 255
        rawImage = rawImage.astype(np.uint64)
    grayImage = np.dot(rawImage[..., :3], [0.299, 0.587, 0.114])
    grayImage = np.round(grayImage).astype(np.uint16)  # 16 or 8?
    grayImage = np.stack((grayImage,) * 3, axis=-1).astype(np.int64)
    xSize, ySize, d = grayImage.shape
    NRandomPixelsMax = 50
    # get random indices to eventually color in
    randomIndices = np.random.default_rng().choice(
        xSize * ySize, size=int(NRandomPixelsMax), replace=False
    )

    # define the coordinate pairs which we will color;
    # returns an array formatted as [[x0,y0],[x1,y1]...]
    randomCoordinates = np.array(
        [[index % xSize, index // xSize] for index in randomIndices]
    )

    colorCoordinates = randomCoordinates
    colorValues = rawImage[randomCoordinates[:, 0], randomCoordinates[:, 1]]
    return rawImage, grayImage, colorCoordinates, colorValues


def test_colorise(file_name):

    rawImage, grayImage, colorCoordinates, colorValues = getInit(file_name)

    # rawImage = readImage(file_name)

    normalKernel = lambda x: np.exp(-(x**2))

    parameters = {
        "delta": 1e-4,  # 0.01,
        "sigma1": 100,  # 100,
        "sigma2": 100,  # 100,
        "p": 0.2,  # 1,
        "kernel": normalKernel,
    }

    c = Coloriser(grayImage, colorCoordinates, colorValues, parameters)
    colorImage = c.kernelColoriseColumnal()

    # save the colorized image
    savePath = pathlib.Path(mainDirectory, "results", file_name)
    plt.imsave(savePath, colorImage)

    # Uncomment below to show images as they are generated!
    # plt.imshow(colorImage)
    # plt.show()

    return generateCosts(rawImage, colorImage)


if __name__ == "__main__":
    # To run just create 2 folders in the 'image_colourisation'
    # project:
    # Folder 1: to contain all output images. This must be called "results"
    # Folder 2: another folder containing all images to test. Enter its name
    # under the `folder_name` variable.

    folder_name = "allims"
    # clean results folder first before every run.
    resultsFolder = pathlib.Path(mainDirectory, "results")
    filesToDelete = glob.glob(str(pathlib.Path(resultsFolder, "*")))
    for f in filesToDelete:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

    file_names = os.listdir(pathlib.Path(mainDirectory, folder_name))
    results = np.zeros(len(file_names))
    worst = 0
    worst_index = -1
    best = np.inf
    best_index = -1

    for i, file_name in enumerate(file_names):
        print(f"on {file_name}, run {i}")
        results[i] = test_colorise(file_name)
        if results[i] > worst:
            worst = results[i]
            worst_index = i
        if results[i] < best:
            best = results[i]
            best_index = i

    print("Worst image: ", file_names[worst_index], " with loss: ", worst)
    print("Best image: ", file_names[best_index], " with loss: ", best)
    print("Average loss: ", np.mean(results))
    print("Standard deviation: ", np.std(results))
