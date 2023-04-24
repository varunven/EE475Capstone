from huskylib import HuskyLensLibrary
from enum import Enum, auto

import gtts
from playsound import playsound

import threading, time

import json

huskylens = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0")

_global_arrows = []
_global_blocks = []
_in_memory_map_id_to_name = {}

def print_blocks(block_array):
	for obj in block_array:
		tostr = ""
		tostr += str(obj.x) + "\n"
		tostr += str(obj.y) + "\n"
		tostr += str(obj.ID)
		print(tostr)

# Declare Modes

class mode(Enum):
	KNOCK = "KNOCK"
	OBJ_RECOGNITION = "YOLO_OBJECT_RECOGNITION"
	FACE_RECOGNITION = "ALGORITHM_FACE_RECOGNITION"
	LINE_TRACKING = "ALGORITHM_LINE_TRACKING"

# control algorithms
def switch_to_face_recognition():
	huskylens.algorthim("ALGORITHM_FACE_RECOGNITION")

def switch_to_line_tracking():
	huskylens.algorthim("ALGORITHM_LINE_TRACKING")

def switch_to_object_recognition():
	huskylens.algorthim("ALGORITHM_OBJECT_RECOGNITION")
	
def switch_to_object_classification():
	huskylens.algorthim("ALGORITHM_OBJECT_CLASSIFICATION")

def switch_to_default():
	switch_to_line_tracking()

def learn(name, current_id):
	try:
		result = huskylens.learn(current_id)
		print(result)
	except Exception as e:
		print(e)
		
# learn faces
def learn_faces(name, current_id):
	try:
		result = huskylens.learn(current_id)
		_in_memory_map_id_to_name[current_id] = name
		test = gtts.gTTS(text="We recognize this face as" + str(name), lang='en')
		filename = str(current_id)+".wav"
		test.save(filename)
		print(result)
	except Exception as e:
		print(e)

# Decode the data generated by the HuskyLens.
def decodeHuskyLens(obj):
	count=1
	if(type(obj)==list):
		print("List object\n")
		for i in obj:
			print("\t " + ("BLOCK_" if i.type=="BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(i.__dict__))
			self.husky_lens_ID = json.loads(json.dumps(i.__dict__))["ID"]
			count+=1
	else:
		print("Not list object\n")
		print("\t " + ("BLOCK_" if obj.type=="BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(obj.__dict__))
		self.husky_lens_ID = json.loads(json.dumps(obj.__dict__))["ID"]

		# Get the recently read block from the HuskyLens to detect the object ID.
		self.decodeHuskyLens(self.husky_lens.blocks())

def knock():
	print(huskylens.knock())
	playsound("knock.wav")
	time.sleep(5)
	t = threading.Thread(target=knock)
	t.start()
	
def framenumber():
	print("frames processed: " + str(huskylens.frameNumber()))
	time.sleep(5)
	t = threading.Thread(target=framenumber)
	t.start()
	
def count():
	print("count: " + str(huskylens.count()))
	time.sleep(5)
	t = threading.Thread(target=count)
	t.start()

# -- BUGGY- always empty. What is proper input/output?
def process_blocks():
	global_blocks = huskylens.blocks()
	print("blocks:\n" + str(global_blocks))

# -- BUGGY- always empty. What is proper input/output?
def process_arrows():
	global_arrows = huskylens.arrows()
	print("arrows:\n" + str(global_arrows))
	time.sleep(5)
	t = threading.Thread(target=process_arrows)
	t.start()
	
def lens_display(text, X, Y):
	huskylens.customText(text, X, Y)
	time.sleep(10)
	huskylens.clearText()

# Entry point to the program
def main():
	current_id = 1
	switch_to_face_recognition()
	time.sleep(0.5)

	test = gtts.gTTS(text="Knock confirmed", lang='en')
	test.save("knock.wav")
		
	print(huskylens.learnedObjCount())
	
	print(huskylens.forget())
	time.sleep(0.5)
	
	print(huskylens.learnedObjCount())
	
# Face recognition
	name = input("Type the name and press enter to start learning\n")
	learn_faces(name, current_id)
			
	current_id+=1
	name = input("Type the name and press enter to start learning\n")
	learn_faces(name, current_id)
		
	current_id+=1
	name = input("Type the name and press enter to start learning\n")
	learn_faces(name, current_id)
	
	while True:
		try:
			blocks = learned()
			for i in blocks:
				ID = i.ID
				filename = str(ID)+".wav"
				playsound(filename)
		except Exception as e:
			print(e)
	
	print(str(_in_memory_map_id_to_name))
	
# Threading for test methods
	# ~ threads = []
	
	# ~ knock_thread = threading.Thread(target=knock)
	# ~ threads.append(knock_thread)
	# ~ knock_thread.start()
		
	# ~ frame_thread = threading.Thread(target=framenumber)
	# ~ threads.append(frame_thread)
	# ~ frame_thread.start()
	
	# ~ count_thread = threading.Thread(target=count)
	# ~ threads.append(count_thread)
	# ~ count_thread.start()
	
	# ~ blocks_thread = threading.Thread(target=process_blocks)
	# ~ threads.append(blocks_thread)
	# ~ blocks_thread.start()
	
	# ~ arrows_thread = threading.Thread(target=process_arrows)
	# ~ threads.append(arrows_thread)
	# ~ arrows_thread.start()
	
	# ~ lens_display_thread = threading.Thread(target=lens_display, args=("Welcome to S.E.E.", 85, 30, ))
	# ~ threads.append(lens_display_thread)
	# ~ lens_display_thread.start()

if __name__ == "__main__":
	main()
