import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import customtkinter as tk
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

# TODO: make stuff look good
# TODO: the block colorisation: make it random? or are we using user input
# dark theme
tk.set_appearance_mode("dark")


class imageColoriser(tk.CTkFrame):
    # Internal attributes:
    # fileName
    # rawImage
    # grayImage
    # grayImageWithSomeColor (contextually dependant)

    # work in OOP
    def __init__(self, master=None):
        tk.CTkFrame.__init__(self, master)
        self.createWidgets()

    def createWidgets(self):
        mainWindowFigure = plt.figure(figsize=(6, 4))  # TODO: what size?
        self.mainPLTWindowTopLeft = mainWindowFigure.add_subplot(221)
        self.mainPLTWindowTopRight = mainWindowFigure.add_subplot(222)
        self.mainPLTWindowBottomLeft = mainWindowFigure.add_subplot(223)
        self.mainPLTWindowBottomRight = mainWindowFigure.add_subplot(224)
        self.mainPLTWindowAxes = [
            self.mainPLTWindowTopLeft,
            self.mainPLTWindowTopRight,
            self.mainPLTWindowBottomLeft,
            self.mainPLTWindowBottomRight,
        ]

        for axis in self.mainPLTWindowAxes:
            axis.axis("off")

        # define the canvas upon which we place the images
        self.canvas = FigureCanvasTkAgg(mainWindowFigure, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.canvas.draw()

        # define the buttons
        self.plotButton = tk.CTkButton(
            master=root, text="Choose Image", command=self.displayImage
        )
        self.grayButton = tk.CTkButton(
            master=root, text="Make Image Gray", command=self.convertGray
        )
        self.randomisedColorButton = tk.CTkButton(
            master=root, text="Add Colored Pixels", command=self.addRandomisedColor
        )
        self.manualColorButton = tk.CTkButton(
            master=root, text="Manually Color", command=self.manualColorPopupWindow
        )
        self.addBlockColorButton = tk.CTkButton(
            master=root, text="Add Color Block", command=self.addBlockColor
        )
        self.saveButton = tk.CTkButton(root, text="Save", command=self.savePicture)
        self.exitButton = tk.CTkButton(root, text="Exit", command=root.destroy)

        self.plotButton.grid(row=0, column=3)
        self.grayButton.grid(row=1, column=3)
        self.randomisedColorButton.grid(row=2, column=3)
        self.manualColorButton.grid(row=3, column=3)
        self.addBlockColorButton.grid(row=4, column=3)
        self.saveButton.grid(row=5, column=3)
        self.exitButton.grid(row=6, column=3)

    # select an image and show it
    def displayImage(self):
        # clear all axes; new image to be loaded
        for axis in self.mainPLTWindowAxes:
            axis.clear()
            axis.axis("off")
        rawImagePLTWindow = self.mainPLTWindowAxes[0]

        # load file
        fileName = tk.filedialog.askopenfilename(
            initialdir="../images/",
            title="Select A File",
            filetypes=(
                ("jpg files", "*.jpg"),
                ("jpeg files", "*.jpeg"),
                ("all files", "*.*"),
            ),
        )  # TODO: initialdir?

        # save file name to be referenced
        self.fileName = fileName

        if fileName:
            rawImage = mpimg.imread(fileName)
            self.rawImage = rawImage
            rawImagePLTWindow.imshow(rawImage)
            rawImagePLTWindow.axis("off")
            rawImagePLTWindow.set_title("Colored Image")
            self.canvas.draw()
        return

    def savePicture(self):
        self.canvas.figure.savefig("./image.png")  # TODO: might not work on windows?

    # convert image to grayscale
    def convertGray(self):
        grayImagePLTWindow = self.mainPLTWindowTopRight
        grayImagePLTWindow.clear()

        # convert to grayscale
        grayImage = np.dot(self.rawImage[..., :3], [0.299, 0.587, 0.114])

        # round to integers
        grayImage = np.round(grayImage).astype(np.uint8)
        self.grayImage = grayImage

        # show grayscale image
        grayImagePLTWindow.imshow(grayImage, cmap="gray")
        grayImagePLTWindow.axis("off")
        grayImagePLTWindow.set_title("Gray Image")
        self.canvas.draw()

    def dimensionalise(self, rawImage, grayImage):
        grayImage3D = np.stack((grayImage,) * 3, axis=-1)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*grayImage.shape) < percentage
        grayImage3D[mask, :] = rawImage[mask, :]

        grayImage3D = np.stack((grayImage,) * 3, axis=-1)
        return grayImage3D

    # add some color to the grayscale image
    def addRandomisedColor(self):
        randomisedColorPLTWindow = self.mainPLTWindowBottomLeft
        grayImage = self.grayImage
        rawImage = self.rawImage

        randomisedColorPLTWindow.clear()
        grayImageWithRandomColor = self.dimensionalise(rawImage, grayImage)

        # grid colorization
        I = 100
        J = 100

        xSize, ySize = grayImage.shape

        for x in np.linspace(0, xSize, I, dtype=int, endpoint=False):
            for y in np.linspace(0, ySize, J, dtype=int, endpoint=False):
                grayImageWithRandomColor[x, y, :] = self.rawImage[x, y, :]

        self.grayImageWithSomeColor = grayImageWithRandomColor
        randomisedColorPLTWindow.imshow(grayImageWithRandomColor)
        randomisedColorPLTWindow.axis("off")
        randomisedColorPLTWindow.set_title("Image with Some Color")
        self.canvas.draw()

    def addBlockColor(self):
        print("hi")

    def manualColorPopupWindow(self):
        popup = tk.CTkToplevel(self)

        popupWindowFigure = plt.figure(figsize=(6, 4))  # TODO: what size?
        popup.PLTWindow = popupWindowFigure.add_subplot(111)
        popup.PLTWindow.axis("off")

        popupCanvas = FigureCanvasTkAgg(popupWindowFigure, master=popup)
        popupCanvas.get_tk_widget().grid(row=0, column=1)
        popupCanvas.draw()

        gs = GridSpec(2, 3)

        popup.mainPLTWindow = popupWindowFigure.add_subplot(gs[0:2, 0:2])
        popup.colorWheelPLTWindow = popupWindowFigure.add_subplot(gs[0, 2])
        popup.chosenColorPLTWindow = popupWindowFigure.add_subplot(gs[1, 2])

        grayImageWithManualColor = self.dimensionalise(self.rawImage, self.grayImage)

        colorWheel = plt.imread("../images/color_wheel.jpeg")
        selectedColor = np.ones([2, 2, 3]) * 0

        popup.mainPLTWindow.imshow(grayImageWithManualColor)
        popup.colorWheelPLTWindow.imshow(colorWheel)
        popup.mainPLTWindow.axis("off")
        popup.colorWheelPLTWindow.axis("off")
        popup.chosenColorPLTWindow.axis("off")
        popup.chosenColorPLTWindow.imshow(selectedColor)

        nx, ny, d = grayImageWithManualColor.shape
        sc = [0, 0, 0]

        def onClick(event):
            global sc
            print("clicked")
            if event.inaxes == popup.mainPLTWindow:
                x, y = event.xdata, event.ydata
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                grayImageWithManualColor[y : y + 5, x : x + 5, :] = sc

                popup.mainPLTWindow.clear()
                popup.mainPLTWindow.imshow(grayImageWithManualColor)
                popup.mainPLTWindow.axis("off")

                self.mainPLTWindowBottomLeft.imshow(grayImageWithManualColor)

                self.grayImageWithSomeColor = grayImageWithManualColor
            if event.inaxes == popup.colorWheelPLTWindow:
                x, y = event.xdata, event.ydata
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                sc = colorWheel[y, x]
                selectedColor = np.tile(sc, (2, 2, 1))

                popup.chosenColorPLTWindow.imshow(selectedColor)
                popup.chosenColorPLTWindow.axis("off")

                print("selected color is ", sc)
                print(selectedColor.shape)
            popupWindowFigure.canvas.draw_idle()

        cid = popupWindowFigure.canvas.mpl_connect("button_press_event", onClick)

        self.mainPLTWindowBottomLeft.set_title("Image with Manual Color")

        popupCloseButton = tk.CTkButton(
            popup, text="Close Window", command=popup.destroy
        )
        saveImageButton = tk.CTkButton(
            popup, text="Write to Main", command=self.saveImage
        )

        popupCloseButton.grid(row=1, column=0)
        saveImageButton.grid(row=2, column=0)

    def saveImage(self):
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.CTk()
    app = imageColoriser(master=root)
    app.mainloop()
