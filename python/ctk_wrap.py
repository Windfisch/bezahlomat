from customtkinter import *
from PIL import Image, ImageTk

_app = None

class Tk(CTk):
	def __init__(self):
		global _app
		CTk.__init__(self)
		_app = self
	pass

class PhotoImage(CTkImage):
	def __init__(self, file):
		CTkImage.__init__(self, Image.open(file))

class Frame(CTkFrame):
	pass

class Label(CTkLabel):
	pass

def _map_button_kwarg(key, value):
	if key == "background": key = "fg_color"
	if key == "foreground": key = "text_color"
	return (key,value)

class Button(CTkButton):
	def __init__(self, master, **kwargs):
		new_kwargs = dict([ _map_button_kwarg(key, value) for key, value in kwargs.items() ])
		CTkButton.__init__(self, master=master, hover=False, border_width=2,corner_radius=11, border_color='gray85', **new_kwargs)
	def configure(self, **kwargs):
		new_kwargs = dict([ _map_button_kwarg(key, value) for key, value in kwargs.items() ])
		CTkButton.configure(self, **new_kwargs)

def mainloop():
	_app.mainloop()
