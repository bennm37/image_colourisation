from coloriserGUI import *
import matplotlib.pyplot as plt
import time 
import pandas as pd
import tracemalloc
import os.path
pd.set_option("display.max.columns", None)

def prepImage(rawImage):
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
    colorCoordinates = randomCoordinates
    colorValues = rawImage[randomCoordinates[:, 0], randomCoordinates[:, 1]]
    return grayImage, colorCoordinates, colorValues

def compareColorisers(filename,nTests = 10,nTrials = 3,small=100,large=100):
    rawImage = plt.imread(filename)
    rawImage = (256*rawImage).astype(np.float64)
    if large>np.min(rawImage.shape[0:2]):
        large = np.min(rawImage.shape[0:2])
    if small <0:
        small = 0 
    large,small = int(large),int(small)
    sizes = np.linspace(small,large,nTests,dtype=int)
    times = np.zeros((nTests,nTrials,2))
    memory = np.zeros((nTests,nTrials,2))
    tracemalloc.start()
    for i in range(nTests):
        print(f"Starting Test {i}")
        testImage = rawImage[:sizes[i],:sizes[i]]
        grayImage, colorCoordinates, colorValues = prepImage(testImage)
        normalKernel = lambda x: np.exp(-x**2)
        parameters = {
            "delta": 0.01,
            "sigma1": 150,
            "sigma2": 150,
            "p": 1,
            "kernel": normalKernel,
        }
        c = Coloriser(grayImage, colorCoordinates, colorValues,parameters,verbose=False)
        for j in range(nTrials):
            print(f"Running trial {i}.{j}")
            # memory and time of fast method
            startFast = time.perf_counter()
            image = c.kernelColoriseColumnal()
            endFast = time.perf_counter()
            current,memFast = tracemalloc.get_traced_memory()
            tracemalloc.clear_traces()

            # memory and time of large method
            startLarge = time.perf_counter()
            image = c.kernelColoriseColumnalLarge()
            endLarge = time.perf_counter()
            current,memLarge = tracemalloc.get_traced_memory()
            tracemalloc.clear_traces()

            times[i,j,0] = endFast-startFast
            times[i,j,1] = endLarge-startLarge
            memory[i,j,0] = memFast
            memory[i,j,1] = memLarge
    memory /= 1024**2 # mesure in MB
    return sizes**2,times,memory

def saveResults(nPixels,times,memory,filename="test"):
    nTests = len(nPixels)
    averageTimes = np.mean(times,axis=1)
    stdTimes = np.std(times,axis=1)
    averageMemory = np.mean(memory,axis=1)
    stdMemory = np.std(memory,axis=1)
    data = np.concatenate([nPixels.reshape(nTests,1),averageTimes],axis=1)
    data = np.concatenate([data,stdTimes],axis=1)
    data = np.concatenate([data,averageMemory],axis=1)
    data = np.concatenate([data,stdMemory],axis=1)
    df = pd.DataFrame(data,columns=["nPixels","averageFastTimes","averageLargeTimes","stdFastTimes","stdLargeTimes","averageFastMemory","averageLargeMemory","stdFastMemory","stdLargeMemory"])
    name = sanitize(filename)
    resultsName = f"./data/{name}BenchmarkingResults.txt"
    i = 1
    while os.path.isfile(resultsName):
        resultsName = f"./data/{name}BenchmarkingResults{i}.txt"
        i+=1
    df.to_csv(resultsName,index=False)
    return resultsName
    
def sanitize(filename):
    return filename.split("/")[-1].split(".")[0]

def plotResults(resultsName):
    df = pd.read_csv(resultsName)
    fig,ax = plt.subplots(1,2)
    fig.suptitle("Benchmarking Performance of 2 Implementations")
    fig.set_size_inches(10,5)
    ax[0].scatter(df["nPixels"],df["averageFastTimes"])
    ax[0].errorbar(df["nPixels"],df["averageFastTimes"],yerr=df["stdFastTimes"],label="Fast Times")
    ax[0].scatter(df["nPixels"],df["averageLargeTimes"])
    ax[0].errorbar(df["nPixels"],df["averageLargeTimes"],yerr=df["stdLargeTimes"],label="Large Times")
    ax[0].legend()
    ax[0].set_yscale("log")
    ax[0].set(xlabel="# Pixels",ylabel="Time (s)",title="Time")

    ax[1].scatter(df["nPixels"],df["averageFastMemory"])
    ax[1].errorbar(df["nPixels"],df["averageFastMemory"],yerr=df["stdFastMemory"],label="Fast Memory")
    ax[1].scatter(df["nPixels"],df["averageLargeMemory"])
    ax[1].errorbar(df["nPixels"],df["averageLargeMemory"],yerr=df["stdLargeMemory"],label="Large Memory")
    ax[1].legend()
    ax[1].set_yscale("log")
    ax[1].set(xlabel="# Pixels",ylabel="Memory (MB)",title="Memory")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    filename = "./images/fresco.png"
    # nPixels,times,memory = compareColorisers("./images/fresco.png",nTests=10,nTrials=3,small=25,large=800)
    # resultsName = saveResults(nPixels,times,memory,filename)
    plotResults("data/testBenchmarkingResults3.txt")
    df = pd.read_csv("data/testBenchmarkingResults3.txt")
    print(df["stdFastTimes"])