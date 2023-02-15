import tkinter as tk
import customtkinter as ctk
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib as mpl
import itertools
import pathlib
import numpy as np
import coloriserGUI as Coloriser
import popupWaitingWindow as waitingWindowClass

mainDirectory = pathlib.Path(__file__).parent.parent  # directory containing main files
# NOTE:
# image takes [y,x,:]
# -> coords must be [y,x]

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# TODO work out what's happening with the columns in sidebarframe and get "edit" "file" and "appearance" labels to center better
# TODO make label backgrounds less chunky
# TODO make sliders line up and longer
# TODO: fix all the default stuff


class imageColoriser(ctk.CTkFrame):
    def __init__(self, master=None):
        # super().__init__()
        ctk.CTkFrame.__init__(self, master)
        self.createUI()

    def createUI(self):
        # configure window
        root.grid_columnconfigure((1, 2, 3), weight=1)
        root.grid_columnconfigure((4, 5, 6, 7, 8), weight=1)
        root.grid_rowconfigure((0, 1, 2), weight=1)

        # initial default values
        # TODO in setdefaults or similar ?
        self.rawImageExists = 0
        self.grayImageWithSomeColorExists = 0
        self.fileName = "Select file"
        self.statePath = "../states/apple.pkl"
        self.colorMode = tk.IntVar(value=1)
        self.labelColor = ("#B2B2B2", "#525252")
        self.brushSizeMin = 0
        self.brushSizeMax = 20
        self.colorFrameColor = "gray17"
        self.selectedColors = ["#000000", "#FFFFFF", "#2596BE"]
        self.selectedColorButtonVar = 2
        # TODO: set these next values??
        self.NRandomPixels = 1000
        self.NRandomPixelsMax = 5000
        self.colorRangeSliderInitial = 0.67
        self.deltaEntry = ctk.StringVar(value="1e-4")
        self.rhoEntry = ctk.StringVar(value="0.5")
        self.sigma1Entry = ctk.StringVar(value="100")
        self.sigma2Entry = ctk.StringVar(value="100")

        self.deltaValue = 1e-4
        self.rhoValue = 0.5
        self.sigma1Value = 100
        self.sigma2Value = 100

        # styling
        fpath = pathlib.Path(
            mpl.get_data_path(),
            "/Users/benn-m/Documents/image_colourisation/gui/fonts/Roboto-Medium.ttf",
        )
        self.captionFont = fpath
        self.captionFontDict = {
            "family": fpath,
            "color": "white",
            "weight": "normal",
            "size": 5,
        }
        self.frameDark3 = "#323333"
        self.frameLight3 = "#CFD0CF"

        # define image frame

        self.generateFrames()

        self.generateFileSection()

        self.generateEditSection()

        self.generateParameterSection()

        self.generateAppearanceSection()

    def setDefaults(self):
        self.fileName = "Select file"
        self.statePath = "../states/apple.pkl"
        self.brushSizeMax = 30
        self.brushSizeMin = 1
        self.brushSize = 10
        self.NRandomPixelsSlider.set(self.NRandomPixels)

    def setColorRange(self, sliderVal, size=40):
        size = 30
        color = np.array(self.rainbow(sliderVal)[:3]) * 255
        color = color.astype(np.uint16)

        t = np.linspace(0, 1, size)
        colorscale = color[np.newaxis, :] * t[:, np.newaxis]
        colorscale = colorscale[:, np.newaxis, :] * t[np.newaxis, :, np.newaxis]
        colorscale = colorscale.astype(np.uint16)

        white = np.array([255, 255, 255])

        grayscale = white[np.newaxis, :] * t[:, np.newaxis]
        grayscale = (
            grayscale[:, np.newaxis, :]
            - grayscale[:, np.newaxis, :] * t[np.newaxis, :, np.newaxis]
        )
        grayscale = grayscale.astype(np.uint16)

        self.colorGrid = grayscale + colorscale
        self.colorGrid = self.colorGrid[::-1]

        self.colorSelectorWindow.imshow(self.colorGrid, interpolation="bilinear")
        self.colorSelectorCanvas.draw_idle()

        # TODO work out how to set slider blob colour to change not slider background
        self.colorRangeSlider.configure(
            button_color="#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
        )  # convert to hex
        self.colorRangeSlider.configure(
            button_hover_color="#{:02x}{:02x}{:02x}".format(
                color[0], color[1], color[2]
            )
        )  # convert to hex

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
            initialdir=str(pathlib.Path(mainDirectory, "images")),
            title="Select A File",
            filetypes=(
                ("jpg files", "*.jpg"),
                ("png files", "*.png"),
                ("jpeg files", "*.jpeg"),
                ("all files", "*.*"),
            ),
        )

        # save file name to be referenced
        self.fileName = fileName

        self.loadImagePath.configure(placeholder_text=self.fileName)

        if fileName:
            rawImage = mpimg.imread(fileName)
            # special case with pngs
            if fileName.endswith(".png"):
                rawImage = rawImage[:, :, :3] * 255
                rawImage = rawImage.astype(np.uint16)

            self.rawImage = rawImage
            self.rawImageExists = 1

            rawImagePLTWindow.imshow(rawImage)
            rawImagePLTWindow.axis("off")
            self.canvas.draw()

            self.grayImageWithSomeColorExists = 0
            grayImagePLTWindow = self.mainPLTWindowTopRight
            grayImagePLTWindow.clear()

            # convert to grayscale
            grayImage = np.dot(self.rawImage[..., :3], [0.299, 0.587, 0.114])

            # round to integers
            grayImage = np.round(grayImage).astype(np.uint16)  # 16 or 8?
            self.grayImage = grayImage
            self.grayImageExists = 1

            # show grayscale image
            grayImagePLTWindow.imshow(grayImage, cmap="gray")
            grayImagePLTWindow.axis("off")
            self.canvas.draw()

            self.dimensionalisedGrayImage = self.dimensionalise(
                self.rawImage, self.grayImage
            )

            xSize, ySize = self.grayImage.shape

            # get random indices to eventually color in
            randomIndices = np.random.default_rng().choice(
                xSize * ySize, size=int(self.NRandomPixelsMax), replace=False
            )

            # define the coordinate pairs which we will color;
            # returns an array formatted as [[y0,x0],[y1,x1]...]
            self.randomCoordinates = self.coordinatesFromIndices(
                randomIndices, len(self.rawImage[0])
            )

            # choose method to colorise image when loaded
            self.loadColorChoice()
        return

    def coordinatesFromIndices(self, indices, size):
        coordinates = [[index % size, index // size] for index in indices]
        return coordinates

    def loadColorChoice(self):
        match self.colorMode.get():
            case 0:
                self.addManualColor()
            case 1:
                self.addRandomisedColor()
            case 2:
                self.addBlockColor()

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
            self.coloredCoordinates = np.empty((0, 2))

            randomisedColorPLTWindow = self.mainPLTWindowBottomLeft
            randomisedColorPLTWindow.clear()
            self.grayImageWithColorTemplate = self.mainPLTWindowBottomLeft.imshow(
                self.dimensionalisedGrayImage
            )

            grayImageWithRandomColor = self.dimensionalise(
                self.rawImage, self.grayImage
            )

            # go over random coordinates,
            # replacing as many pairs as necessary with their colored equivalents
            for index in range(0, int(self.NRandomPixels)):
                grayImageWithRandomColor[
                    self.randomCoordinates[index][1],
                    self.randomCoordinates[index][0],
                    :,
                ] = self.rawImage[
                    self.randomCoordinates[index][1],
                    self.randomCoordinates[index][0],
                    :,
                ]

            # get coloredCoordinates and colorValues
            self.coloredCoordinates = np.flip(
                np.array(self.randomCoordinates[0 : int(self.NRandomPixels)]).astype(
                    int
                )
            )
            self.colorValues = grayImageWithRandomColor[
                self.coloredCoordinates[:, 0], self.coloredCoordinates[:, 1]
            ]

            self.grayImageWithSomeColorExists = 1

            self.grayImageWithColorTemplate.set_data(grayImageWithRandomColor)
            self.grayImageWithColorTemplate.autoscale()
            randomisedColorPLTWindow.axis("off")
            # randomisedColorPLTWindow.set_title("Image with Some Color")
            self.canvas.draw()

    def addBlockColor(self):
        if self.rawImageExists == 0:
            pass
        else:
            self.grayImageWithSomeColorExists = 0
            self.coloredCoordinates = np.empty((0, 2))

            blockColorPLTWindow = self.mainPLTWindowBottomLeft
            blockColorPLTWindow.clear()
            self.grayImageWithColorTemplate = blockColorPLTWindow.imshow(
                self.dimensionalisedGrayImage
            )

            grayImageWithBlockColor = self.dimensionalise(self.rawImage, self.grayImage)

            def onclick(event):
                if self.colorMode.get() == 2:
                    if event.inaxes == blockColorPLTWindow:
                        x, y = event.xdata, event.ydata
                        x, y = np.round(x).astype(int), np.round(y).astype(int)
                        colorBoxSize = 2

                        grayImageWithBlockColor[
                            y : y + colorBoxSize, x : x + colorBoxSize, :
                        ] = self.rawImage[y : y + colorBoxSize, x : x + colorBoxSize, :]

                        # generate colorCoordinates and colorValues

                        coloredCoordinateBounds = np.array(
                            [[y, x], [y + colorBoxSize - 1, x + colorBoxSize - 1]]
                        )

                        coloredYCoordinates = [
                            y
                            for y in range(
                                coloredCoordinateBounds[0][0],
                                coloredCoordinateBounds[1][0] + 1,
                            )
                        ]
                        coloredXCoordinates = [
                            x
                            for x in range(
                                coloredCoordinateBounds[0][1],
                                coloredCoordinateBounds[1][1] + 1,
                            )
                        ]
                        self.coloredCoordinates = np.append(
                            self.coloredCoordinates,
                            np.array(
                                list(
                                    set(
                                        itertools.product(
                                            coloredYCoordinates, coloredXCoordinates
                                        )
                                    )
                                )
                            ),
                            axis=0,
                        ).astype(int)

                        self.colorValues = grayImageWithBlockColor[
                            self.coloredCoordinates[:, 0], self.coloredCoordinates[:, 1]
                        ]

                        self.grayImageWithSomeColorExists = 1

                        self.grayImageWithColorTemplate.set_data(
                            grayImageWithBlockColor
                        )
                        self.grayImageWithColorTemplate.autoscale()
                    self.canvas.draw_idle()

            cid2 = self.canvas.mpl_connect("button_press_event", onclick)

            blockColorPLTWindow.axis("off")

            self.canvas.draw()

    def addManualColor(self):
        if self.rawImageExists == 0:
            pass
        else:
            self.grayImageWithSomeColorExists = 0
            self.coloredCoordinates = np.empty((0, 2))

            manualColorPLTWindow = self.mainPLTWindowBottomLeft
            manualColorPLTWindow.clear()
            self.grayImageWithColorTemplate = manualColorPLTWindow.imshow(
                self.dimensionalisedGrayImage
            )

            grayImageWithManualColor = self.dimensionalise(
                self.rawImage, self.grayImage
            )

            def onclick(event):
                if self.colorMode.get() == 0:
                    if event.inaxes == manualColorPLTWindow:
                        selectedColorInHex = self.selectedColors[
                            self.selectedColorButtonVar - 1
                        ]

                        selectedColorInRGB = list(
                            int(selectedColorInHex.lstrip("#")[i : i + 2], 16)
                            for i in (0, 2, 4)
                        )

                        x, y = event.xdata, event.ydata  # coordinates
                        x, y = np.round(x).astype(int), np.round(y).astype(int)
                        # print(x)
                        # print(y)

                        grayImageWithManualColor[
                            y : y + self.brushSize, x : x + self.brushSize, :
                        ] = selectedColorInRGB

                        # generate colorCoordinates and colorValues

                        coloredCoordinateBounds = np.array(
                            [[y, x], [y + self.brushSize - 1, x + self.brushSize - 1]]
                        )
                        coloredYCoordinates = [
                            y
                            for y in range(
                                coloredCoordinateBounds[0][0],
                                coloredCoordinateBounds[1][0] + 1,
                            )
                        ]
                        coloredXCoordinates = [
                            x
                            for x in range(
                                coloredCoordinateBounds[0][1],
                                coloredCoordinateBounds[1][1] + 1,
                            )
                        ]
                        self.coloredCoordinates = np.append(
                            self.coloredCoordinates,
                            np.array(
                                list(
                                    set(
                                        itertools.product(
                                            coloredYCoordinates, coloredXCoordinates
                                        )
                                    )
                                )
                            ),
                            axis=0,
                        ).astype(int)

                        self.colorValues = grayImageWithManualColor[
                            self.coloredCoordinates[:, 0], self.coloredCoordinates[:, 1]
                        ]

                        self.grayImageWithSomeColorExists = 1

                        self.grayImageWithColorTemplate.set_data(
                            grayImageWithManualColor
                        )
                        self.grayImageWithColorTemplate.autoscale()

                    self.canvas.draw_idle()

            cid2 = self.canvas.mpl_connect("button_press_event", onclick)

            manualColorPLTWindow.axis("off")
            self.canvas.draw()

    def saveImage(self):
        self.mainWindowFigure.savefig("./image.png")

    def generateColoredImage(self):
        if self.grayImageWithSomeColorExists == 0:
            print("no such image!")
        else:
            popupWaitingWindow = waitingWindowClass.waitingWindow()

            colorisedWindow = self.mainPLTWindowBottomRight
            colorisedWindow.clear()

            normalKernel = lambda x: np.exp(-(x**2))
            parameters = {
                "delta": self.deltaValue,
                "sigma1": self.sigma1Value,
                "sigma2": self.sigma2Value,
                "p": self.rhoValue,
                "kernel": normalKernel,
            }
            self.coloriserInstance = Coloriser.Coloriser(
                self.dimensionalisedGrayImage,
                self.coloredCoordinates,
                self.colorValues,
                parameters,
            )
            self.colorisedImage = self.coloriserInstance.kernelColoriseColumnal()
            colorisedWindow.imshow(self.colorisedImage)
            colorisedWindow.axis("off")
            self.canvas.draw()

            popupWaitingWindow.destroy()

    def clearColorisedImage(self):
        self.mainPLTWindowBottomRight.clear()
        self.mainPLTWindowBottomRight.axis("off")
        self.canvas.draw()
        print("Cleared image!")

    def colorDropper(self):
        if self.colorDropperVar == 0:
            print("Color Dropper Activated")
            self.colorDropperVar = 1
        else:
            print("Color Dropper Activated")
            self.colorDropperVar = 0

    def selectedColor1(self):
        # TODO this is clunky, could refactor as radio buttons.
        self.selectedColorButtonVar = 1
        self.selectedColorButton1.configure(border_width=2, border_color="#b2b2b2")
        self.selectedColorButton2.configure(border_width=1, border_color="gray16")
        self.selectedColorButton3.configure(border_width=1, border_color="gray16")

    def selectedColor2(self):
        self.selectedColorButtonVar = 2
        self.selectedColorButton1.configure(border_width=1, border_color="gray16")
        self.selectedColorButton2.configure(border_width=2, border_color="#b2b2b2")
        self.selectedColorButton3.configure(border_width=1, border_color="gray16")

    def selectedColor3(self):
        self.selectedColorButtonVar = 3
        self.selectedColorButton1.configure(border_width=1, border_color="gray16")
        self.selectedColorButton2.configure(border_width=1, border_color="gray16")
        self.selectedColorButton3.configure(border_width=2, border_color="#b2b2b2")

    def colorSelected(self, event):
        print("Color Selected")
        print(f"{self.selectedColorButtonVar = }")
        print(f"{self.selectedColors = }")
        x, y = int(event.xdata), int(event.ydata)
        self.currentColor = self.colorGrid[y, x]
        self.currentColor = "#{:02x}{:02x}{:02x}".format(
            self.currentColor[0], self.currentColor[1], self.currentColor[2]
        )
        self.selectedColors[self.selectedColorButtonVar - 1] = self.currentColor
        self.selectedColorButton1.configure(fg_color=self.selectedColors[0])
        self.selectedColorButton2.configure(fg_color=self.selectedColors[1])
        self.selectedColorButton3.configure(fg_color=self.selectedColors[2])

    def setBrushSize(self, event):
        size = int(event)
        if self.brushSizeMin < size < self.brushSizeMax:
            self.brushSize = size
        elif size > self.brushSize:
            self.brushSize = self.brushSizeMax
        else:
            self.brushSize = self.brushSizeMin
        self.brushSizeEntry.configure(placeholder_text=str(size))

    def setNRandomPixels(self, event):
        self.NRandomPixels = event
        self.NRandomPixelEntry.configure(placeholder_text=int(self.NRandomPixels))
        if self.colorMode.get() == 1:
            self.addRandomisedColor()

    def setColorChoiceBackground(self, color):
        if color == "dark":
            self.selectedColorButtonBorder1.configure(
                bg=self.colorByPixelFrame._bg_color[1]
            )
        else:
            self.selectedColorButtonBorder1.configure(
                bg=self.colorByPixelFrame._bg_color[0]
            )

    def changeAppearanceEvent(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode.lower() == "dark":
            self.mainWindowFigure.patch.set_facecolor(self.frameDark3)
            self.setColorChoiceBackground("dark")
            self.mainWindowFigure.canvas.draw_idle()

        if new_appearance_mode.lower() == "light":
            self.mainWindowFigure.patch.set_facecolor(self.frameLight3)
            self.setColorChoiceBackground("light")
            self.mainWindowFigure.canvas.draw_idle()

    def generateFrames(self):
        self.imageFrame = ctk.CTkFrame(root, width=150, corner_radius=0)
        self.imageFrame.grid(row=0, column=1, rowspan=4, columnspan=1, sticky="nsew")
        self.imageFrame.grid_rowconfigure(16, weight=1)

        self.mainWindowFigure = plt.figure(figsize=(20, 7))  # TODO: what size?
        self.mainWindowFigure.patch.set_facecolor(self.frameDark3)
        self.mainWindowFigure.subplots_adjust(
            # left=0.01, right=0.99, top=0.99, bottom=0.01, hspace=0, wspace=0
            left=0.05,
            right=0.95,
            top=0.95,
            bottom=0.05,
            hspace=0.1,
            wspace=0.1,
        )
        self.mainPLTWindowTopLeft = self.mainWindowFigure.add_subplot(221)
        self.mainPLTWindowTopRight = self.mainWindowFigure.add_subplot(222)
        self.mainPLTWindowBottomLeft = self.mainWindowFigure.add_subplot(223)
        self.mainPLTWindowBottomRight = self.mainWindowFigure.add_subplot(224)
        self.mainPLTWindowAxes = [
            self.mainPLTWindowTopLeft,
            self.mainPLTWindowTopRight,
            self.mainPLTWindowBottomLeft,
            self.mainPLTWindowBottomRight,
        ]

        for axis in self.mainPLTWindowAxes:
            axis.axis("off")

        # define the canvas upon which we place the images
        self.canvas = FigureCanvasTkAgg(self.mainWindowFigure, self.imageFrame)
        self.canvas.get_tk_widget().pack(side="top", padx=0, pady=0)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas, self.imageFrame)
        self.toolbar.set_message = lambda x: ""
        self.toolbar.config(background="gray16")
        self.toolbar.children["!button2"].pack_forget()
        self.toolbar.children["!button3"].pack_forget()
        self.toolbar.children["!button4"].pack_forget()
        self.toolbar._message_label.config(
            background="gray16"
        )  # TODO: make the checkboxes dark blue when selected
        for button in self.toolbar.winfo_children()[0:-2]:
            button.configure(
                background="#3A7EBF",
                highlightbackground="#325882",
                # highlightcolor="#325882",
                # fg="#325882",
                # activeforeground="#325882",
                # activebackground="#325882",
            )
        self.toolbar.winfo_children()[-2].configure(background="gray16")
        self.toolbar.update()
        self.toolbar.pack(side="bottom", padx=3, pady=3)
        self.canvas.draw()

        # create sidebar and widgets after defining frame
        self.sidebarFrame = ctk.CTkFrame(
            root, width=150, corner_radius=0
        )  # width doesn't do anything ?
        self.sidebarFrame.grid(row=0, column=0, rowspan=4, columnspan=1, sticky="nsew")
        self.sidebarFrame.grid_rowconfigure(17, weight=1)

    def generateFileSection(self):
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
            self.sidebarFrame, placeholder_text=self.fileName
        )
        self.loadImagePath.grid(row=1, column=1, columnspan=4, padx=10, pady=5)

        self.loadStateButton = ctk.CTkButton(
            self.sidebarFrame, command=self.generateColoredImage, text="Colorise Image"
        )
        self.loadStateButton.grid(row=2, column=0, padx=20, pady=5)
        self.loadStatePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.statePath
        )
        self.loadStatePath.grid(row=2, column=1, columnspan=4, padx=10, pady=5)

        self.saveStateButton = ctk.CTkButton(
            self.sidebarFrame,
            command=self.clearColorisedImage,
            text="Clear colorised image",
        )
        self.saveStateButton.grid(row=3, column=0, padx=20, pady=5)
        self.saveStatePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.statePath
        )
        self.saveStatePath.grid(row=3, column=1, columnspan=4, padx=10, pady=5)

        self.saveImageButton = ctk.CTkButton(
            self.sidebarFrame, command=self.hello, text="Placeholder"
        )
        self.saveImageButton.grid(row=4, column=0, padx=20, pady=5)
        self.saveImagePath = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.fileName
        )
        self.saveImagePath.grid(row=4, column=1, columnspan=4, padx=10, pady=5)

    def hello(self):
        print(self.rhoEntry.get())
        print(self.deltaValue)
        print(self.sigma1Entry)
        print(self.sigma1Entry)

    def generateEditSection(self):
        # edit section
        self.editLabel = ctk.CTkLabel(
            self.sidebarFrame, text="Edit", anchor="center", fg_color=self.labelColor
        )
        self.editLabel.grid(
            row=5, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )

        # colorbypixel tools #TODO
        # self.colorByPixel = ctk.CTkRadioButton(
        #     self.sidebarFrame,
        #     text="Color by Pixel",
        #     command=self.addManualColor,
        #     variable=self.colorMode,
        #     value=0,
        # )
        # self.colorByPixel.grid(row=6, column=0, pady=10, padx=20, sticky="nw")

        self.colorByPixelFrame = ctk.CTkFrame(
            self.sidebarFrame,
            width=150,
            height=100,
            corner_radius=0,
            fg_color=("#DBDBDA", "#2B2A2B"),
        )  # width doesn't do anything ?
        self.colorByPixelFrame.grid(
            row=7, column=0, rowspan=1, columnspan=5, sticky="ew"
        )
        self.colorByPixelFrame.grid_rowconfigure(4, weight=1)
        self.colorByPixelFrame.grid_columnconfigure(6, weight=1)
        self.colorByPixel = ctk.CTkRadioButton(
            self.colorByPixelFrame,
            text="Color by Pixel",
            command=self.addManualColor,
            variable=self.colorMode,
            value=0,
        )
        self.colorByPixel.grid(
            row=0, column=0, columnspan=3, pady=(10, 0), padx=20, sticky="nw"
        )

        brushSizePady = 0
        self.brushSizeLabel = ctk.CTkLabel(
            self.colorByPixelFrame,
            text="Size",
            anchor="nw",
        )
        self.brushSizeLabel.grid(
            row=1,
            column=1,
            columnspan=1,
            padx=(0, 0),
            pady=(brushSizePady + 7.5, 5),
            sticky="w",
        )
        self.brushSizeEntry = ctk.CTkEntry(
            self.colorByPixelFrame, width=50, placeholder_text=self.brushSizeMax // 2
        )  # work out how to update when changed
        self.brushSizeEntry.grid(
            row=1, column=0, padx=10, pady=(brushSizePady, 5), sticky="w"
        )

        self.brushSizeSlider = ctk.CTkSlider(
            self.colorByPixelFrame,
            from_=self.brushSizeMin,
            to=self.brushSizeMax,
            number_of_steps=20,
            command=self.setBrushSize,
            width=100,
        )
        self.brushSizeSlider.grid(
            row=1, column=1, columnspan=2, padx=(25, 0), pady=(brushSizePady, 5)
        )
        # selected color buttons and borders #TODO: get rid of frame
        self.selectedColorButtonBorder1 = tk.Frame(
            self.colorByPixelFrame,
            highlightthickness=0,
            bg=self.colorFrameColor,
            width=10,
            height=10,
        )
        self.selectedColorButtonBorder1.grid(
            row=2, column=0, padx=(20, 5), pady=(5, 20), columnspan=3
        )

        self.selectedColorButton1 = ctk.CTkButton(
            self.selectedColorButtonBorder1,
            command=self.selectedColor1,
            text="",
            border_width=1,
            border_color="gray16",
            corner_radius=15,
            width=30,
            anchor="CENTER",
            # border_color="green",
            fg_color=self.selectedColors[0],
        )
        self.selectedColorButton1.grid(row=7, column=0, padx=(0, 5), pady=(0, 0))
        #

        self.selectedColorButton2 = ctk.CTkButton(
            self.selectedColorButtonBorder1,
            command=self.selectedColor2,
            text="",
            border_width=2,
            border_color="#b2b2b2",
            corner_radius=15,
            width=30,
            anchor="CENTER",
            fg_color=self.selectedColors[1],
        )
        self.selectedColorButton2.grid(row=7, column=1, padx=(5, 5), pady=(0, 0))

        self.selectedColorButton3 = ctk.CTkButton(
            self.selectedColorButtonBorder1,
            command=self.selectedColor3,
            text="",
            border_width=1,
            border_color="gray16",
            corner_radius=15,
            width=30,
            anchor="CENTER",
            fg_color=self.selectedColors[2],
        )
        self.selectedColorButton3.grid(row=7, column=2, padx=(5, 5), pady=(0, 0))

        self.placeholderButton = ctk.CTkButton(
            self.selectedColorButtonBorder1,
            text="Undo",
            border_width=1,
            border_color="gray16",
            corner_radius=15,
            width=30,
            anchor="CENTER",
        )
        self.placeholderButton.grid(row=7, column=3, padx=(5, 5), pady=(0, 0))

        self.colorRangeSlider = ctk.CTkSlider(
            self.colorByPixelFrame, from_=0, to=1, command=self.setColorRange, width=150
        )
        self.colorRangeSlider.grid(
            row=4, column=4, padx=(0, 0), pady=(5, 5), columnspan=2, sticky="w"
        )
        self.colorRangeSlider.set(self.colorRangeSliderInitial)
        self.colorSelectorFigure = plt.figure(figsize=(0.7, 0.7))
        self.colorSelectorFigure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.colorSelectorFigure.subplots_adjust(wspace=0.0, hspace=0.0)

        self.colorSelectorWindow = self.colorSelectorFigure.add_subplot()
        self.colorSelectorWindow.axis("off")

        self.rainbow = mpl.colormaps["gist_rainbow"]

        self.colorSelectorCanvas = FigureCanvasTkAgg(
            self.colorSelectorFigure, self.colorByPixelFrame
        )
        self.colorSelectorCanvas.get_tk_widget().grid(
            row=0,
            column=3,
            rowspan=3,
            columnspan=3,
            padx=(5, 5),
            pady=(15, 0),
        )
        self.colorSelectorCanvas.callbacks.connect(
            "button_press_event", self.colorSelected
        )
        self.setColorRange(self.colorRangeSliderInitial)

        # TODO sort out color dropper button
        # # colorDropperImage = tk.PhotoImage('button_images/color_dropper.png')
        # self.colorDropperButton = tk.Button(self.sidebarFrame,width = 1,height=1,command=self.colorDropper)
        # # for making transparency work
        # colorDropperLoad = Image.open('button_images/color_dropper.png')
        # self.colorDropperImage = ImageTk.PhotoImage(colorDropperLoad)
        # # self.colorDropperButton.config(image=colorDropperLoad)
        # self.colorDropperButton.grid(row = 7,column = 4, columnspan =1,padx=0,pady=0)

        self.colorRandomPixels = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color Random Pixels",
            command=self.addRandomisedColor,
            variable=self.colorMode,
            value=1,
        )
        self.colorRandomPixels.grid(row=9, column=0, pady=10, padx=20, sticky="nw")
        self.NRandomPixelsSlider = ctk.CTkSlider(
            self.sidebarFrame,
            from_=0,
            to=self.NRandomPixelsMax,
            number_of_steps=20,
            command=self.setNRandomPixels,
        )
        self.NRandomPixelsSlider.grid(
            row=10, column=0, columnspan=5, padx=(100, 5), pady=(5, 5), sticky="ew"
        )
        self.NRandomPixelEntry = ctk.CTkEntry(
            self.sidebarFrame, width=50, placeholder_text=int(self.NRandomPixels)
        )
        self.NRandomPixelEntry.grid(row=10, column=0, padx=10, pady=(5, 5), sticky="w")
        self.NRandomPixelLabel = ctk.CTkLabel(self.sidebarFrame, text="N", anchor="n")
        self.NRandomPixelLabel.grid(
            row=10, column=0, padx=80, pady=(12.5, 5), sticky="w"
        )

        self.colorByBlockButton = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color by Grid",
            command=self.addBlockColor,
            variable=self.colorMode,
            value=2,
        )
        self.colorByBlockButton.grid(row=11, column=0, pady=10, padx=20, sticky="nw")

    def setDelta(self, *args):
        try:
            self.deltaValue = float(self.deltaEntry.get())
        except Exception as e:
            self.deltaValue = 1e-4

    def setRho(self, *args):
        try:
            self.rhoValue = float(self.rhoEntry.get())
        except Exception as e:
            self.rhoValue = 0.5

    def setSigma1(self, *args):
        try:
            self.sigma1Value = float(self.sigma1Entry.get())
        except Exception as e:
            self.sigma1Value = 100

    def setSigma2(self, *args):
        try:
            self.sigma2Value = float(self.sigma2Entry.get())
        except Exception as e:
            self.sigma2Value = 100

    def generateParameterSection(self):
        self.parameterLabel = ctk.CTkLabel(
            self.sidebarFrame,
            text="Parameters",
            anchor="center",
            fg_color=self.labelColor,
        )
        self.parameterLabel.grid(
            row=12, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )

        self.deltaLabel = ctk.CTkLabel(self.sidebarFrame, text="Delta:", anchor="n")
        self.deltaLabel.grid(row=13, column=0, padx=(20, 0), pady=(5, 5), sticky="w")
        self.deltaEntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.deltaEntry,
        )
        self.deltaEntryBox.grid(row=13, column=1, columnspan=4, padx=(5,35), pady=(5, 5))
        self.deltaEntry.trace("w", self.setDelta)

        self.rhoLabel = ctk.CTkLabel(self.sidebarFrame, text="Rho:", anchor="n")
        self.rhoLabel.grid(row=14, column=0, padx=(20, 0), pady=(5, 5), sticky="w")
        self.rhoEntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.rhoEntry,
        )
        self.rhoEntryBox.grid(row=14, column=1, padx=(5,35), pady=(5, 5), columnspan=4)
        self.rhoEntry.trace("w", self.setRho)

        self.sigma1Label = ctk.CTkLabel(self.sidebarFrame, text="Sigma 1:", anchor="n")
        self.sigma1Label.grid(
            row=15, column=0, padx=(20, 0), pady=(5, 5), sticky="w"
        )
        self.sigma1EntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.sigma1Entry,
        )
        self.sigma1EntryBox.grid(row=15, column=1, padx=(5,35), pady=(5, 5), columnspan=4)
        self.sigma1Entry.trace("w", self.setSigma1)

        self.sigma2Label = ctk.CTkLabel(self.sidebarFrame, text="Sigma 2:", anchor="n")
        self.sigma2Label.grid(
            row=16, column=0, padx=(20, 0), pady=(5, 5), sticky="w"
        )
        self.sigma2EntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.sigma2Entry,
        )
        self.sigma2EntryBox.grid(row=16, column=1, columnspan=4, padx=(5,35), pady=(5, 5))
        self.sigma2Entry.trace("w", self.setSigma2)

    def generateAppearanceSection(self):
        # appearance section
        self.appearanceLabel = ctk.CTkLabel(
            self.sidebarFrame,
            text="Appearance",
            anchor="center",
            fg_color=self.labelColor,
        )
        self.appearanceLabel.grid(
            row=17, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )
        self.appearanceOptionMenu = ctk.CTkOptionMenu(
            self.sidebarFrame,
            values=["Light", "Dark", "System"],
            command=self.changeAppearanceEvent,
        )
        self.appearanceOptionMenu.grid(
            row=18, column=0, columnspan=1, padx=20, pady=(10, 10)
        )
        self.appearanceOptionMenu.set("Dark")

        self.exitButton = ctk.CTkButton(
            self.sidebarFrame, text="Exit", command=root.destroy
        )
        #
        self.exitButton.grid(row=18, column=1)
        self.setDefaults()


def popup_bonus():
    win = ctk.CTkToplevel()
    win.wm_title("Window")

    l = tk.Label(win, text="Input")
    l.grid(row=0, column=0)

    b = ctk.CTkButton(win, text="Okay", command=win.destroy)
    b.grid(row=1, column=0)
    win.wait_visibility()
    win.grab_set()


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("MMSC Image Colouriser")
    root.geometry(f"{1300}x{768}")
    app = imageColoriser(master=root)
    app.mainloop()
##
# cc = app.coloredCoordinates
# cv = app.colorValues
image = app.rawImage
