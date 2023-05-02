# import numpy as np 
# import matplotlib.pyplot as plt 
# import skvideo.io

# videopath = "videos/looney/chunk5.mp4"
# videodata = skvideo.io.vread(videopath)
# sampleRate = 10 
# fig,ax = plt.subplots(subplot_kw={"projection":"3d"})
# ax.imshow(videodata[0,:,:],extent=[0,1,0,1])
# # ax.axis("off")
# plt.show()

import numpy as np
import skvideo.io
# from skimage import io

# vol = io.imread("https://s3.amazonaws.com/assets.datacamp.com/blog_assets/attention-mri.tif")
# volume = vol.T
# r, c = volume[0].shape
videopath = "videos/looney/chunk1.mp4"
videodata = skvideo.io.vread(videopath)
volume = np.dot(videodata[..., :3], [0.299, 0.587, 0.114]).astype(np.uint16)
# grayVideo = np.stack([grayVideo]*3,axis=-1)
r,c = volume[0].shape
# Define frames
import plotly.graph_objects as go
nb_frames = 68
layout = {'xaxis': {
    'range':[0,r],
    'showgrid': False, # thin lines in the background
    'zeroline': False, # thick line at x=0
    'visible': False,  # numbers below
},
'yaxis': {
    'range':[0,c],
    'showgrid': False, # thin lines in the background
    'zeroline': False, # thick line at x=0
    'visible': False,  # numbers below
}}
fig = go.Figure(frames=[go.Frame(data=go.Surface(
    z=(6.7 - k * 0.1) * np.ones((r, c)),
    surfacecolor=np.flipud(volume[67 - k]),
    cmin=0, cmax=200
    ),
    name=str(k) # you need to name the frame for the animation to behave properly
    )
    for k in range(nb_frames)],
    layout=layout)

# Add data to be displayed before animation starts
# For Black and White
# for i in range(7):
#     # print(volume.shape)
#     fig.add_trace(go.Surface(
#         z=i * np.ones((r, c)),
#         surfacecolor=np.flipud(volume[i*10]),
#         colorscale='Gray',
#         cmin=0, cmax=200,
#         colorbar=dict(thickness=20, ticklen=4),
#         opacity = 0.7
#         ))

# For RGB
colors = ['reds','greens','blues']
for k in range(3):
    print(f"Starting {colors[k]}")
    for i in range(1):
        # print(volume.shape)
        fig.add_trace(go.Surface(
            z=k * np.ones((r, c)),
            surfacecolor=np.flipud(videodata[i*10,:,:,k]),
            colorscale=colors[k],
            cmin=0, cmax=200,
            colorbar=dict(thickness=20, ticklen=4),
            opacity = 0.7
            ))
fig.show()
