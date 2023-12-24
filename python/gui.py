import tkinter as tk
import re

topratio = 0.2
botratio = 0.15

font = ("Sans", 24)
root = tk.Tk()
root.tk_strictMotif(boolean=True)
root.maxsize(width=480, height=320)
root.minsize(width=480, height=320)

talerimg = tk.PhotoImage(file = "taler.png")


def taler_clicked():
	message.config(text = "Fnord")

def strichliste_clicked():
	main_strichliste.lift()
	name_callback("")

def strip_name(n):
	return re.sub("[^a-zA-ZäöüÄÖÜ]", "", n).lower()

def matching_names(names, text):
	text = text.lower()
	matches = [(strip_name(name).find(text), name) for name in names]
	print(matches)
	print(strip_name("windfisch"))
	print("windfisch".find(text))
	matches = [(i, n)  for (i,n) in matches if i >= 0]
	matches.sort()
	return [n for i,n in matches]

def name_callback(name):
	if len(name) > 0:
		message.config(text = name)
	else:
		message.config(text = "Wie heißt du?")

	names = ["emilia", "noah", "mia", "matteo", "elias", "sophia", "sophie", "hanna", "leon", "kevin", "lukas", "laura", "anna", "julia", "katharina", "philipp", "alexander", "tobias", "daniel", "franziska"]
	
	matching = matching_names(names, name)

	for i in range(6):
		if i < len(matching):
			nameslots[i].config(text=matching[i], command = lambda name=matching[i]: name_clicked(name))
		else:
			nameslots[i].config(text="", command = lambda:None)

def name_clicked(name):
	print("going to charge %s's wallet" % name)
	message.config(text="Bitte Geld eingeben")


def back_clicked():
	pass

class Keyboard(tk.Frame):
	def __init__(self, master, callback):
		self.string = ""
		self.callback = callback
		tk.Frame.__init__(self, master)
		for i, letter in enumerate("qwertzuiopü"):
			tk.Button(master=self, text=letter, font=font, command = lambda l=letter: self.type(l)).place(relx=(i/11.5), rely = 0, relwidth=1/11.5, relheight = 1/3)
		for i, letter in enumerate("asdfghjklöä"):
			tk.Button(master=self, text=letter, font=font, command = lambda l=letter: self.type(l)).place(relx=((i+.3)/11.5), rely = 1/3, relwidth=1/11.5, relheight = 1/3)
		for i, letter in enumerate("zxcvbnm"):
			tk.Button(master=self, text=letter, font=font, command = lambda l=letter: self.type(l)).place(relx=((i+.7)/11.5), rely = 2/3, relwidth=1/11.5, relheight = 1/3)
		tk.Button(master=self, text="<--", font=font, command = lambda: self.backspace()).place(relx=((7.5+.7)/11.5), rely = 2/3, relwidth=2/11.5, relheight = 1/3)

	def type(self, letter):
		self.string += letter
		self.callback(self.string)

	def backspace(self):
		if len(self.string) > 0:
			self.string = self.string[:-1]
			self.callback(self.string)

# FIXME make root fullscreen / kiosk mode

top = tk.Frame(master=root)
bottom = tk.Frame(master=root)
main = tk.Frame(master=root)

message = tk.Label(master=top, text = "Welche Geldbörse\nmöchtest du aufladen?", font=font)
message.pack()

top.place(relx=0, rely=0, relwidth = 1, relheight = topratio)
main.place(relx=0, rely=topratio, relwidth=1, relheight = (1-topratio-botratio))
bottom.place(relx=0, rely=1-botratio, relwidth=1, relheight = botratio)

main_welcome = tk.Frame(master=main)
main_welcome.place(relx=0, rely=0, relwidth=1, relheight=1)

talerbtn = tk.Button(master=main_welcome, background = "blue", text = "GNU Taler", image=talerimg, compound=tk.TOP, font = font, command = taler_clicked)
talerbtn.place(relx = 0, rely = 0, relwidth = .5, relheight = 1)

strichlistebtn = tk.Button(master=main_welcome, background = "green", text="Strichliste", font=font, command=strichliste_clicked)
strichlistebtn.place(relx=0.5, rely = 0, relwidth=.5, relheight=1)

backbtn = tk.Button(master=bottom, background = "red", text="Zurück", font=font, command=back_clicked)
backbtn.place(relx=0, rely=0, relwidth=.3, relheight=1)

langbtn = tk.Button(master=bottom, text = "Sprache")
langbtn.place(relx=0.7, relwidth=0.3, rely=0, relheight=1)

credit = tk.Label(master=bottom, text = "13.37€", font=font)
credit.place(relx=0.3, relwidth=0.4, rely=0, relheight=1)

main_strichliste = tk.Frame(master=main)
main_strichliste.place(relx=0, rely=0, relwidth=1, relheight=1)

kbd = Keyboard(master=main_strichliste, callback = name_callback)
kbd.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

nameslots = [tk.Button(master=main_strichliste, font=font) for i in range(6)]
for i in range(3):
	nameslots[i].place(relx=0, rely=i/3*0.5, relwidth=0.5, relheight=0.5/3)
	nameslots[i+3].place(relx=0.5, rely=i/3*0.5, relwidth=0.5, relheight=0.5/3)

main_welcome.lift()


tk.mainloop()
