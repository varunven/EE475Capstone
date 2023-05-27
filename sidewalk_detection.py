import threading
import time
import json
import socketio
import serial

class SidewalkDetectionWorker:

    socket = socketio.Client()
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)

    def __init__(self, server_link):
        self.isDetecting = False
        self.link = server_link
        self.ser.write("NNNNNNNNNNN".encode('utf-8'))
        self.worker = threading.Thread(target=self.connect_to_server).start()
        
        
    def connect_to_server(self):
        @self.socket.event
        def connect():
            print('Sidewalk Detection Service: connected to YOLO server')
            self.socket.emit('sidewalk_detector')
                 
        @self.socket.event
        def disconnect():
            print('Sidewalk Detection Service: disconnected from YOLO server')
            
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
            
    
    def start_detection(self):
        self.isDetecting = True
        threading.Thread(target=self.connect_to_server).start()
                
            
    def stop_detection(self):
        self.ser.write("NNNNNNNNNNN".encode('utf-8'))
        self.isDetecting = False
        self.socket.disconnect()
