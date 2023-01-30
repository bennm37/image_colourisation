import tkinter as tk
import numpy as np
import tkinter.messagebox
from pathlib import Path
import matplotlib.image as mpimg
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
# TODO work out what's happening with the columns in sidebarframe and get "edit" "file" and "appearance" labels to center better
# TODO make label backgrounds less chunky
# TODO make sliders line up and longer
# TODO make label background color change with appearance mode
class imageColoriser(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("MMSC Image Colouriser")
        self.geometry(f"{1000}x{580}")
        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.grid_columnconfigure((4, 5, 6, 7, 8), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # initial default values
        self.imagePath = "../images/apple.jpeg"
        self.statePath = "../states/apple.pkl"
        self.colorMode = tk.IntVar(value=0)
        self.labelColor = "#525252"

        # create sidebar and widgets
        self.sidebarFrame = ctk.CTkFrame(
            self, width=150, corner_radius=0
        )  # width doesn't do anything ?
        self.sidebarFrame.grid(row=0, column=0, rowspan=4, columnspan=1, sticky="nsew")
        self.sidebarFrame.grid_rowconfigure(16, weight=1)

        self.nextFrame = ctk.CTkFrame(
            self, width=150, corner_radius=0
        )  # width doesn't do anything ?
        self.nextFrame.grid(row=0, column=1, rowspan=4, columnspan=1, sticky="nsew")
        self.nextFrame.grid_rowconfigure(16, weight=1)

        ##### my stuff
        mainWindowFigure = plt.figure(figsize=(7, 7))  # TODO: what size?
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
        self.canvas = FigureCanvasTkAgg(mainWindowFigure, self.nextFrame)
        self.canvas.get_tk_widget().pack(side="top", padx=4, pady=4)
        self.canvas.draw()
        #####
        # file section
        self.title_padx = 30  # padding for titles
        self.fileLabel = ctk.CTkLabel(
            self.sidebarFrame, text="File", anchor="center", fg_color=self.labelColor
        )
        self.fileLabel.grid(
            row=0, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )
        self.loadImageButton = ctk.CTkButton(
            self.sidebarFrame, command=self.loadImage, text="Load Image"
        )
        self.loadImageButton.grid(row=1, column=0, padx=5, pady=5)
        self.loadImagePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.imagePath
        )
        self.loadImagePath.grid(row=1, column=1, columnspan=4, padx=10, pady=5)
        self.saveImageButton = ctk.CTkButton(
            self.sidebarFrame, command=self.saveImage, text="Save Image"
        )
        self.saveImageButton.grid(row=2, column=0, padx=20, pady=5)
        self.saveImagePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.imagePath
        )
        self.saveImagePath.grid(row=2, column=1, columnspan=4, padx=10, pady=5)
        self.loadStateButton = ctk.CTkButton(
            self.sidebarFrame, command=self.loadState, text="Load State"
        )
        self.loadStateButton.grid(row=3, column=0, padx=20, pady=5)
        self.loadStatePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.statePath
        )
        self.loadStatePath.grid(row=3, column=1, columnspan=4, padx=10, pady=5)
        self.saveStateButton = ctk.CTkButton(
            self.sidebarFrame, command=self.saveState, text="Save State"
        )
        self.saveStateButton.grid(row=4, column=0, padx=20, pady=5)
        self.saveStatePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.statePath
        )
        self.saveStatePath.grid(row=4, column=1, columnspan=4, padx=10, pady=5)

        # edit section
        self.editLabel = ctk.CTkLabel(
            self.sidebarFrame, text="Edit", anchor="center", fg_color=self.labelColor
        )
        self.editLabel.grid(
            row=5, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )
        self.colorByPixel = ctk.CTkRadioButton(
            self.sidebarFrame, text="Color by Pixel", variable=self.colorMode, value=0
        )
        self.colorByPixel.grid(row=6, column=0, pady=10, padx=20, sticky="nw")

        self.colorRandomPixels = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color Random Pixels",
            variable=self.colorMode,
            value=1,
            command=self.addRandomisedColor,
            state=ctk.DISABLED,
        )
        self.colorRandomPixels.grid(row=9, column=0, pady=10, padx=20, sticky="nw")
        self.NRandomPixelsSlider = ctk.CTkSlider(
            self.sidebarFrame, from_=0, to=1, number_of_steps=20
        )
        self.NRandomPixelsSlider.grid(
            row=10, column=0, columnspan=5, padx=(100, 5), pady=(5, 5), sticky="ew"
        )
        self.NRandomPixelEntry = ctk.CTkEntry(
            self.sidebarFrame, width=50, placeholder_text="20"
        )
        self.NRandomPixelEntry.grid(row=10, column=0, padx=40, pady=(5, 5), sticky="w")
        self.NRandomPixelLabel = ctk.CTkLabel(self.sidebarFrame, text="N")
        self.NRandomPixelLabel.grid(row=10, column=0, padx=20, pady=(5, 5), sticky="w")

        ####
        self.colorByGrid = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color by Grid",
            command=self.addBlockColor,
            variable=self.colorMode,
            value=2,
            state=ctk.DISABLED,
        )
        self.colorByGrid.grid(row=11, column=0, pady=10, padx=20, sticky="nw")
        #####
        # parameter section
        self.parameterLabel = ctk.CTkLabel(
            self.sidebarFrame,
            text="Parameters",
            anchor="center",
            fg_color=self.labelColor,
        )
        self.parameterLabel.grid(
            row=12, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )
        self.RhoSlider = ctk.CTkSlider(
            self.sidebarFrame, from_=0, to=1, number_of_steps=20
        )
        self.RhoSlider.grid(
            row=13, column=0, columnspan=5, padx=(100, 5), pady=(5, 5), sticky="ew"
        )
        self.RhoLabel = ctk.CTkLabel(self.sidebarFrame, text="Rho")
        self.RhoLabel.grid(row=13, column=0, padx=50, pady=(5, 5), sticky="w")
        self.BetaSlider = ctk.CTkSlider(
            self.sidebarFrame, from_=0, to=1, number_of_steps=20
        )
        self.BetaSlider.grid(
            row=14, column=0, columnspan=5, padx=(100, 5), pady=(5, 5), sticky="ew"
        )
        self.BetaLabel = ctk.CTkLabel(self.sidebarFrame, text="Beta")
        self.BetaLabel.grid(row=14, column=0, padx=50, pady=(5, 5), sticky="w")

        # appearance section
        self.appearanceLabel = ctk.CTkLabel(
            self.sidebarFrame, text="Misc", anchor="center", fg_color=self.labelColor
        )
        self.appearanceLabel.grid(
            row=15, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )
        self.appearanceOptionMenu = ctk.CTkOptionMenu(
            self.sidebarFrame,
            values=["Light", "Dark", "System"],
            command=self.changeAppearanceEvent,
        )
        self.appearanceOptionMenu.grid(
            row=16, column=0, columnspan=1, padx=20, pady=(10, 10)
        )
        self.appearanceOptionMenu.set("Dark")
        self.exitButton = ctk.CTkButton(
            self.sidebarFrame, text="Exit", command=self.destroy
        )
        #
        self.exitButton.grid(row=16, column=1)

    def setDefaults(self):
        self.imagePath = "../images/apple.jpeg"
        self.statePath = "../states/apple.pkl"
        self.colorMode = tk.IntVar(value=0)

    # MORE OF MY STUFF
    ####
    def dimensionalise(self, rawImage, grayImage):
        grayImage3D = np.stack((grayImage,) * 3, axis=-1)

        # replace the pixels of the grayscale image with the pixels of the original image
        percentage = 0.1
        mask = np.random.rand(*grayImage.shape) < percentage
        grayImage3D[mask, :] = rawImage[mask, :]

        grayImage3D = np.stack((grayImage,) * 3, axis=-1)
        return grayImage3D

    def addRandomisedColor(self):
        if self.rawImageExists == 0:
            pass
        else:
            self.grayImageWithSomeColorExists = 0
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
            self.grayImageWithSomeColorExists = 1
            randomisedColorPLTWindow.imshow(grayImageWithRandomColor)
            randomisedColorPLTWindow.axis("off")
            randomisedColorPLTWindow.set_title("Image with Some Color")
            self.canvas.draw()

    def addBlockColor(self):
        if self.rawImageExists == 0:
            pass
        else:
            self.grayImageWithSomeColorExists = 0

            blockColorPLTWindow = self.mainPLTWindowBottomLeft
            blockColorPLTWindow.clear()

            grayImage = self.grayImage
            rawImage = self.rawImage

            xSize, ySize, null = rawImage.shape
            yStart = np.random.randint(0, ySize - 50)
            xStart = np.random.randint(0, xSize - 50)
            grayImageWithBlockColor = self.dimensionalise(rawImage, grayImage)

            def addColorBox(xStart, xEnd, yStart, yEnd):
                for i in range(xStart, xEnd):
                    for j in range(yStart, yEnd):
                        grayImageWithBlockColor[i, j, :] = rawImage[i, j, 0:3]

            addColorBox(xStart, xStart + 50, yStart, yStart + 50)
            self.grayImageWithSomeColorExists = 1

            blockColorPLTWindow.axis("off")
            blockColorPLTWindow.imshow(grayImageWithBlockColor)
            blockColorPLTWindow.set_title("Image with Block Color")
            self.canvas.draw()

    def loadImage(self):
        self.grayImageExists = 0
        self.rawImageExists = 0
        self.grayImageWithSomeColorExists = 0

        # clear all axes; new image to be loaded
        for axis in self.mainPLTWindowAxes:
            axis.clear()
            axis.axis("off")
        rawImagePLTWindow = self.mainPLTWindowAxes[0]

        # load file
        fileName = ctk.filedialog.askopenfilename(
            initialdir=str(Path("..", "images")),
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
            self.rawImageExists = 1
            rawImagePLTWindow.imshow(rawImage)
            self.mainPLTWindowBottomRight.imshow(rawImage)
            self.mainPLTWindowTopRight.imshow(rawImage)
            rawImagePLTWindow.axis("off")
            rawImagePLTWindow.set_title("Colored Image")
            self.canvas.draw()

        self.grayImageWithSomeColorExists = 0
        grayImagePLTWindow = self.mainPLTWindowTopRight
        grayImagePLTWindow.clear()

        # convert to grayscale
        grayImage = np.dot(self.rawImage[..., :3], [0.299, 0.587, 0.114])

        # round to integers
        grayImage = np.round(grayImage).astype(np.uint8)
        self.grayImage = grayImage
        self.grayImageExists = 1

        # show grayscale image
        grayImagePLTWindow.imshow(grayImage, cmap="gray")
        grayImagePLTWindow.axis("off")
        grayImagePLTWindow.set_title("Gray Image")
        self.canvas.draw()
        self.colorByGrid.configure(state=ctk.NORMAL)
        self.colorRandomPixels.configure(state=ctk.NORMAL)
        return

    ###
    def saveImage(self):
        print("Save Image")

    def loadState(self):
        print("Load State")

    def saveState(self):
        print("Save State")

    def changeAppearanceEvent(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode.lower() == "light" or "system":
            self.labelColor = "#B2B2B2"
        if new_appearance_mode.lower() == "dark":
            self.labelColor = "#525252"
        # TODO this is clunky, how can you do this more systematically
        self.fileLabel.configure(fg_color=self.labelColor)
        self.editLabel.configure(fg_color=self.labelColor)
        self.parameterLabel.configure(fg_color=self.labelColor)
        self.appearanceLabel.configure(fg_color=self.labelColor)


if __name__ == "__main__":
    app = imageColoriser()
    app.mainloop()
