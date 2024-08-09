import customtkinter as ctk
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Toolbar(tkagg.NavigationToolbar2Tk):
    def __init__(self, canvas: FigureCanvasTkAgg, imageFrame: ctk.CTkFrame):
        super().__init__(canvas, imageFrame)

    def configure(self):
        self.set_message = lambda x: ""
        self.config(background="gray16")
        self.children["!button2"].pack_forget()
        self.children["!button3"].pack_forget()
        self.children["!button4"].pack_forget()
        self._message_label.config(
            background="gray16"
        )  # TODO: make the checkboxes dark blue when selected
        for button in self.winfo_children()[0:-2]:
            button.configure(
                background="#3A7EBF",
                highlightbackground="#325882",
                # highlightcolor="#325882",
                # fg="#325882",
                # activeforeground="#325882",
                # activebackground="#325882",
            )
        self.winfo_children()[-2].configure(background="gray16")
        self.update()
        self.pack(side="bottom", padx=3, pady=3)
