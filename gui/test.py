import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#  Create an animation of a sine wave moving forward
#  and a cosine wave moving backward

#  First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
x = np.arange(0,3,0.1)
y = np.sin(x)
line, = ax.plot(x, y, lw=2)
# define update function
def update(num, x, y, line):
    # shift x along and plot the new line
    line.axes.axis([0, 2, -2, 2])
    return line,
# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, update, fargs=(x, y, line), frames=len(x), interval=20, blit=True)
plt.show()



