import numpy as np

dimx,dimy,dimt =2,3,4
N = dimt*dimx*dimy
vid = np.linspace(0,N-1,N).reshape(dimt,dimx,dimy)
for i in range(N):
    a = i//(dimx*dimy)
    k = i%(dimx*dimy)
    b = k%dimx
    c = k//dimx
    print(a,b,c)
    print(vid[a,b,c])