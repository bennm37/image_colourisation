import numpy as np 
import matplotlib.pyplot as plt
def grayscale(img):
    img_gray = np.dot(img[...,:3], [0.299, 0.587, 0.114]).astype(int)
    new_img_gray = np.stack((img_gray,)*3,axis=-1)
    assert(np.all(new_img_gray[:,:,0]==img_gray))
    assert(np.all(new_img_gray[:,:,1]==img_gray))
    assert(np.all(new_img_gray[:,:,2]==img_gray))
    return new_img_gray

