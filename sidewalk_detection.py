import threading
import time
import json
import socketio
import serial

# The SidewalkDetectionWorker class starts the sidewalk detection on a seperate thread, where it
# uses a socket to connect to the YOLO server. Via the socket, it receives the output of the sidewalk detection
# model running on the server. The output is either "Nothing Detected", "Middle of Sidewalk", "Right of Sidewalk",
# and "Left of Sidewalk". If the output received via the socket is "Right of Sidewalk", then the user needs to move
# to the right to get back on the sidewalk. Similarly, if the output is "Left of Sidewalk", then the user needs to
# move to the left. On receiving the sidewalk detections, it sends the corresponding data to the STM32 microcontroller
# via serial connection to buzz the corresponding haptic feedback pads. Takes in the YOLO server's link to connect
# to the server and receive detections
class SidewalkDetectionWorker:

    socket = socketio.Client()
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)

    def __init__(self, server_link):
        self.isDetecting = False
        self.link = server_link
        self.ser.write("NNNNNNNNNNN".encode('utf-8'))
        self.worker = threading.Thread(target=self.connect_to_server).start()
        
    # Connects the socket to the YOLO server. Attempts to reconnect every 5 seconds on disconnect.
    # Defines different event handlers depending on the event received by the socket from the YOLO server.    
    def connect_to_server(self):
        @self.socket.event
        
        # service identifies itself as obj recognition service to YOLO server on connect
        def connect():
            print('Sidewalk Detection Service: connected to YOLO server')
            self.socket.emit('sidewalk_detector')
       
        # tells the user that the service has disconnected on disconnect            
        @self.socket.event
        def disconnect():
            print('Sidewalk Detection Service: disconnected from YOLO server')
   
        # handles the "detections" event emitted by the YOLO server. Receives sidewalk detections from the server,
        # and relays that information to the STM32 microcontroller      
        @self.socket.event
        def detect_sidewalk(detection):
            if self.isDetecting:
                print(detection)
                sidewalk_state = detection["sw_state"]
                data = ""
                if (sidewalk_state == "Left of Sidewalk"):
                    data = "LLLLLLLLLLL"
                    self.ser.write(data.encode('utf-8'))
                    print(sidewalk_state)
                elif (sidewalk_state == "Right of Sidewalk"):
                    data = "RRRRRRRRRRR"
                    self.ser.write(data.encode('utf-8'))
                    print(sidewalk_state)
                else:
                    print(sidewalk_state)
                    data = "NNNNNNNNNNN"
                    self.ser.write(data.encode('utf-8'))


        if self.isDetecting:
            try:
                self.socket.connect(self.link)
                self.socket.wait()
            except Exception as e:
                print("Sidewalk Detection Service: YOLO server not yet started. Attempting to reconnect...")
                time.sleep(5)
                self.connect_to_server()
            
    # Begins the sidewalk detection service on a new thread
    def start_detection(self):
        self.isDetecting = True
        threading.Thread(target=self.connect_to_server).start()
                
    # Stops the sidewalk detection service and disconnects the socket from the YOLO server        
    def stop_detection(self):
        self.ser.write("NNNNNNNNNNN".encode('utf-8'))
        self.isDetecting = False
        self.socket.disconnect()
