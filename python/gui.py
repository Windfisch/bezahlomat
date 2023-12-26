#import tkinter as tk
import ctk_wrap as tk
import re
import unicodedata

topratio = 0.2
botratio = 0.15

font = ("Sans", 24)
fontsmall = ("Sans", 20)

root = tk.Tk()
root.tk_strictMotif(boolean=True)
root.maxsize(width=509, height=340)
root.minsize(width=509, height=340)

talerimg = tk.PhotoImage(file = "taler.png")


def taler_clicked():
	message.configure(text = "Fnord")

def strichliste_clicked():
	main_strichliste.lift()
	name_callback("")

def strip_name1(n):
	return re.sub("[^a-zA-Z]", "", n).lower()

def strip_name2(n):
	return strip_name1(unicodedata.normalize('NFD', n).encode('ASCII', 'ignore').decode())

def strip_name3(n):
	return strip_name2( n.lower().replace("ö", "oe").replace("ü", "ue").replace("ä", "ae"))

def name_distance(typed, reference):
	dists = [strip_fn(reference).find(typed) for strip_fn in  [strip_name1, strip_name2, strip_name3]]
	dists = [d for d in dists if d >= 0] + [999]
	return min(dists)


def matching_names(names, text):
	text = text.lower()
	matches = [(name_distance(text, name), name) for name in names]
	matches = [(i, n)  for (i,n) in matches if i < 999]
	matches.sort()
	return [n for i,n in matches]

def name_callback(name):
	names = ["emilia", "noah", "mia", "matteo", "elias", "renè", "sophia", "günther", "sophie", "hanna", "leon", "kevin", "lukas", "laura", "anna", "julia", "katharina", "philipp", "alexander", "tobias", "daniel", "franziska"]
	
	matching = matching_names(names, name)
	print("MATCH ", len(matching))

	if len(name) == 0:
		message.configure(text = "Wie heißt du?")
		nameslots_explainer.lift()
	elif len(matching) == 0:
		message.configure(text = name)
		nameslots_nomatches.lift()
	else:
		message.configure(text = name)
		nameslots_buttons.lift()

	for i in range(4):
		if i < len(matching):
			nameslots[i].configure(text=matching[i], state="enabled", background="blue", command = lambda name=matching[i]: name_clicked(name))
		else:
			nameslots[i].configure(text="", state="disabled", background = "gray", command = lambda:None)

def name_clicked(name):
	print("going to charge %s's wallet" % name)
	message.configure(text="Bitte Geld eingeben")


def back_clicked():
	pass

class Keyboard(tk.Frame):
	def __init__(self, master, callback):
		self.string = ""
		self.callback = callback
		tk.Frame.__init__(self, master)
		for i, letter in enumerate("qwertzuiop"):
			tk.Button(background="#555", foreground="white",master=self, text=letter, font=font, command = lambda l=letter: self.type(l)).place(relx=(i/10), rely = 0, relwidth=1/10, relheight = 1/3)
		for i, letter in enumerate("asdfghjkl"):
			tk.Button(background="#555", foreground="white",master=self, text=letter, font=font, command = lambda l=letter: self.type(l)).place(relx=((i+.3)/10), rely = 1/3, relwidth=1/10, relheight = 1/3)
		for i, letter in enumerate("yxcvbnm"):
			tk.Button(background="#555", foreground="white",master=self, text=letter, font=font, command = lambda l=letter: self.type(l)).place(relx=((i+.7)/10), rely = 2/3, relwidth=1/10, relheight = 1/3)
		tk.Button(background="#555", foreground="white",master=self, text="<--", font=font, command = lambda: self.backspace()).place(relx=((7.5+.7)/10), rely = 2/3, relwidth=2/10, relheight = 1/3)

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
kbd.place(relx=0, rely=0.4, relwidth=1, relheight=0.6)

nameslots_buttons = tk.Frame(master = main_strichliste)
nameslots_buttons.place(relx=0, rely=0, relwidth = 1, relheight = 0.4)

nameslots_explainer = tk.Label(master = main_strichliste, text="Tippe deinen Namen ein und\ntippe dann auf einen der Vorschläge.\n(Sonderzeichen/Umlaute kannst du weglassen.)", font=fontsmall)
nameslots_explainer.place(relx=0, rely=0, relwidth=1, relheight=0.4)

nameslots_nomatches = tk.Label(master = main_strichliste, text="Nichts gefunden.\nHast du dich vielleicht vertippt?", font=fontsmall)
nameslots_nomatches.place(relx=0, rely=0, relwidth=1, relheight=0.4)

nameslots = [tk.Button(master=nameslots_buttons, font=font) for i in range(4)]
for i in range(2):
	nameslots[i].place(relx=0, rely=i/2, relwidth=0.5, relheight=1/2)
	nameslots[i+2].place(relx=0.5, rely=i/2, relwidth=0.5, relheight=1/2)

main_welcome.lift()


tk.mainloop()
