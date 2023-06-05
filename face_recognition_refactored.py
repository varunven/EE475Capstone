import threading
import time

from huskylib import HuskyLensLibrary
import threading
import time
from button import Button
import os

from web_app_handler import WebAppJobChangeFaces, WebAppJobForgetFaces

huskylens = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0")

# The FacialRecogntionWorker is a class that runs the face recognition service. It starts a new thread
# that actively tries to detect new faces via the HuskyLens. It takes in an audio_controller to play
# voicelines (face names) and/or save learned faces as a specific name. It takes in the web_app_handler
# in order to send and receive requests to and from the webapp when learning a face
class FacialRecognitionWorker:


    def __init__(self, audio_controller, web_app_handler):        
        self.audio_controller = audio_controller
        self.current_face_id = 1
        self.web_app_handler = web_app_handler
        self.face_lock = threading.Lock()
        knck = huskylens.algorthim("ALGORITHM_FACE_RECOGNITION")
        time.sleep(0.20)
        print("startup knock ", knck)
        self.forget_faces()


        
        threading.Thread(target=self.detect_faces).start()
      
    # handles web app requests related to facial recognition. Involves requests such as changing a learned face's name
    # and forgetting all faces learned. Note: This feature has not made the final demo.
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
            
    # Forget all learned faces and delete corresponding audio files
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
        
        
    # detect all faces in a scene. For all faces that are known (learned), play their corresponding name's audio
    def detect_faces(self):
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
                            self.audio_controller.play_from_file(filename)
                            print("Recognized " + str(ID))
                            time.sleep(1.5)
                        except Exception:
                            print("Could not find face corresponding to " + str(ID))
                    else:
                        pass
            except Exception as e:
                print(e)
            
    # Attempts to learn an unknown face in the scene. If a face is learned, sends a request to the webapp,
    # where the user enters the person's name. The webapp responds with the entered name, which is converted
    # to an mp3 file and saved.
    def learn_face(self):
        self.face_lock.acquire()
        blocks = huskylens.requestAll()
        self.face_lock.release()
        if len(blocks) == 0:
            # no faces found
            return
        for i in blocks:
            ID = i.ID
            if (ID <= 0):
                # unlearned face detected
                name = "face " + str(self.current_face_id)
            try:
                hasLearned = self.our_learn()
                if (hasLearned):
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
                    self.current_face_id += 1
                    threading.Thread(target=self.detect_faces).start()
                    return
                else:
                    threading.Thread(target=self.detect_faces).start()
            except Exception as e:
                print(e)
                threading.Thread(target=self.detect_faces).start() 
      
    # Wrapper function for the HuskyLens' learn function that returns
    # whether or not a face was actually learned
    def our_learn(self):
        self.face_lock.acquire()
        try:
            prev = huskylens.learnedObjCount()
            time.sleep(0.5)
            huskylens.learn(self.current_face_id)
            time.sleep(0.5)
            after = huskylens.learnedObjCount()
            time.sleep(0.5)
            # learning worked
            if (after - prev == 1):
                self.face_lock.release()
                return True
            else:
                self.face_lock.release()
                return False
        except Exception as e:
            print(e)
            self.face_lock.release()
            return False
