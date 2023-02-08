import customtkinter as ctk


class waitingWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.label = ctk.CTkLabel(self, text="Generating image, please wait...")
        self.label.pack(padx=20, pady=20)
        self.update()
