import serial
import threading, time
import RPi.GPIO as GPIO

ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
ser.flush()

# GPIO global vars
GPIO.setmode(GPIO.BCM)
#set GPIO Pins for left sensor, right sensor
GPIO_TRIGGER_L = 18
GPIO_ECHO_L = 24
GPIO_TRIGGER_R = 23
GPIO_ECHO_R = 15
GPIO.setup(GPIO_TRIGGER_L, GPIO.OUT)
GPIO.setup(GPIO_ECHO_L, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_R, GPIO.OUT)
GPIO.setup(GPIO_ECHO_R, GPIO.IN)

# Object Detection
def object_detect_startup():
	#reset GPIO output pins
	GPIO.output(GPIO_TRIGGER_L, False)
	GPIO.output(GPIO_TRIGGER_R, False)
	time.sleep(2)

# calculate distance for sensor given as parameter
def distance(side):
	if (side == 0):
		# set Trigger to HIGH
		GPIO.output(GPIO_TRIGGER_L, True)

		# set Trigger after 0.01ms to LOW
		time.sleep(0.00001)
		GPIO.output(GPIO_TRIGGER_L, False)

		StartTime = time.time()
		StopTime = time.time()

		# save StartTime
		while GPIO.input(GPIO_ECHO_L) == 0:
			StartTime = time.time()

		# save time of arrival
		while GPIO.input(GPIO_ECHO_L) == 1:
			StopTime = time.time()

		# time difference between start and arrival
		TimeElapsed = StopTime - StartTime
		# multiply with the sonic speed (34300 cm/s)
		# and divide by 2, because there and back
		distance = (TimeElapsed * 34300) / 2
	else:
		# set Trigger to HIGH
		GPIO.output(GPIO_TRIGGER_R, True)

		# set Trigger after 0.01ms to LOW
		time.sleep(0.00001)
		GPIO.output(GPIO_TRIGGER_R, False)

		StartTime = time.time()
		StopTime = time.time()

		# save StartTime
		while GPIO.input(GPIO_ECHO_R) == 0:
			StartTime = time.time()

		# save time of arrival
		while GPIO.input(GPIO_ECHO_R) == 1:
			StopTime = time.time()

		# time difference between start and arrival
		TimeElapsed = StopTime - StartTime
		# multiply with the sonic speed (34300 cm/s)
		# and divide by 2, because there and back
		distance = (TimeElapsed * 34300) / 2
	return distance
	
# Send inputs to microcontroller based on distance
def program_sensor(left, right):
	if(abs(left-right) < 50):
		data = "11111111111" # Replace this with your sensor data
		print("program sending " + str(left))
		ser.write(data.encode('utf-8'))
		time.sleep(0.01)

		data = "11111111111" # Replace this with your sensor data
		print("program sending " + str(left) + " number 2")
		ser.write(data.encode('utf-8'))
		time.sleep(3)
	if(abs(left-right) < 150):
		data = "22222222222" # Replace this with your sensor data
		print("program sending " + str(left))
		ser.write(data.encode('utf-8'))
		time.sleep(0.01)

		data = "22222222222" # Replace this with your sensor data
		print("program sending " + str(left) + " number 2")
		ser.write(data.encode('utf-8'))
		time.sleep(3)
	if(abs(left-right) < 300):
		data = "33333333333" # Replace this with your sensor data
		print("program sending " + str(left))
		ser.write(data.encode('utf-8'))
		time.sleep(0.01)

		data = "33333333333" # Replace this with your sensor data
		print("program sending " + str(left) + " number 2")
		ser.write(data.encode('utf-8'))
		time.sleep(3)
	else:
		data = "00000000000" # Replace this with your sensor data
		print("program sending " + str(left))
		ser.write(data.encode('utf-8'))
		time.sleep(0.01)

		data = "00000000000" # Replace this with your sensor data
		print("program sending " + str(left) + " number 2")
		ser.write(data.encode('utf-8'))
		time.sleep(3)

# method to be used in thread to detect objects
def detect_objects():
	try:
		dist_L = distance(0)
		print ("Measured Distance left  = %.1f cm" % dist_L)
		time.sleep(0.45)
		dist_R = distance(1)
		print ("Measured Distance right = %.1f cm" % dist_R)
		time.sleep(0.45)

		if dist_R-dist_L > 20:
			print("Object is to the left")
		elif dist_L-dist_R > 20:
			print("Object is to the right")
		else:
			print("Object is in the center")
		program_sensor(dist_L, dist_R)
		time.sleep(0.5)
		t = threading.Thread(target=detect_objects)
		t.start()

	# Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Measurement stopped by User")
		GPIO.cleanup()
