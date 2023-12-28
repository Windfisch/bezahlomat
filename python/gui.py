#import tkinter as tk
import ctk_wrap as tk
import re
import unicodedata
import sys
import taler
import real_money as money_acceptor
import qrcode
import time

money = taler.MoneyPool()



def money_callback(amount):
	global mode
	print("received money %s" % amount)
	money.update(amount)

def taler_money_callback(total):
	global mode
	global img
	if mode == "taler":
		print("total moneyy is %s" % total)
		uri = taler_mgr.set_amount(total)
		print(uri)

		img = qrcode.make(uri).get_image()
		print("made qrcode")

		print(img.size)
		try:
			taler_qrcode.configure(image = tk.CTkImage(img, size = (200,200)), text="")
		except Exception as e:
			print("FAIL", e)
		print("YEAY")

def taler_money_done_callback(withdrawn):
	global taler_mgr

	print("taler done (withdrawn = %s). grace time starts" % withdrawn)
	taler_mgr = None
	taler_explainer.configure(text="Vielen Dank.")
	money.update(-withdrawn)
	money_acceptor.disable()
	time.sleep(1)
	print("taler done ends, money is %s" % money.get())
	if money.get() <= 0:
		back_clicked()
	else:
		taler_clicked()
		taler_money_callback(money.get())
		taler_explainer.configure(text="Bitte nochmal\nscannen!")

def update_credit_label(total):
    credit.configure(text = "%.2f€" % total)

taler_mgr = None

money.callbacks.append(update_credit_label)
money.callbacks.append(taler_money_callback)


money_acceptor.watch(money_callback)

topratio = 0.2
botratio = 0.15

mode = "menu"

font = ("Sans", 24)
fontsmall = ("Sans", 20)

root = tk.Tk()
root.tk_strictMotif(boolean=True)

if len(sys.argv) >= 2 and sys.argv[1] == "-s":
	root.maxsize(width=509, height=340)
	root.minsize(width=509, height=340)
else:
	root.attributes("-fullscreen", True) # run fullscreen
	root.wm_attributes("-topmost", True) # keep on top



talerimg = tk.PhotoImage(file = "taler.png", size = (192,82))


def taler_clicked():
	global mode
	global taler_mgr

	message.configure(text = "GNU-Taler-Wallet aufladen")

	taler_explainer = tk.Label(master=main_taler, text="Bitte zahle den\ngewünschten\nBetrag ein\n und scanne\ndann den QR-\ncode links.", font=fontsmall)

	main_taler.lift()
	mode = "taler"
	taler_mgr = taler.TalerManager(taler.cfg, taler_money_done_callback)
	money_acceptor.enable()

def strichliste_clicked():
	global mode
	main_strichliste.lift()
	name_callback("")
	mode = "strichliste"

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
	global mode
	if mode == "taler":
		mode = "menu"
		main_welcome.lift()

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

credit = tk.Label(master=bottom, text = "0€", font=font)
credit.place(relx=0.3, relwidth=0.4, rely=0, relheight=1)

main_taler = tk.Frame(master=main)
main_taler.place(relx=0, rely=0, relwidth=1, relheight=1)

taler_qrcode = tk.Label(master=main_taler, text="(Auflade-QR-Code wird\nhier angezeigt werden.)")
taler_qrcode.place(relx=0, rely = 0, relwidth=0.6, relheight=1)

taler_explainer = tk.Label(master=main_taler, text="Bitte zahle den\ngewünschten\nBetrag ein\n und scanne\ndann den QR-\ncode links.", font=fontsmall)
taler_explainer.place(relx=.65, rely=0, relwidth=0.35, relheight=1)

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
