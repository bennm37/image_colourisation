import customtkinter as ctk


class waitingWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        # super().__init__()

        super().__init__(*args, **kwargs)
        # l = ctk.CTkLabel(self, text="Input")
        # l.grid(row=0, column=0)
        #
        # b = ctk.CTkButton(self, text="Okay", command=self.destroy)
        # b.grid(row=1, column=0)
        self.label = ctk.CTkLabel(
            self, text="Generating image, please wait...", width=500
        )
        self.label.grid(row=0, column=0)
        self.update()
        self.grab_release()
