import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import colormaps as cm
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
import matplotlib.image as mpimg

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

        self.imagePath = "../images/apple.jpeg"
        self.statePath = "../states/apple.pkl"
        self.colorMode = tk.IntVar(value=0)
        self.labelColor = ("#B2B2B2", "#525252")
        self.brushSizeMin = 0
        self.brushSizeMax = 20
        self.selectedColors = ["#FF0000", "#00FF00", "#0000FF"]
        self.selectedColorButtonVar = 2
        self.NRandomPixels = 10
        self.NRandomPixelsMax = 100

        # styling 
        fpath = Path(mpl.get_data_path(), "/Users/benn-m/Documents/image_colourisation/gui/fonts/Roboto-Medium.ttf")
        self.captionFont = fpath
        self.captionFontDict = {'family': fpath,
        'color':  'white',
        'weight': 'normal',
        'size': 5,
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
        self.imagePath = "../images/apple.jpeg"
        self.statePath = "../states/apple.pkl"
        # self.colorMode = tk.IntVar(value=0)
        self.brushSizeMax = 30
        self.brushSizeMin = 1
        self.brushSize = 10
        self.NRandomPixelsSlider.set(self.NRandomPixels)

    def setColorRange(self, sliderVal, size=40):
        # np.array([[color[0:3]]],dtype=np.uint16)
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
            initialdir=str(Path("..", "images")),
            title="Select A File",
            filetypes=(
                ("jpg files", "*.jpg"),
                ("png files", "*.png"),
                ("jpeg files", "*.jpeg"),
                ("all files", "*.*"),
            ),
        )  # TODO: initialdir?

        # save file name to be referenced
        self.fileName = fileName

        if fileName:
            rawImage = mpimg.imread(fileName)
            # special case with pngs
            if fileName.endswith(".png"):
                rawImage = rawImage.astype(np.uint16)
                rawImage = rawImage[:, :, :3] * 255

            self.rawImage = rawImage
            self.rawImageExists = 1

            rawImagePLTWindow.imshow(rawImage)
            # self.mainPLTWindowBottomRight.imshow(rawImage)
            # self.mainPLTWindowTopRight.imshow(rawImage)
            rawImagePLTWindow.axis("off")
            rawImagePLTWindow.set_title("Colored Image",font=self.captionFont,fontdict=self.captionFontDict)
            # rawImagePLTWindow.set
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
            grayImagePLTWindow.set_title("Gray Image",font=self.captionFont,fontdict=self.captionFontDict)
            self.canvas.draw()

            self.dimensionalisedGrayImage = self.dimensionalise(
                self.rawImage, self.grayImage
            )

            xSize, ySize = self.grayImage.shape

            self.listOfRandomXCoords = np.random.default_rng().choice(
                xSize, size=int(self.NRandomPixelsMax), replace=False
            )
            self.listOfRandomYCoords = np.random.default_rng().choice(
                ySize, size=int(self.NRandomPixelsMax), replace=False
            )

            self.loadColorChoice()
        return

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

            randomisedColorPLTWindow = self.mainPLTWindowBottomLeft
            randomisedColorPLTWindow.clear()
            self.grayImageWithColorTemplate = self.mainPLTWindowBottomLeft.imshow(
                self.dimensionalisedGrayImage
            )

            grayImageWithRandomColor = self.dimensionalise(
                self.rawImage, self.grayImage
            )

            # grid colorization
            for x in self.listOfRandomXCoords[0 : int(self.NRandomPixels)]:
                for y in self.listOfRandomYCoords[
                    0 : int(self.NRandomPixels)
                ]:  # np.linspace(0, ySize, J, dtype=int, endpoint=False):
                    grayImageWithRandomColor[int(x), int(y), :] = self.rawImage[
                        int(x), int(y), :
                    ]

            self.grayImageWithSomeColorExists = 1

            self.grayImageWithColorTemplate.set_data(grayImageWithRandomColor)
            self.grayImageWithColorTemplate.autoscale()
            randomisedColorPLTWindow.axis("off")
            randomisedColorPLTWindow.set_xlabel("Image with Some Color",font=self.captionFont,fontdict=self.captionFontDict)
            self.canvas.draw()

    def addBlockColor(self):
        if self.rawImageExists == 0:
            pass
        else:
            self.grayImageWithSomeColorExists = 0

            blockColorPLTWindow = self.mainPLTWindowBottomLeft
            blockColorPLTWindow.clear()
            self.grayImageWithColorTemplate = blockColorPLTWindow.imshow(
                self.dimensionalisedGrayImage
            )

            grayImageWithBlockColor = self.dimensionalise(self.rawImage, self.grayImage)
            # xSize, ySize, null = self.rawImage.shape
            # yStart = np.random.randint(0, ySize - 50)
            # xStart = np.random.randint(0, xSize - 50)

            def addColorBox(xStart, xEnd, yStart, yEnd):
                for i in range(xStart, xEnd):
                    for j in range(yStart, yEnd):
                        grayImageWithBlockColor[i, j, :] = self.rawImage[i, j, 0:3]

            def onclick(event):
                if self.colorMode.get() == 2:
                    if event.inaxes == blockColorPLTWindow:
                        x, y = event.xdata, event.ydata
                        x, y = np.round(x).astype(int), np.round(y).astype(int)

                        addColorBox(y, y + 20, x, x + 20)

                        self.grayImageWithColorTemplate.set_data(
                            grayImageWithBlockColor
                        )
                        self.grayImageWithColorTemplate.autoscale()
                    self.canvas.draw_idle()

            cid2 = self.canvas.mpl_connect("button_press_event", onclick)

            self.grayImageWithSomeColorExists = 1

            blockColorPLTWindow.axis("off")
            blockColorPLTWindow.set_title("Image with Block Color",font=self.captionFont,fontdict=self.captionFontDict)
            self.canvas.draw()

    def addManualColor(self):
        if self.rawImageExists == 0:
            pass
        else:
            self.grayImageWithSomeColorExists = 0

            manualColorPLTWindow = self.mainPLTWindowBottomLeft
            manualColorPLTWindow.clear()
            self.grayImageWithColorTemplate = manualColorPLTWindow.imshow(
                self.dimensionalisedGrayImage
            )

            grayImageWithManualColor = self.dimensionalise(
                self.rawImage, self.grayImage
            )
            # xSize, ySize, null = rawImage.shape
            # yStart = np.random.randint(0, ySize - 50)
            # xStart = np.random.randint(0, xSize - 50)

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

                        x, y = event.xdata, event.ydata
                        x, y = np.round(x).astype(int), np.round(y).astype(int)

                        grayImageWithManualColor[
                            y : y + self.brushSize, x : x + self.brushSize, :
                        ] = selectedColorInRGB

                        self.grayImageWithColorTemplate.set_data(
                            grayImageWithManualColor
                        )
                        self.grayImageWithColorTemplate.autoscale()

                    self.canvas.draw_idle()

            cid2 = self.canvas.mpl_connect("button_press_event", onclick)

            self.grayImageWithSomeColorExists = 1

            manualColorPLTWindow.axis("off")
            manualColorPLTWindow.set_title("Image with Manual Color",font=self.captionFont,fontdict=self.captionFontDict)
            self.canvas.draw()

    def saveImage(self):
        self.mainWindowFigure.savefig("./image.png")

    def loadState(self):
        print("Load State")

    def saveState(self):
        print("Save State")

    def colorDropper(self):
        if self.colorDropperVar == 0:
            print("Color Dropper Activated")
            self.colorDropperVar = 1
        else:
            print("Color Dropper Activated")
            self.colorDropperVar = 0

    def selectedColor1(self):
        # TODO this is clunky, could refactor as radio buttons.
        # print('Selected Color 1')
        self.selectedColorButtonVar = 1
        self.selectedColorButtonBorder1.configure(highlightbackground="red")
        self.selectedColorButtonBorder2.configure(highlightbackground="black")
        self.selectedColorButtonBorder3.configure(highlightbackground="black")

    def selectedColor2(self):
        # print('Selected Color 2')
        self.selectedColorButtonVar = 2
        self.selectedColorButtonBorder1.configure(highlightbackground="black")
        self.selectedColorButtonBorder2.configure(highlightbackground="red")
        self.selectedColorButtonBorder3.configure(highlightbackground="black")

    def selectedColor3(self):
        # print('Selected Color 3')
        self.selectedColorButtonVar = 3
        self.selectedColorButtonBorder1.configure(highlightbackground="black")
        self.selectedColorButtonBorder2.configure(highlightbackground="black")
        self.selectedColorButtonBorder3.configure(highlightbackground="red")

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

    def changeAppearanceEvent(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode.lower() == "dark":
            self.mainWindowFigure.patch.set_facecolor(self.frameDark3)
            self.mainWindowFigure.canvas.draw_idle()

        if new_appearance_mode.lower()== "light":
            self.mainWindowFigure.patch.set_facecolor(self.frameLight3)
            self.mainWindowFigure.canvas.draw_idle()

    def generateFrames(self):
        self.imageFrame = ctk.CTkFrame(root, width=150, corner_radius=0)
        self.imageFrame.grid(row=0, column=1, rowspan=4, columnspan=1, sticky="nsew")
        self.imageFrame.grid_rowconfigure(16, weight=1)

        self.mainWindowFigure = plt.figure(figsize=(7, 8))  # TODO: what size?
        self.mainWindowFigure.patch.set_facecolor(self.frameDark3)
        self.mainWindowFigure.subplots_adjust(
            left=0.05, right=0.95, top=0.95, bottom=0.05, hspace=0.1, wspace=0.1
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
        self.canvas.draw()

        # create sidebar and widgets after defining frame
        self.sidebarFrame = ctk.CTkFrame(
            root, width=150, corner_radius=0
        )  # width doesn't do anything ?
        self.sidebarFrame.grid(row=0, column=0, rowspan=4, columnspan=1, sticky="nsew")
        self.sidebarFrame.grid_rowconfigure(15, weight=1)

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

    def generateEditSection(self):
        # edit section
        self.editLabel = ctk.CTkLabel(
            self.sidebarFrame, text="Edit", anchor="center", fg_color=self.labelColor
        )
        self.editLabel.grid(
            row=5, column=0, columnspan=5, padx=(0, 0), pady=(0, 0), sticky="ew"
        )

        # colorbypixel tools #TODO
        self.colorByPixel = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color by Pixel",
            command=self.addManualColor,
            variable=self.colorMode,
            value=0,
        )
        self.colorByPixel.grid(row=6, column=0, pady=10, padx=20, sticky="nw")
        self.colorByPixelFrame = ctk.CTkFrame(
            self.sidebarFrame, width=150, height=100, corner_radius=0,fg_color=("#DBDBDA","#2B2A2B")
        )  # width doesn't do anything ?
        self.colorByPixelFrame.grid(
            row=7, column=0, rowspan=1, columnspan=5, sticky="ew"
        )
        self.colorByPixelFrame.grid_rowconfigure(3, weight=1)
        self.colorByPixelFrame.grid_columnconfigure(6, weight=1)

        self.brushSizeLabel = ctk.CTkLabel(
            self.colorByPixelFrame, text="Brush size", anchor="w"
        )
        self.brushSizeLabel.grid(
            row=0, column=0, columnspan=3, padx=(20, 0), sticky="w"
        )
        self.brushSizeEntry = ctk.CTkEntry(
            self.colorByPixelFrame, width=50, placeholder_text=self.brushSizeMax // 2
        )  # work out how to update when changed
        self.brushSizeEntry.grid(row=0, column=2, padx=0, pady=(5, 5), sticky="w")
        self.brushSizeSlider = ctk.CTkSlider(
            self.colorByPixelFrame,
            from_=self.brushSizeMin,
            to=self.brushSizeMax,
            number_of_steps=20,
            command=self.setBrushSize,
        )
        self.brushSizeSlider.grid(
            row=1, column=0, columnspan=3, padx=(0, 0), pady=(5, 20), sticky="ew"
        )
        # selected color buttons and borders
        self.selectedColorButtonBorder1 = tk.Frame(
            self.colorByPixelFrame,
            highlightbackground="black",
            highlightthickness=2,
            width=10,
            height=10,
        )
        self.selectedColorButtonBorder1.grid(
            row=2, column=0, padx=(20, 5), pady=(5, 20)
        )

        self.selectedColorButton1 = ctk.CTkButton(
            self.selectedColorButtonBorder1,
            command=self.selectedColor1,
            text="",
            corner_radius=0,
            width=30,
            anchor="CENTER",
            fg_color=self.selectedColors[0],
        )
        self.selectedColorButton1.grid(row=2, column=0, padx=(0, 0), pady=(0, 0))

        self.selectedColorButtonBorder2 = tk.Frame(
            self.colorByPixelFrame,
            highlightbackground="red",
            highlightthickness=2,
            width=10,
            height=10,
        )
        self.selectedColorButtonBorder2.grid(
            row=2, column=1, padx=(20, 5), pady=(5, 20)
        )
        self.selectedColorButton2 = ctk.CTkButton(
            self.selectedColorButtonBorder2,
            command=self.selectedColor2,
            text="",
            corner_radius=0,
            width=30,
            anchor="CENTER",
            fg_color=self.selectedColors[1],
        )
        self.selectedColorButton2.grid(row=0, column=0, padx=(0, 0), pady=(0, 0))

        self.selectedColorButtonBorder3 = tk.Frame(
            self.colorByPixelFrame,
            highlightbackground="black",
            highlightthickness=2,
            width=10,
            height=10,
        )
        self.selectedColorButtonBorder3.grid(
            row=2, column=2, padx=(20, 5), pady=(5, 20)
        )
        self.selectedColorButton3 = ctk.CTkButton(
            self.selectedColorButtonBorder3,
            command=self.selectedColor3,
            text="",
            corner_radius=0,
            width=30,
            anchor="CENTER",
            fg_color=self.selectedColors[2],
        )
        self.selectedColorButton3.grid(row=0, column=0, padx=(0, 0), pady=(0, 0))

        self.colorRangeSlider = ctk.CTkSlider(
            self.colorByPixelFrame, from_=0, to=1, command=self.setColorRange
        )
        self.colorRangeSlider.grid(row=2, column=3, columnspan=3)

        self.colorSelectorFigure = plt.figure(figsize=(0.5, 0.5))
        self.colorSelectorFigure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.colorSelectorFigure.subplots_adjust(wspace=0.0, hspace=0.0)

        self.colorSelectorWindow = self.colorSelectorFigure.add_subplot()
        self.colorSelectorWindow.axis("off")
        # for item in [self.colorSelectorFigure, self.colorSelectorAx]:
        #     item.patch.set_visible(False)
        # self.colorSelectorAx.spines['top'].set_visible(False)
        # self.colorSelectorAx.spines['right'].set_visible(False)
        # self.colorSelectorAx.spines['bottom'].set_visible(False)
        # self.colorSelectorAx.spines['left'].set_visible(False)

        self.rainbow = cm["gist_rainbow"]

        self.colorSelectorCanvas = FigureCanvasTkAgg(
            self.colorSelectorFigure, self.colorByPixelFrame
        )
        self.colorSelectorCanvas.get_tk_widget().grid(
            row=0, column=4, rowspan=2, columnspan=2, pady=(5, 0), sticky="nsw"
        )
        self.colorSelectorCanvas.callbacks.connect(
            "button_press_event", self.colorSelected
        )
        self.setColorRange(0.5)

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
        self.NRandomPixelEntry.grid(row=10, column=0, padx=40, pady=(5, 5), sticky="w")
        self.NRandomPixelLabel = ctk.CTkLabel(self.sidebarFrame, text="N")
        self.NRandomPixelLabel.grid(row=10, column=0, padx=20, pady=(5, 5), sticky="w")

        self.colorByBlockButton = ctk.CTkRadioButton(
            self.sidebarFrame,
            text="Color by Grid",
            command=self.addBlockColor,
            variable=self.colorMode,
            value=2,
        )
        self.colorByBlockButton.grid(row=11, column=0, pady=10, padx=20, sticky="nw")

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

    def generateAppearanceSection(self):
        # appearance section
        self.appearanceLabel = ctk.CTkLabel(
            self.sidebarFrame,
            text="Appearance",
            anchor="center",
            fg_color=self.labelColor,
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
            self.sidebarFrame, text="Exit", command=root.destroy
        )
        #
        self.exitButton.grid(row=16, column=1)
        self.setDefaults()


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("MMSC Image Colouriser")
    root.geometry(f"{1300}x{720}")
    app = imageColoriser(master=root)
    app.mainloop()