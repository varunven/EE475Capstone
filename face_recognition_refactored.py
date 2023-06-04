import threading
import time

from huskylib import HuskyLensLibrary
import threading
import time
from inputimeout import inputimeout
#from utils.audio import play_from_file, create_audio_file
from button import Button
import os

from web_app_handler import WebAppJobChangeFaces, WebAppJobForgetFaces

huskylens = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0")

class FacialRecognitionWorker:


    def __init__(self, audio_controller, web_app_handler):        
        # ~ try:
            # ~ self.huskylens = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0")
        # ~ except Exception as e:
            # ~ print("USB 0 did not work.. trying USB1")
            # ~ try:
                # ~ self.huskylens = HuskyLensLibrary("SERIAL", "/dev/ttyUSB1")
            # ~ except Exception as e:
                # ~ print("LMFAOOOOOO")
                # ~ quit()
        self.audio_controller = audio_controller
        self.last_seen_face = ""
        self.current_face_id = 1
        self.web_app_handler = web_app_handler
        self.face_lock = threading.Lock()
        knck = huskylens.algorthim("ALGORITHM_FACE_RECOGNITION")
        time.sleep(0.20)
        print("startup knock ", knck)
          # ~ forget_faces_btn = Button(27, lambda x: face_recognition_service.forget_faces())
  # ~ learn_faces_btn = Button(22, lambda x: face_recognition_service.learn_face())
        self.forget_faces()


        
        threading.Thread(target=self.detect_faces).start()
        
    def handle_event(self, event):
        folder_path = '/home/see/EE475Capstone/HUSKYLENSPythonLibrary/HUSKYLENS/face_files'
        
        if(isinstance(event, WebAppJobChangeFaces)):
            faceId = event.faceId
            fileName = folder_path+"face_"+str(faceId)+".wav"
            newFirstName = event.newFirstName
            newLastName = event.newLastName
            new_audio = "This is " + str(newFirstName) + str(newLastName)
            try:
                self.audio_controller.create_audio_file(new_audio, fileName)
                # receive the new fileName from server --> server will change the file in cloud automatically
                # send audio file and fileName to socket --> there, change the existing fileName.wav to be this one
                response = "Changed the name successfully"
                return response
            except Exception as e:
                print(e)
                response = e+", Could not forget all learned faces"
                return response
        elif(isinstance(event, WebAppJobForgetFaces)):
            self.forget_faces()
            response = "All learned faces have been forgotten"
            return response
            # send new state of folder to server to send to web client for images/name audio --> another socket?
            
    # Forget data and delete audio files
    def forget_faces(self):
        self.current_face_id = 1
        self.face_lock.acquire()
        print(f"Num learned objects = {huskylens.learnedObjCount()}")
        time.sleep(0.5)
        print("Forget result: ", huskylens.forget())
        time.sleep(0.5)
        print(f"Num learned objects after forgetting = {huskylens.learnedObjCount()}")
        time.sleep(0.5)
        
        folder_path = '/home/see/EE475Capstone/HUSKYLENSPythonLibrary/HUSKYLENS/face_files/'

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.wav'):
                try:
                    print("Deleting file " + str(file_name))
                    os.remove(folder_path + file_name)
                except Exception as e:
                    print(e)
        self.face_lock.release()
    def detect_faces(self):
        print("starting face detection")
        while(True):
            try:
                time.sleep(0.1)
                self.face_lock.acquire()
                learned_blocks = huskylens.requestAll()
                self.face_lock.release()
                for i in learned_blocks:
                    ID = i.ID
                    folder_path = "/home/see/EE475Capstone/HUSKYLENSPythonLibrary/HUSKYLENS/face_files/"
                    filename = folder_path+"face_" + str(ID)+".wav"
                    print("Found face ID ", ID)
                    if(ID > 0):
                        try:
                            #self.audio_controller.acquire_audio_lock()
                            self.audio_controller.play_from_file(filename)
                            #self.audio_controller.release_audio_lock()
                            print("Recognized " + str(ID))
                            #self.change_name(ID)
                            time.sleep(1.5)
                        except Exception:
                            print("Could not find face corresponding to " + str(ID))
                    else:
                        # ~ print("Unlearned face detected")
                        pass
            except Exception as e:
                print(e)
        # ~ time.sleep(0.1)
        # ~ t = threading.Thread(target=self.detect_faces)
        # ~ t.start()
       
    # edit name associated with face ID    
    # ~ def change_name(self, _id):
        # ~ try:
            # ~ newname = inputimeout("If you would like to change their name, type the new name and press enter\n", timeout=8)
            # ~ file_sentence = "This is " + str(newname)
            # ~ filename =  "face_" + str(_id)
            # ~ self.audio_controller.create_audio_file(file_sentence, filename)
        # ~ except Exception as e:
            # ~ print("Timeout occurred")
            
    # ~ def learn_faces(self):
        # ~ try:
            # ~ name = inputimeout("Type the name and press enter to start learning\n", timeout=8)
        # ~ except Exception:
            # ~ print("Timeout, face not learned")
            # ~ name =  "face " + str(self.current_face_id)
        # ~ try:
            # ~ result = self.huskylens.learn(self.current_face_id)
                        
            # ~ file_sentence = "This is " + str(name)
            # ~ filename =  "face_files/face_" + str(self.current_face_id)
            # ~ self.audio_controller.create_audio_file(file_sentence, filename)
            # ~ self.current_face_id += 1
            # ~ print(result)
        # ~ except Exception as e:
            # ~ print("Failed in learn")
            
    # added to learn one face on-click
    def learn_face(self):
        self.face_lock.acquire()
        print("trying to learn face")
        #self.web_app_handler.send_request(1, 10)
        blocks = huskylens.requestAll()
        self.face_lock.release()
        #time.sleep(0.5)
        if len(blocks) == 0:
            print("No face found")
            return
        for i in blocks:
            ID = i.ID
            if (ID <= 0):
                print("unlearned face detected")
                
            # ~ try:
                # ~ #name = inputimeout("Type the first and last name and press enter to start learning\n", timeout=8)
                # ~ #self.web_app_handler.send_request(1, 10)
            # ~ except Exception as e:
                # ~ print (e)
                # ~ print("Timeout, face not learned")
                name = "face " + str(self.current_face_id)
            try:
                #result = self.huskylens.learn(self.current_face_id)
                hasLearned = self.our_learn()
                if (hasLearned):
                    print("Learned step 1")
                    name, response_code = self.web_app_handler.send_request(self.current_face_id, 20)
                    print(f"got name = {name} and code = {response_code}")
                    if (name == "" or response_code == 500):
                        print("Error contacting server.")
                        return
                    file_sentence = "This is " + str(name)
                    folder_path = "/home/see/EE475Capstone/HUSKYLENSPythonLibrary/HUSKYLENS/face_files/"
                    filename =  folder_path+"face_" + str(self.current_face_id)
                    # send faceId to socket --> take a picture to name as face_2.jpg, send faceId and name (will be stored as first_last_faceid.png)
                    self.audio_controller.create_audio_file(file_sentence, filename)
                    #self.current_face_id += 1
                    #print("Learned face ", result)
                    self.current_face_id += 1
                    threading.Thread(target=self.detect_faces).start()
                    return
                else:
                    print("Our learn is false :/")
                    threading.Thread(target=self.detect_faces).start()
            except Exception as e:
                print(e)
                threading.Thread(target=self.detect_faces).start()

    def update_buffered_face(self, new_face):
        # get detections that were not present in existing detections buffer
        if (new_face != self.last_seen_face):
            self.last_seen_face = new_face   
            
    def our_learn(self):
        self.face_lock.acquire()
        try:
            prev = huskylens.learnedObjCount()
            time.sleep(0.5)
            huskylens.learn(self.current_face_id)
            time.sleep(0.5)
            after = huskylens.learnedObjCount()
            time.sleep(0.5)
            print("before = ", prev, " after = ", after)
            # learning worked
            if (after - prev == 1):
                self.face_lock.release()
                print("LEARNED FACE")
                return True
            else:
                self.face_lock.release()
                return False
        except Exception as e:
            print(e)
            self.face_lock.release()
            return False
