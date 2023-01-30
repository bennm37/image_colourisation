import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk

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
        self.grid_columnconfigure((1,2,3), weight=1)
        self.grid_columnconfigure((4,5,6,7,8), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # initial default values
        self.imagePath = "../images/apple.jpeg"
        self.statePath = "../states/apple.pkl"
        self.colorMode = tk.IntVar(value=0)
        self.labelColor = "#525252"

        # create sidebar and widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=150, corner_radius=0) # width doesn't do anything ?
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, columnspan =1,sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(15, weight=1)
        # file section
        self.title_padx = 30 # padding for titles
        self.file_label = ctk.CTkLabel(self.sidebar_frame, text="File", anchor="center",fg_color=self.labelColor)
        self.file_label.grid(row=0, column=0, columnspan = 5, padx=(0,0), pady=(0, 0),sticky="ew")
        self.loadImage = ctk.CTkButton(self.sidebar_frame, command=self.loadImage, text = "Load Image")
        self.loadImage.grid(row=1, column=0, padx=5, pady=5)
        self.loadImagePath = ctk.CTkEntry(self.sidebar_frame, placeholder_text = self.imagePath)
        self.loadImagePath.grid(row=1, column=1, columnspan = 4, padx=10, pady=5)
        self.saveImage = ctk.CTkButton(self.sidebar_frame, command=self.loadImage, text = "Save Image")
        self.saveImage.grid(row=2, column=0, padx=20, pady=5)
        self.saveImagePath = ctk.CTkEntry(self.sidebar_frame, placeholder_text = self.imagePath)
        self.saveImagePath.grid(row=2, column=1, columnspan = 4, padx=10, pady=5)
        self.loadState = ctk.CTkButton(self.sidebar_frame, command=self.loadImage, text = "Load State")
        self.loadState.grid(row=3, column=0, padx=20, pady=5)
        self.loadStatePath = ctk.CTkEntry(self.sidebar_frame, placeholder_text = self.statePath)
        self.loadStatePath.grid(row=3, column=1, columnspan = 4, padx=10, pady=5)
        self.saveState = ctk.CTkButton(self.sidebar_frame, command=self.loadImage, text = "Save State")
        self.saveState.grid(row=4, column=0, padx=20, pady=5)
        self.saveStatePath = ctk.CTkEntry(self.sidebar_frame, placeholder_text = self.statePath)
        self.saveStatePath.grid(row=4, column=1, columnspan = 4, padx=10, pady=5)
        
        # edit section
        self.edit_label = ctk.CTkLabel(self.sidebar_frame, text="Edit",anchor="center",fg_color=self.labelColor)
        self.edit_label.grid(row=5, column=0, columnspan = 5, padx=(0,0), pady=(0, 0),sticky="ew")
        self.colorByPixel = ctk.CTkRadioButton(self.sidebar_frame, text = "Color by Pixel", variable=self.colorMode, value=0)
        self.colorByPixel.grid(row=6, column=0, pady=10, padx=20, sticky="nw")

        
        self.colorRandomPixels = ctk.CTkRadioButton(self.sidebar_frame, text = "Color Random Pixels", variable=self.colorMode, value=1)
        self.colorRandomPixels.grid(row=9, column=0, pady=10, padx=20, sticky="nw")
        self.NRandomPixelsSlider = ctk.CTkSlider(self.sidebar_frame, from_=0, to=1, number_of_steps=20)
        self.NRandomPixelsSlider.grid(row=10, column=0, columnspan = 5, padx=(100,5), pady=(5, 5),sticky="ew")
        self.NRandomPixelEntry = ctk.CTkEntry(self.sidebar_frame,width = 50,placeholder_text="20")
        self.NRandomPixelEntry.grid(row=10, column=0, padx=40, pady=(5, 5),sticky="w")
        self.NRandomPixelLabel = ctk.CTkLabel(self.sidebar_frame, text = 'N')
        self.NRandomPixelLabel.grid(row=10, column=0, padx=20, pady=(5, 5),sticky="w")

        self.colorByGrid = ctk.CTkRadioButton(self.sidebar_frame, text = "Color by Grid", variable=self.colorMode, value=2)
        self.colorByGrid.grid(row=11, column=0, pady=10, padx=20, sticky="nw")

        # parameter section
        self.parameterLabel = ctk.CTkLabel(self.sidebar_frame, text="Parameters",anchor="center",fg_color=self.labelColor)
        self.parameterLabel.grid(row=12, column=0, columnspan = 5, padx=(0,0), pady=(0, 0),sticky="ew")
        self.RhoSlider = ctk.CTkSlider(self.sidebar_frame, from_=0, to=1, number_of_steps=20)
        self.RhoSlider.grid(row=13, column=0, columnspan = 5, padx=(100,5), pady=(5, 5),sticky="ew")
        self.RhoLabel = ctk.CTkLabel(self.sidebar_frame, text = 'Rho')
        self.RhoLabel.grid(row=13, column=0, padx=50, pady=(5, 5),sticky="w")
        self.BetaSlider = ctk.CTkSlider(self.sidebar_frame, from_=0, to=1, number_of_steps=20)
        self.BetaSlider.grid(row=14, column=0, columnspan = 5, padx=(100,5), pady=(5, 5),sticky="ew")
        self.BetaLabel = ctk.CTkLabel(self.sidebar_frame, text = 'Beta')
        self.BetaLabel.grid(row=14, column=0, padx=50, pady=(5, 5),sticky="w")

        # appearance section
        self.appearanceLabel = ctk.CTkLabel(self.sidebar_frame, text="Appearance",anchor="center",fg_color=self.labelColor)
        self.appearanceLabel.grid(row=15, column=0, columnspan = 5, padx=(0,0), pady=(0, 0),sticky="ew")
        self.appearanceOptionMenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.changeAppearanceEvent)
        self.appearanceOptionMenu.grid(row=16, column=0, columnspan = 1, padx=20, pady=(10, 10))
        self.appearanceOptionMenu.set("Dark")
        
    def setDefaults(self):
        self.imagePath = "../images/apple.jpeg"
        self.statePath = "../states/apple.pkl"
        self.colorMode = tk.IntVar(value=0)
        

    def loadImage(self):
        print("Load Image")
    
    def saveImage(self):
        print("Save Image")

    def loadState(self):
        print("Load State")
    
    def saveState(self):
        print("Save State")

    
    def changeAppearanceEvent(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode == "light" or "system":
            self.labelColor = "#B2B2B2"
        if new_appearance_mode == "dark":
            self.labelColor = "#525252"
    

if __name__ == "__main__":
    app = imageColoriser()
    app.mainloop()
