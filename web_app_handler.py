import threading
import socketio
import time
import json
import asyncio


class WebAppHandler():
    
    socket = socketio.Client()


    
    def __init__(self, server_link, jobs_queue):
        self.server_link = server_link
        self.jobs_queue = jobs_queue
        self.socket.on('see-request', self.handle_see_request)
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
                request['newSettings']
            ))
            print(request['newSettings'])
        elif(request['service_name'] == 'object-detection-settings'):
            self.jobs_queue.put(WebAppJobObjectDetection(
                request['newSettings']
            ))
        elif(request['service_name'] == 'change-faces'):
            self.jobs_queue.put(WebAppJobChangeFaces(
                request['faceId'],
                request['newFirstName'],
                request['newLastName']
            ))
        elif(request['service_name'] == 'forget-faces'):
            self.jobs_queue.put(WebAppJobForgetFaces(
                request['toForget']
            ))
        return 200
        #print(callback)
    
    def handle_see_response(self, response):
        print("responding")
        print(response)
        
    def send_request(self, data, timeout):
        print("trying to send request")
        response = None
        response_received = threading.Event()
        
        def callback(name, response_code):
            print("received code = ", response_code)
            print("received name = ", name)
            nonlocal response
            response = (name, response_code)
            response_received.set()
        
        if (self.socket.connected):     
            print("emitting")   
            self.socket.emit('learn-face', data,  callback=callback)
            response_received.wait(timeout=timeout)
            print("send_request returning = ", response)
            if (response is not None):
                return response
            else:
                return ("", 500)
    
        
# ~ class WebAppJob():
    
    # ~ def __init__(self, service_name, parameter_name, new_value):
        # ~ self.service_name = service_name,
        # ~ self.parameter_name = parameter_name,
        # ~ self.new_value = new_value
     
class WebAppJobObjectRecognition():
    
    def __init__(self, settings):
        self.volumeControl = settings['volumeControl']
        self.isAudioOn = settings['isAudioOn']
        self.voiceGender = settings['voiceGender']
        self.objsPriority = settings['objsPriority']
        self.audioPlaybackTime = settings['audioPlaybackTime']

class WebAppJobObjectDetection():
    
    def __init__(self, settings):
        self.nearCutoff = settings['nearCutoff']
        self.midCutoff = settings['midCutoff']
        self.farCutoff = settings['farCutoff']
        self.isHapticOn = settings['isHapticOn']

class WebAppJobChangeFaces():
    
    def __init__(self, faceId, newFirstName, newLastName):
        self.faceId = faceId
        self.newFirstName = newFirstName
        self.newLastName = newLastName

class WebAppJobForgetFaces():
    
    def __init__(self, toForget):
        self.toForget = toForget
