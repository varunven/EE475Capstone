import threading
import time
import serial
import RPi.GPIO as GPIO

# The ObjectDetectionWorker class starts the object detection service on a seperate thread, where it
# measures distance using the two ultrasonic sensors (left and right) on the SEE glasses, and relays
# that data to the STM32 microcontroller through serial connection.
class ObjectDetectionWorker:

    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    GPIO_TRIGGER_L = 18
    GPIO_ECHO_L = 24 
    GPIO_TRIGGER_R = 23
    GPIO_ECHO_R = 15

    def __init__(self):
        self.nearCutoff = 40
        self.midCutoff = 100
        self.farCutoff = 200
        self.isHapticOn = True
        
        self.ser.flush()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_TRIGGER_L, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO_L, GPIO.IN)
        GPIO.setup(self.GPIO_TRIGGER_R, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO_R, GPIO.IN)
        self.object_detect_startup()
        threading.Thread(target=self.detect_objects).start()
        
    # Used on service startup to reset GPIO output pins
    def object_detect_startup(self):
        GPIO.output(self.GPIO_TRIGGER_L, False)
        GPIO.output(self.GPIO_TRIGGER_R, False)
        time.sleep(2)
    
    # handles web app requests related to object detection. Receives requests that update the settings
    # for object detection, such as changing the nearCutoff, midCutoff, farCutOff parameters, as well
    # as enabling or disabling haptic feedback
    def handle_event(self, event):
        self.nearCutoff = event.nearCutoff
        self.midCutoff = event.midCutoff
        self.farCutoff = event.farCutoff
        self.isHapticOn = event.isHapticOn
        response = "Updated state values for object detection"
        print(response)
        return response
             
    # calculate distance detected by the sensor, where side = 0 represents left sensor, side = 1 is right
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

    # Measures distance using the two sensors, and sends that data to the STM32 via serial connection
    def detect_objects(self):
        try:
            dist_L = self.distance(0)
            time.sleep(0.05)
            dist_R = self.distance(1)
            time.sleep(0.05)

            if(self.isHapticOn):
                self.program_sensor(dist_L, dist_R)
            else:
                self.program_sensor(1000, 1000)
            time.sleep(0.1)
            t = threading.Thread(target=self.detect_objects).start()

        # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            print("Measurement stopped by User")
            GPIO.cleanup()
      
    # Send inputs to microcontroller based on distance, which are used to buzz the
    # haptic feedback pads based on the values passed.
    def program_sensor(self, left, right):
        if (left > self.farCutoff):
            data = "00000000000" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.midCutoff < left and left <= self.farCutoff):
            data = "33333333333" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.nearCutoff < left and left <= self.midCutoff):
            data = "22222222222" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (left <= self.nearCutoff):
            data = "11111111111" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        if (right > self.farCutoff):
            data = "44444444444" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.midCutoff < right and right <= self.farCutoff):
            data = "77777777777" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (self.nearCutoff < right and right <= self.midCutoff):
            data = "66666666666" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)
            
        elif (right <= self.nearCutoff):
            data = "55555555555" # Replace this with your sensor data
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.01)
            self.ser.write(data.encode('utf-8'))
            time.sleep(0.05)      
            
    # sends "turn off" commands to microcontroller to turn off haptic feedback pads
    # and stops object detection
    def stop_detection(self):
        self.ser.write("00000000000".encode("utf-8"))
        time.sleep(0.01)
        self.ser.write("44444444444".encode("utf-8"))
        time.sleep(0.01)
        self.ser.flush()
        GPIO.cleanup()

