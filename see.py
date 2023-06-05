from object_recognition_refactored import ObjectRecognitionWorker
from face_recognition_refactored import FacialRecognitionWorker
from object_detection_refactored import ObjectDetectionWorker
from sidewalk_detection import SidewalkDetectionWorker
from priority_table import PriorityTable
from audio_controller import AudioController
from web_app_handler import WebAppHandler, WebAppJobObjectRecognition, WebAppJobObjectDetection, WebAppJobChangeFaces, WebAppJobForgetFaces

import argparse
import time
from queue import Queue
from button import Button
from utils.audio import play_audio, create_audio_file, play_from_file
import os
import atexit
import threading

# The see.py file represents the main entry point to our SEE application running on the Raspberry Pi.
# It instantiates each of object recognition, object detection, facial recognition, and sidewalk detection
# as services that communicate with each other through this main file. The audio controller and web app 
# handler are also instantiated and passed into some of the services to enable the usage of audio
# features and communication to and from the webapp. The physical buttons are also instantiated through
# the button class, and a jobs queue is created to keep track of the list of jobs queued by the web app.


# App Modes
modes = ["base", "street"]

# Jobs queue containing jobs from web app requests
web_app_jobs_queue = Queue()

# Confidence threshold for object recognition. Detections under
# this threshold are discarded
OBJ_RECOG_CONFIDENCE_THRESHOLD = 0.25

# Current App Mode index number
current_mode = 0

# -----------------------BUTTON HANDLERS-------------------------------#

# Handles changing the SEE glasses' operating mode  
def handle_mode_change(sidewalk_detection_service):
  global current_mode
  print("change btn pressed")
  current_mode = current_mode + 1
  if (current_mode >= len(modes)):
    current_mode = 0
  
  print(f"Changing Mode from {modes[current_mode - 1]} to {modes[current_mode]}")
  audio_str = "Switching to " + modes[current_mode] + " mode"
  
  folder_path = '/home/see/EE475Capstone/HUSKYLENSPythonLibrary/HUSKYLENS/'+ modes[current_mode]+".wav"

  if (not os.path.isfile(folder_path)):
    filename =  modes[current_mode] + " mode"
    create_audio_file(audio_str, filename)
  
  play_audio(audio_str)
 
  if modes[current_mode] == "street":
    sidewalk_detection_service.start_detection()
    print("starting sidewalk detection")
  else:
    print("stopping sidewalk detection")
    sidewalk_detection_service.stop_detection()
  

# Handles stopping services that communicate with the STM32 microcontroller
# on program exit. This is to flush the serial buffer and make sure
# the haptic feedback pads are reset on program exit.
def on_exit_cleanup(obj_detect_service, sidewalk_detect_service):
  obj_detect_service.stop_detection()
  sidewalk_detect_service.stop_detection()
 

# Pulls jobs from the jobs queue and assigns them to their corresponding service worker
def event_listener(web_app_handler, obj_recog_worker, facial_recog_worker, obj_detect_worker):
	while True:
		event = web_app_jobs_queue.get()
		if(isinstance(event, WebAppJobChangeFaces) or isinstance(event, WebAppJobForgetFaces)):
			facial_recog_worker.handle_event(event)
		elif(isinstance(event, WebAppJobObjectRecognition)):
			obj_recog_worker.handle_event(event)
		elif(isinstance(event, WebAppJobObjectDetection)):
			obj_detect_worker.handle_event(event)

# Main entry point to the program
def main():
  # Set up command-line argument parser to obtain YOLO server link
  # Changed required to false because hardcoded for now
  parser = argparse.ArgumentParser(description='Connect to YOLO server, fetches detections, and outputs corresponding audio')
  parser.add_argument('-l', '--link', required=False, help='Link to the YOLO server')
  args = parser.parse_args()
  
  YOLO_SERVER_LINK = 'https://7f46-2601-602-867f-c8d0-a8b4-eee3-ec61-e127.ngrok-free.app/'
  if args.link:
    YOLO_SERVER_LINK = args.link
  else:
    print("Using hardcoded link")
    
  # Instantiate Services
  web_app_handler = WebAppHandler(YOLO_SERVER_LINK, web_app_jobs_queue)
  audio_controller = AudioController()
  obj_recog_priority_table = PriorityTable()
  obj_detection_service = ObjectDetectionWorker()
  obj_recognition_service = ObjectRecognitionWorker(YOLO_SERVER_LINK, obj_recog_priority_table, OBJ_RECOG_CONFIDENCE_THRESHOLD, audio_controller)
  face_recognition_service = FacialRecognitionWorker(audio_controller, web_app_handler)
  sidewalk_detection_service = SidewalkDetectionWorker(YOLO_SERVER_LINK)
  
  # start jobs fetcher
  event_listener_thread = threading.Thread(target=event_listener, args=(web_app_handler, obj_recognition_service, face_recognition_service, obj_detection_service))
  event_listener_thread.daemon = True
  event_listener_thread.start()

  # Set up buttons
  mode_switch_btn = Button(17, lambda x: handle_mode_change(sidewalk_detection_service))
  forget_faces_btn = Button(27, lambda x: face_recognition_service.forget_faces())
  learn_faces_btn = Button(22, lambda x: face_recognition_service.learn_face())

if __name__ == "__main__":
  main()
