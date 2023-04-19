#Libraries
import RPi.GPIO as GPIO
import time

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins for left sensor
GPIO_TRIGGER_L = 18
GPIO_ECHO_L = 24

#set GPIO Pins for right sensor
GPIO_TRIGGER_R = 23
GPIO_ECHO_R = 15

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_L, GPIO.OUT)
GPIO.setup(GPIO_ECHO_L, GPIO.IN)

GPIO.setup(GPIO_TRIGGER_R, GPIO.OUT)
GPIO.setup(GPIO_ECHO_R, GPIO.IN)

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

if __name__ == '__main__':
	GPIO.output(GPIO_TRIGGER_L, False)
	GPIO.output(GPIO_TRIGGER_R, False)
	time.sleep(2)
	try:
		print("running")
		while True:
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

	# Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Measurement stopped by User")
		GPIO.cleanup()
