import threading
import time
import serial
import RPi.GPIO as GPIO


class ObjectDetectionWorker:

    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    GPIO_TRIGGER_L = 18
    GPIO_ECHO_L = 24
    GPIO_TRIGGER_R = 23
    GPIO_ECHO_R = 15

    def __init__(self):
        self.objDetectionDistanceNear = 40
        self.objDetectionDistanceMid = 100
        self.objDetectionDistanceFar = 200
        self.hapticFeedbackState = True
        
        self.ser.flush()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_TRIGGER_L, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO_L, GPIO.IN)
        GPIO.setup(self.GPIO_TRIGGER_R, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO_R, GPIO.IN)
        self.object_detect_startup()
        threading.Thread(target=self.detect_objects).start()
        
    def object_detect_startup(self):
        #reset GPIO output pins
        GPIO.output(self.GPIO_TRIGGER_L, False)
        GPIO.output(self.GPIO_TRIGGER_R, False)
        time.sleep(2)
        
    def handle_event(event):
        self.objDetectionDistanceNear = event.objDetectionDistanceNear
        self.objDetectionDistanceMid = event.objDetectionDistanceMid
        self.objDetectionDistanceFar = event.objDetectionDistanceFar
        self.hapticFeedbackState = event.hapticFeedbackState
        
        
    # calculate distance for sensor given as parameter
    def distance(self, side):
        if (side == 0):
            # set Trigger to HIGH
            GPIO.output(self.GPIO_TRIGGER_L, True)

            # set Trigger after 0.01ms to LOW
            time.sleep(0.00001)
            GPIO.output(self.GPIO_TRIGGER_L, False)

            StartTime = time.time()
            StopTime = time.time()

            # save StartTime
            while GPIO.input(self.GPIO_ECHO_L) == 0:
                StartTime = time.time()

            # save time of arrival
            while GPIO.input(self.GPIO_ECHO_L) == 1:
                StopTime = time.time()

            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            distance = (TimeElapsed * 34300) / 2
        else:
            # set Trigger to HIGH
            GPIO.output(self.GPIO_TRIGGER_R, True)

            # set Trigger after 0.01ms to LOW
            time.sleep(0.00001)
            GPIO.output(self.GPIO_TRIGGER_R, False)

            StartTime = time.time()
            StopTime = time.time()

            # save StartTime
            while GPIO.input(self.GPIO_ECHO_R) == 0:
                StartTime = time.time()

            # save time of arrival
            while GPIO.input(self.GPIO_ECHO_R) == 1:
                StopTime = time.time()

            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            distance = (TimeElapsed * 34300) / 2
        return distance

    # method to be used in thread to detect objects
    def detect_objects(self):
        try:
            dist_L = self.distance(0)
            #print ("Measured Distance left  = %.1f cm" % dist_L)
            time.sleep(0.05)
            dist_R = self.distance(1)
            #print ("Measured Distance right = %.1f cm" % dist_R)
            time.sleep(0.05)
            
            # ~ # 20 is value we determined to define a 'centered' object
            # ~ if dist_R-dist_L > 20:
                # ~ #print("Object is to the left")
                # ~ pass
            # ~ elif dist_L-dist_R > 20:
                # ~ #print("Object is to the right")
                # ~ pass
            # ~ else:
                # ~ #print("Object is in the center")
                # ~ pass
            if(self.hapticFeedbackState):
                self.program_sensor(dist_L, dist_R)
            time.sleep(0.1)
            t = threading.Thread(target=self.detect_objects).start()

        # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            print("Measurement stopped by User")
            GPIO.cleanup()
      
    # Send inputs to microcontroller based on distance
    def program_sensor(self, left, right):
        if (left > self.objDetectionDistanceFar):
            data = "00000000000" # Replace this with your sensor data
            #print("program sending left " + str(left))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.objDetectionDistanceMid < left and left <= self.objDetectionDistanceFar):
            data = "33333333333" # Replace this with your sensor data
            #print("program sending left" + str(left))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.objDetectionDistanceNear < left and left <= self.objDetectionDistanceMid):
            data = "22222222222" # Replace this with your sensor data
            #print("program sending left" + str(left))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (left <= self.objDetectionDistanceNear):
            data = "11111111111" # Replace this with your sensor data
            #print("program sending left" + str(left))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        if (right > self.objDetectionDistanceFar):
            data = "44444444444" # Replace this with your sensor data
            #print("program sending right " + str(right))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.objDetectionDistanceMid < right and right <= self.objDetectionDistanceFar):
            data = "77777777777" # Replace this with your sensor data
            #print("program sending right" + str(right))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.objDetectionDistanceNear < right and right <= self.objDetectionDistanceMid):
            data = "66666666666" # Replace this with your sensor data
            #print("program sending right" + str(right))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (right <= self.objDetectionDistanceNear):
            data = "55555555555" # Replace this with your sensor data
            #print("program sending right" + str(right))
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)      
            
    def stop_detection(self):
        print("off")
        self.ser.write("00000000000".encode("utf-8"))
        time.sleep(0.01)
        #self.ser.write("00000000000".encode("utf-8"))
        #time.sleep(0.01)
        #self.ser.write("44444444444".encode("utf-8"))
        #time.sleep(0.01)
        self.ser.write("44444444444".encode("utf-8"))
        time.sleep(0.01)
        self.ser.flush()
        GPIO.cleanup()

