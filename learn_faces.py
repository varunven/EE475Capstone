#TODO: fix why we cant use methods from external file without request all failure

# Learn Faces
_face_current_id = 0

def learn_faces():
	global _face_current_id
	
	name = input("Type the name and press enter to start learning\n")
	# ~ name = _face_current_id
	if(name!="quit"):
		try:
			result = huskylens.learn(_face_current_id)
			file_sentence = gtts.gTTS(text="This is " + str(name), lang='en')
			filename =  "face_" + str(_face_current_id)+".wav"
			file_sentence.save(filename)
			_face_current_id+=1
			print(result)
		except Exception as e:
			print("Failed in learn")
		
# edit name associated with face ID
def change_name(ID, newname):
	try:
		result = huskylens.learn(_face_current_id)
		file_sentence = gtts.gTTS(text="This is " + str(newname), lang='en')
		filename =  "face_" + str(_face_current_id)+".wav"
		file_sentence.save(filename)
		print(result)
	except Exception as e:
		print("failed in learn")
	
# method to be used in thread to see if any learned faces are present
def detect_faces():
	if(_current_mode == "ALGORITHM_FACE_RECOGNITION"):
		try:
			learned_blocks = huskylens.requestAll()
			for i in learned_blocks:
				ID = i.ID
				filename = "face_" + str(ID)+".wav"
				if(ID > 0):
					try:
						playsound(filename)
						print("Recognized " + str(ID))
					except Exception:
						print("Could not find face corresponding to " + str(ID))
				else:
					print("Unlearned face detected")
					response = learn_faces()
					print(response)
		except Exception:
			print("Failed in request all")
	time.sleep(0.1)
	t = threading.Thread(target=detect_faces)
	t.start()
