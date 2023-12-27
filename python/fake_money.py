import os
import threading
import time

def watch(callback):
	try:
		os.remove("/tmp/money")
	except:
		pass
	os.mkfifo("/tmp/money")

	threading.Thread(target = _watch_thread, args=(callback,)).start()

def _watch_thread(callback):
	f = open("/tmp/money", "r")
	while True:
		time.sleep(1)
		line = f.readline()
		if line == "": continue
		print("read '%s'" % line)
		try:
			amount = float(line)
			print("got amount %s" % amount)
			callback(amount)
		except Exception as e:
			print(e.format_exc())

def enable():
	print("ENABLE")

def disable():
	print("DISABLE")
