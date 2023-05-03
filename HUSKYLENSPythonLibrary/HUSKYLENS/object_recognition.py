import argparse
import socketio
import gtts
from playsound import playsound
import os
import uuid
import time
import json

# Set up command-line argument parser to obtain YOLO server link
parser = argparse.ArgumentParser(description='Connect to YOLO server, fetches detections, and outputs corresponding audio')
parser.add_argument('-l', '--link', required=True, help='Link to the YOLO server')
args = parser.parse_args()

# Get the server's link
YOLO_SERVER_LINK = args.link

# Set up socket to connect to server and fetch detections
socket = socketio.Client()

x = 0

@socket.event
def connect():
	print('Connected to YOLO server')
	socket.emit('see_rasp_pi')
	
	
@socket.event
def disconnect():
	print('disconnected from YOLO server')
	
@socket.event
def detections(detections):
	audio_string = 'Detected '
	global x
	x = x + 1
	# output sound for each fifth detection
	if (x % 5 == 0):
		for detection in json.loads(detections):
			print(detection)
			_class = detection['class']
			_count = detection['count']
			
			audio_string += str(_count) + ' ' + str(_class)

		audio_blob = gtts.gTTS(text=audio_string, lang='en')
		file_name = str(uuid.uuid4()) + ".wav"
		audio_blob.save(file_name)
			
		# try playing the file & remove it after playing
		# playsound is blocking
		try:
			playsound(file_name)
			os.remove(file_name)
		except Exception:
			print("Could not play file")
	print(x)
	
	
# Connect to the YOLO server
socket.connect(YOLO_SERVER_LINK)
	
	
socket.wait()
	
