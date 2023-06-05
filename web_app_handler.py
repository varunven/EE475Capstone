import threading
import socketio
import time
import json
import asyncio

# The WebAppHandler class uses socket communication to communicate with the web app. It listens
# for see-requests coming from the web app, and sends back responses. These requests are relayed
# to the different service workers.
class WebAppHandler():
    
    socket = socketio.Client()


    
    def __init__(self, server_link, jobs_queue):
        self.server_link = server_link
        self.jobs_queue = jobs_queue
        self.socket.on('see-request', self.handle_see_request)
        threading.Thread(target=self.connect_to_server).start()
        
    # Connects the socket to the YOLO server. Attempts to reconnect every 5 seconds on disconnect.
    # Defines different event handlers depending on the event received by the socket from the YOLO server.      
    def connect_to_server(self):

        # service identifies itself as obj recognition service to YOLO server on connect
        @self.socket.event
        def connect():
            print('Web App Handler: connected to YOLO server')
            self.socket.emit("web-app-handler")
         
        # tells the user that the service has disconnected on disconnect            
        @self.socket.event
        def disconnect():
            print('Web App Handler: disconnected from YOLO server')
            
        try:
            self.socket.connect(self.server_link)
            self.socket.wait()
        except Exception as e:
            print("Web App Handler: YOLO server not yet started. Attempting to reconnect...")
            time.sleep(5)
            self.connect_to_server()

    # receives a see-request from the web-app, parses it, and puts it in the jobs queue.
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
    
    # sends a request to the webapp, with the payload = data. If a response takes longer than timeout
    # then the request fails    
    def send_request(self, data, timeout):
        response = None
        response_received = threading.Event()
        
        def callback(name, response_code):
            nonlocal response
            response = (name, response_code)
            response_received.set()
        
        if (self.socket.connected):      
            self.socket.emit('learn-face', data,  callback=callback)
            response_received.wait(timeout=timeout)
            print("send_request returning = ", response)
            if (response is not None):
                return response
            else:
                return ("", 500)
    
 
# Represents a object recognition job or request
class WebAppJobObjectRecognition():
    
    def __init__(self, settings):
        self.volumeControl = settings['volumeControl']
        self.isAudioOn = settings['isAudioOn']
        self.voiceGender = settings['voiceGender']
        self.objsPriority = settings['objsPriority']
        self.audioPlaybackTime = settings['audioPlaybackTime']

# Represents a object detection job or request
class WebAppJobObjectDetection():
    
    def __init__(self, settings):
        self.nearCutoff = settings['nearCutoff']
        self.midCutoff = settings['midCutoff']
        self.farCutoff = settings['farCutoff']
        self.isHapticOn = settings['isHapticOn']

# Represents a change faces job or request
class WebAppJobChangeFaces():
    
    def __init__(self, faceId, newFirstName, newLastName):
        self.faceId = faceId
        self.newFirstName = newFirstName
        self.newLastName = newLastName

# Represents a forget faces job or request
class WebAppJobForgetFaces():
    
    def __init__(self, toForget):
        self.toForget = toForget
