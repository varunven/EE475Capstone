import time

#from object_detection import detect_objects, object_detect_startup
#from object_recognition import start_client

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

# App Modes
modes = ["base", "street"]
web_app_jobs_queue = Queue()

OBJ_RECOG_CONFIDENCE_THRESHOLD = 0.25

# Current App Mode
current_mode = 0

# -----------------------BUTTON HANDLERS-------------------------------#
  
def handle_mode_change(sidewalk_detection_service):
  global current_mode
  print("change btn pressed")
  current_mode = current_mode + 1
  if (current_mode >= len(modes)):
    current_mode = 0
  
  #time.sleep(0.05)
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
  
# TODO
def handle_power_btn(x):
  pass
  
def handle_forget_btn(x):
  print("forget btn pressed!")
  
def handle_change_btn(x):
  print("CHANGING MODES")
  
def play_audio_on_startup():
  play_from_file("startup.mp3")
  
def on_exit_cleanup(obj_detect_service, sidewalk_detect_service):
  obj_detect_service.stop_detection()
  sidewalk_detect_service.stop_detection()
  
def event_listener(web_app_handler, obj_recog_worker, facial_recog_worker, obj_detect_worker):
	while True:
		event = web_app_jobs_queue.get()
		if(isinstance(event, WebAppJobChangeFaces) or isinstance(event, WebAppJobForgetFaces)):
		# ~ if event.service_name == 'change_faces' or event.service_name == 'forget_faces':
			facial_recog_worker.handle_event(event)
		elif(isinstance(event, WebAppJobObjectRecognition)):
			obj_recog_worker.handle_event(event)
		elif(isinstance(event, WebAppJobObjectDetection)):
			obj_detect_worker.handle_event(event)

# Entry point to the program
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
    

  web_app_handler = WebAppHandler(YOLO_SERVER_LINK, web_app_jobs_queue)
  audio_controller = AudioController()
  obj_recog_priority_table = PriorityTable()
  obj_detection_service = ObjectDetectionWorker()
  obj_recognition_service = ObjectRecognitionWorker(YOLO_SERVER_LINK, obj_recog_priority_table, OBJ_RECOG_CONFIDENCE_THRESHOLD, audio_controller)
  face_recognition_service = FacialRecognitionWorker(audio_controller, web_app_handler)

  sidewalk_detection_service = SidewalkDetectionWorker(YOLO_SERVER_LINK)
  
  event_listener_thread = threading.Thread(target=event_listener, args=(web_app_handler, obj_recognition_service, face_recognition_service, obj_detection_service))
  event_listener_thread.daemon = True
  event_listener_thread.start()

     # Set up buttons
  mode_switch_btn = Button(17, lambda x: handle_mode_change(sidewalk_detection_service))
  forget_faces_btn = Button(27, lambda x: face_recognition_service.forget_faces())
  learn_faces_btn = Button(22, lambda x: face_recognition_service.learn_face())
  
  #mode_switch_btn = Button(17, lambda x: print("SIDEWALK BUTTON PRESSED"))
  #forget_faces_btn = Button(27, lambda x: print("FORGET FACES BUTTON PRESSED"))
  #learn_faces_btn = Button(22, lambda x: print("LEARN FACE BUTTON PRESSED"))
  
  # Set up exit handler
  #atexit.register(lambda: on_exit_cleanup(obj_detection_service, sidewalk_detection_service))


  
  
if __name__ == "__main__":
  main()
