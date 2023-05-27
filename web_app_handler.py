import threading
import socketio
import time
import json


class WebAppHandler():
    
    socket = socketio.Client()


    
    def __init__(self, server_link, jobs_queue):
        self.server_link = server_link
        self.jobs_queue = jobs_queue
        self.socket.on('see_request', self.handle_see_request)
        threading.Thread(target=self.connect_to_server).start()
        
        
    def connect_to_server(self):

        @self.socket.event
        def connect():
            print('Web App Handler: connected to YOLO server')
            self.socket.emit("web-app-handler")
                    
        @self.socket.event
        def disconnect():
            print('Web App Handler: disconnected from YOLO server')
            

        #@self.socket.on('see_request')
        #def see_request(request):


        try:
            self.socket.connect(self.server_link)
            self.socket.wait()
        except Exception as e:
            print("Web App Handler: YOLO server not yet started. Attempting to reconnect...")
            time.sleep(5)
            self.connect_to_server()

    def handle_see_request(self, request):
        print(f'obtained request = {request}')
        if(request['service_name'] == 'object-recognition-settings'):
            self.jobs_queue.put(WebAppJobObjectRecognition(
                request['volume'],
                request['dist'],
                request['audioEnable'],
                request['objRecognitionVoice'],
                request['objMap'],
                request['audioPlayBackTime']
            ))
        elif(request['service_name'] == 'object-detection-settings'):
            self.jobs_queue.put(WebAppJobObjectRecognition(
                request['objDetectionDistanceNear'],
                request['objDetectionDistanceMid'],
                request['objDetectionDistanceFar'],
                request['hapticFeedbackState']
            ))
        elif(request['service_name'] == 'change-faces'):
            self.jobs_queue.put(WebAppJobObjectRecognition(
                request['fileName'],
                request['newFirstName'],
                request['newLastName']
            ))
        elif(request['service_name'] == 'forget-faces'):
            self.jobs_queue.put(WebAppJobObjectRecognition(
                request['toForget']
            ))
        
        
# ~ class WebAppJob():
    
    # ~ def __init__(self, service_name, parameter_name, new_value):
        # ~ self.service_name = service_name,
        # ~ self.parameter_name = parameter_name,
        # ~ self.new_value = new_value

class WebAppJobObjectRecognition():
    
    def __init__(self, volume, dist, audioEnable, objRecognitionVoice, objList, audioPlayBackTime):
        self.volume = volume,
        self.dist = dist,
        self.audioEnable = audioEnable,
        self.objRecognitionVoice = objRecognitionVoice,
        self.objList = objList,
        self.audioPlayBackTime = audioPlayBackTime
        
class WebAppJobObjectDetection():
    
    def __init__(self, newVolume, newDist, audioEnable, objRecognitionVoice, objMap, audioPlayBackTime):
        self.newVolume = newVolume,
        self.newDist = newDist,
        self.audioEnable = audioEnable,
        self.objRecognitionVoice = objRecognitionVoice,
        self.objMap = objMap,
        self.audioPlayBackTime = audioPlayBackTime

class WebAppJobChangeFaces():
    
    def __init__(self, fileName, newFirstName, newLastName):
        self.fileName = fileName,
        self.newFirstName = newFirstName
        self.newLastName = newLastName

class WebAppJobForgetFaces():
    
    def __init__(self, toForget):
        self.toForget = toForget
