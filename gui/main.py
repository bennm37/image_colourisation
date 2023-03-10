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


class imageColoriser(ctk.CTkFrame):
    def __init__(self, master=None):
        # create the frame which will contain our GUI
        ctk.CTkFrame.__init__(self, master)

        # the createUI() method generates the application winodw
        self.createUI()

    def createUI(self):
        # configure window parameters
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
        self.NRandomPixels = 500
        self.NRandomPixelsMax = 1000
        self.colorRangeSliderInitial = 0.67

        # these entry variables are what we use
        # to hold info on what our values for delta, rho, etc. are
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

        # now generate the sub-frames which have all the buttons
        # etc. that we need

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
        """
        Depending on where the color slider is, generate
        appropriate colors and update the window where we
        choose colors.
        """
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
        """
        When called, refreshes all plt windows and prompts the user to select an image.
        Upon selection displays the image as well as grayscaled versions, with one of these
        ready to be coloured in.
        """
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
            initialdir=str(pathlib.Path(mainDirectory, "flattenedImages")),
            title="Select A File",
            filetypes=(
                ("all files", "*.*"),
                ("jpg files", "*.jpg"),
                ("png files", "*.png"),
                ("jpeg files", "*.jpeg"),
            ),
        )

        # save file name to be referenced
        self.fileName = fileName
        self.colorisedFileName = (
            f"{fileName.split('.')[0]}_colorised.{fileName.split('.')[1]}"
        )

        self.loadImageEntry.configure(placeholder_text=self.fileName)
        self.saveImageEntry.configure(placeholder_text=self.colorisedFileName)

        if fileName:
            rawImage = mpimg.imread(fileName)
            self.t = rawImage
            if rawImage.dtype == "float32":
                if fileName.endswith(".jpg") or fileName.endswith(".jpeg"):
                    rawImage = (rawImage * 255).astype(np.uint8)
                else:
                    pass
            # special case with pngs
            if fileName.endswith(".png"):
                # remove transparency, convert to white
                if rawImage.shape[2] == 4:
                    for i in np.argwhere(rawImage[:, :, 3] != 1):
                        rawImage[i[0], i[1], :] = 1.0
                rawImage = rawImage[:, :, :3] * 255
                rawImage = rawImage.astype(np.uint64)
                print(np.max(rawImage))
            self.q = rawImage
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
            self.dimensionalisedGrayImage = self.dimensionalise(self.grayImage)
            grayImagePLTWindow.imshow(self.dimensionalisedGrayImage)
            grayImagePLTWindow.axis("off")
            self.canvas.draw()

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
        """
        Given a list of indices, generates the corresponding coordinates
        """
        coordinates = [[index % size, index // size] for index in indices]
        return coordinates

    def loadColorChoice(self):
        """
        when called, looks at which radio button has been selected for
        how the user wants to add color into the image. upon matching
        this case, calls the appropriate method.
        """
        match self.colorMode.get():
            case 0:
                self.addManualColor()
            case 1:
                self.addRandomisedColor()
            case 2:
                self.addBlockOfOriginalColor()

    def dimensionalise(self, grayImage):
        """
        Ensures that grayscale images have 3 dimensions to be filled with RGB values
        """
        grayImage3D = np.stack((grayImage,) * 3, axis=-1).astype(np.int64)
        return grayImage3D

    def addRandomisedColor(self):
        """
        When called, adds N randomly selected correctly colored pixels to the grayscale image.
        These N pixels are pre-determined from the given image and defined maximum number of colored
        pixels, and the number currently colored may be updated on the fly.
        This method also generates the appropriate colored pixel coordinates and RGB values
        to be used in colorising via the Coloriser class.
        """
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

            grayImageWithRandomColor = self.dimensionalise(self.grayImage)

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
            self.canvas.draw()

    def addBlockOfOriginalColor(self):
        """
        This method colors the grayscale image with a square block of the
        original picture's color, whilst also generating the color coordinates and
        color values which are used in Coloriser to re-color the image.
        """
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

            grayImageWithBlockColor = self.dimensionalise(self.grayImage)

            # this function colors the image where clicked, whilst
            # also updating the GUI as well as noting the coordinates of where
            # has been clicked, alongside the RGB values of the colored pixels.
            def onclick(event):
                if self.colorMode.get() == 2:
                    if event.inaxes == blockColorPLTWindow:
                        x, y = event.xdata, event.ydata
                        x, y = np.round(x).astype(int), np.round(y).astype(int)
                        colorBoxSize = 2

                        # this step overwrites the grayscale RGB values with their
                        # raw-image values.
                        grayImageWithBlockColor[
                            y : y + colorBoxSize, x : x + colorBoxSize, :
                        ] = self.rawImage[y : y + colorBoxSize, x : x + colorBoxSize, :]

                        # generate colorCoordinates
                        self.getColoredCoordinatesFromClickBounds(y, x, colorBoxSize)

                        self.colorValues = grayImageWithBlockColor[
                            self.coloredCoordinates[:, 0], self.coloredCoordinates[:, 1]
                        ]

                        self.grayImageWithSomeColorExists = 1

                        self.grayImageWithColorTemplate.set_data(
                            grayImageWithBlockColor
                        )
                        self.grayImageWithColorTemplate.autoscale()
                    self.canvas.draw_idle()

            self.canvas.mpl_connect("button_press_event", onclick)

            blockColorPLTWindow.axis("off")

            self.canvas.draw()

    def addManualColor(self):
        """
        This method adds a block of color to the grayscale image where it has been clicked.
        The color that is added can be chosen manually. Furthermore this method generates the
        color coordinates and color values of where has been selected.
        """
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

            grayImageWithManualColor = self.dimensionalise(self.grayImage)

            # this function colors the image where clicked, whilst
            # also updating the GUI as well as noting the coordinates of where
            # has been clicked, alongside the RGB values of the colored pixels.
            def onclick(event):
                if self.colorMode.get() == 0:
                    if event.inaxes == manualColorPLTWindow:
                        # the selected colors are stored in hex format in this
                        # program; we first grab that color
                        selectedColorInHex = self.selectedColors[
                            self.selectedColorButtonVar - 1
                        ]

                        # next we convert this hex color to an RGB value which we can
                        # input into an array
                        selectedColorInRGB = list(
                            int(selectedColorInHex.lstrip("#")[i : i + 2], 16)
                            for i in (0, 2, 4)
                        )

                        x, y = event.xdata, event.ydata  # coordinates
                        x, y = np.round(x).astype(int), np.round(y).astype(int)

                        # overwrite the gray image where clicked with the new chosen
                        # color
                        grayImageWithManualColor[
                            y : y + self.brushSize, x : x + self.brushSize, :
                        ] = selectedColorInRGB

                        # generate colorCoordinates and colorValues

                        self.getColoredCoordinatesFromClickBounds(y, x, self.brushSize)

                        self.colorValues = grayImageWithManualColor[
                            self.coloredCoordinates[:, 0], self.coloredCoordinates[:, 1]
                        ]

                        self.grayImageWithSomeColorExists = 1

                        self.grayImageWithColorTemplate.set_data(
                            grayImageWithManualColor
                        )
                        self.grayImageWithColorTemplate.autoscale()

                    self.canvas.draw_idle()

            self.canvas.mpl_connect("button_press_event", onclick)

            manualColorPLTWindow.axis("off")
            self.canvas.draw()

    def getColoredCoordinatesFromClickBounds(self, y, x, clickSize):
        """
        This method generates a list of colored coordinates to be used
        for methods in which the gray picture is clicked with a given square
        pixel size. To generate the coordinates we first define the bounds they
        lie between, then create arrays of all the possible X and Y coordinates
        between those bounds. Then, take these lists of X, and Y coordinates and
        get the corresponding tuples.
        """
        coloredCoordinateBounds = np.array(
            [[y, x], [y + clickSize - 1, x + clickSize - 1]]
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
                list(set(itertools.product(coloredYCoordinates, coloredXCoordinates)))
            ),
            axis=0,
        ).astype(int)

    def saveImage(self):
        # self.mainWindowFigure.savefig("./image.png")
        try:
            plt.imsave(
                f"{self.colorisedFileName}", self.colorisedImage.astype(np.uint8)
            )
            print("Image Saved Successfully!")
        except AttributeError:
            print("Please colorise the image first.")

    def generateColoredImage(self):
        """
        This method takes our image with some color in it, and
        calls Coloriser to colorise it, using parameters defined by
        the user via the GUI.
        """
        if self.grayImageWithSomeColorExists == 0:
            print("no such image!")
        else:
            # generate a waiting popup
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

            # creating an instance of the Coloriser class
            self.coloriserInstance = Coloriser.Coloriser(
                self.dimensionalisedGrayImage,
                self.coloredCoordinates,
                self.colorValues,
                parameters,
            )

            # calling a method within this instance to colorise our image
            self.width, self.height = self.rawImage.shape[0:2]
            self.n = self.colorValues.shape[0]
            self.sizeThreshHold = 5e8
            if self.width * self.height * self.n < self.sizeThreshHold:
                print("Using Fast Coloriser")
                self.colorisedImage = self.coloriserInstance.kernelColoriseColumnal()
            else:
                print("Using Large Coloriser")
                self.colorisedImage = (
                    self.coloriserInstance.kernelColoriseColumnalLarge()
                )
            colorisedWindow.imshow(self.colorisedImage)
            colorisedWindow.axis("off")
            self.canvas.draw()

            popupWaitingWindow.destroy()

    def clearColorisedImage(self):
        """
        Simply clear the colorised image from the bottom right window
        """
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
        self.loadImageEntry = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.fileName
        )
        self.loadImageEntry.grid(row=1, column=1, columnspan=4, padx=(20, 5), pady=5)

        self.saveImageButton = ctk.CTkButton(
            self.sidebarFrame, command=self.saveImage, text="Save Image"
        )
        self.saveImageButton.grid(row=2, column=0, padx=20, pady=5)
        self.saveImageEntry = ctk.CTkEntry(
            self.sidebarFrame, placeholder_text=self.fileName
        )
        self.saveImageEntry.grid(row=2, column=1, columnspan=4, padx=(20, 5), pady=5)

        self.colorisedImageButton = ctk.CTkButton(
            self.sidebarFrame, command=self.generateColoredImage, text="Colorise Image"
        )
        self.colorisedImageButton.grid(row=3, column=0, padx=20, pady=(5, 10))
        self.clearColorisedImageButton = ctk.CTkButton(
            self.sidebarFrame,
            command=self.clearColorisedImage,
            text="Clear colorised image",
        )
        self.clearColorisedImageButton.grid(row=3, column=1, padx=(20, 5), pady=(5, 10))

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
            row=4, column=4, padx=(0, 5), pady=(5, 5), columnspan=2, sticky="w"
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
            padx=(5, 10),
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
            number_of_steps=50,
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

        self.addBlockOfOriginalColorButton = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color by Grid",
            command=self.addBlockOfOriginalColor,
            variable=self.colorMode,
            value=2,
        )
        self.addBlockOfOriginalColorButton.grid(
            row=11, column=0, pady=10, padx=20, sticky="nw"
        )

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
        self.deltaEntryBox.grid(
            row=13, column=1, columnspan=4, padx=(20, 5), pady=(5, 5)
        )
        self.deltaEntry.trace("w", self.setDelta)

        self.rhoLabel = ctk.CTkLabel(self.sidebarFrame, text="Rho:", anchor="n")
        self.rhoLabel.grid(row=14, column=0, padx=(20, 0), pady=(5, 5), sticky="w")
        self.rhoEntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.rhoEntry,
        )
        self.rhoEntryBox.grid(row=14, column=1, padx=(20, 5), pady=(5, 5), columnspan=4)
        self.rhoEntry.trace("w", self.setRho)

        self.sigma1Label = ctk.CTkLabel(self.sidebarFrame, text="Sigma 1:", anchor="n")
        self.sigma1Label.grid(row=15, column=0, padx=(20, 0), pady=(5, 5), sticky="w")
        self.sigma1EntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.sigma1Entry,
        )
        self.sigma1EntryBox.grid(
            row=15, column=1, padx=(20, 5), pady=(5, 5), columnspan=4
        )
        self.sigma1Entry.trace("w", self.setSigma1)

        self.sigma2Label = ctk.CTkLabel(self.sidebarFrame, text="Sigma 2:", anchor="n")
        self.sigma2Label.grid(row=16, column=0, padx=(20, 0), pady=(5, 5), sticky="w")
        self.sigma2EntryBox = ctk.CTkEntry(
            self.sidebarFrame,
            textvariable=self.sigma2Entry,
        )
        self.sigma2EntryBox.grid(
            row=16, column=1, columnspan=4, padx=(20, 5), pady=(5, 5)
        )
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
        self.exitButton.grid(row=18, column=1, padx=(20, 5))
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
    root.title("MMSC Image Coloriser")
    root.geometry(f"{1300}x{750}")
    app = imageColoriser(master=root)
    app.mainloop()
