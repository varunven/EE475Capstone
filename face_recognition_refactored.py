import threading
import time

from huskylib import HuskyLensLibrary
import threading
import time
from inputimeout import inputimeout
#from utils.audio import play_from_file, create_audio_file
from button import Button
import os

class FacialRecognitionWorker:


    def __init__(self, audio_controller):        
        self.huskylens = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0")
        self.audio_controller = audio_controller
        self.last_seen_face = ""
        self.current_face_id = 1
        knck = self.huskylens.algorthim("ALGORITHM_FACE_RECOGNITION")
        print("startup knock ", knck)
        # ~ self.forget_faces()
        # ~ forget_faces_btn = Button(18, self.forget_faces)
        # ~ print("resumed")
        # ~ if(True):
            # ~ self.forget_faces()        
        
        threading.Thread(target=self.detect_faces).start()
        
    def handle_event(event):
        if event.service_name == 'change_faces':
            fileName = event.fileName
            newFirstName = event.newFirstName
            newLastName = event.newLastName
            new_audio = "This is " + str(newFirstName) + str(newLastName)
            try:
                self.audio_controller.create_audio_file(new_audio, fileName)
            except Exception as e:
                print(e)
        elif event.service_name == 'forget_faces':
            self.forget_faces()
            # send new state of folder to server to send to web client for images/name audio --> another socket?
            
    # Forget data and delete audio files
    def forget_faces(self):
        time.sleep(0.5)
        print(f"Num learned objects = {self.huskylens.learnedObjCount()}")
        print(self.huskylens.forget())
        time.sleep(0.5)
        print(f"Num learned objects after forgetting = {self.huskylens.learnedObjCount()}")
        
        folder_path = '/home/see/EE475Capstone/HUSKYLENSPythonLibrary/HUSKYLENS/face_files'

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.wav') or file_name.endswith('.png'):
                try:
                    print("Deleting file " + str(file_name))
                    os.remove(folder_path + file_name)
                except Exception:
                    print("Could not delete file")
        
    def detect_faces(self):
        try:
            learned_blocks = self.huskylens.requestAll()
            for i in learned_blocks:
                ID = i.ID
                filename = "face_" + str(ID)+".wav"
                if(ID > 0):
                    try:
                        #self.audio_controller.acquire_audio_lock()
                        self.audio_controller.play_from_file(filename)
                        #self.audio_controller.release_audio_lock()
                        print("Recognized " + str(ID))
                        #self.change_name(ID)
                    except Exception:
                        print("Could not find face corresponding to " + str(ID))
                else:
                    # ~ print("Unlearned face detected")
                    #response = self.learn_faces()
                    #print(response)
                    pass
        except Exception:
            print("Failed in request all")
        time.sleep(0.1)
        t = threading.Thread(target=self.detect_faces)
        t.start()
       
    # edit name associated with face ID    
    # ~ def change_name(self, _id):
        # ~ try:
            # ~ newname = inputimeout("If you would like to change their name, type the new name and press enter\n", timeout=8)
            # ~ file_sentence = "This is " + str(newname)
            # ~ filename =  "face_" + str(_id)
            # ~ self.audio_controller.create_audio_file(file_sentence, filename)
        # ~ except Exception as e:
            # ~ print("Timeout occurred")
            
    def learn_faces(self):
        try:
            name = inputimeout("Type the name and press enter to start learning\n", timeout=8)
        except Exception:
            print("Timeout, face not learned")
            name =  "face " + str(self.current_face_id)
        try:
            result = self.huskylens.learn(self.current_face_id)
            
            # take picture with pycam and save it to /face_files/ --> doable during obj rec still?
            
            file_sentence = "This is " + str(name)
            filename =  "face_files/face_" + str(self.current_face_id)
            self.audio_controller.create_audio_file(file_sentence, filename)
            self.current_face_id += 1
            print(result)
        except Exception as e:
            print("Failed in learn")
            
    # added to learn one face on-click
    def learn_face(self):
        print("trying to learn face")
        try:
            blocks = self.huskylens.requestAll()
            if len(blocks) == 0:
                print("No face found")
                return
            for i in blocks:
                ID = i.ID
                if (ID <= 0):
                    print("unlearned face detected")
                    
                try:
                    name = inputimeout("Type the name and press enter to start learning\n", timeout=8)
                except Exception:
                    print("Timeout, face not learned")
                    
                try:
                    result = self.huskylens.learn(self.current_face_id)
                    file_sentence = "This is " + str(name)
                    filename =  "face_" + str(self.current_face_id)
                    self.audio_controller.create_audio_file(file_sentence, filename)
                    self.current_face_id += 1
                    print("Learned face , knock ", result)
                    return
                except Exception as e:
                    print("Failed in learn")
        except Exception:
            print("Failed in request all")

    def update_buffered_face(self, new_face):
        # get detections that were not present in existing detections buffer
        if (new_face != self.last_seen_face):
            self.last_seen_face = new_face   
