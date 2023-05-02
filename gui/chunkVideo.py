import skvideo.io  
import numpy as np
import os 
import shutil

def sanitize(path):
    return path.split("/")[-1].split(".")[0]

def chunk(videopath,length=100):
    start,stop = 2000,3000
    length = int(length)
    videofolder = videopath.split("/")[-2]
    print(videofolder)
    videodata = skvideo.io.vread(videopath)[start:stop]
    T,nx,ny,d = videodata.shape
    print(T,nx,ny)
    nChunks = T//length
    times = np.arange(0,T,length,dtype=int)
    foldername = sanitize(videopath)
    try:
        os.mkdir(f"{videofolder}/{foldername}")
    except FileExistsError:
        shutil.rmtree(f"{videofolder}/{foldername}")
        os.mkdir(f"{videofolder}/{foldername}")
    for i,time in enumerate(times):
        print(f"Writing chunk {i+10}/{nChunks}")
        truncData = videodata[time:time+length,:,:,:]
        skvideo.io.vwrite(f"{videofolder}/{foldername}/chunk{i}.mp4",truncData)  
    
if __name__ == "__main__":
    print("Chunking Looney")
    chunk("./videos/looney.mp4")