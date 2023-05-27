import RPi.GPIO as GPIO
import threading
import time

class Button:
	def __init__(self, gpio_pin, on_press):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(gpio_pin, GPIO.FALLING, callback=on_press, bouncetime=3000)
		
		
		#self.on_press = on_press
		threading.Thread(target=self.read_btn).start()
		
	def read_btn(self):
		try:
			while True:
				time.sleep(0.1)
		finally:
			GPIO.cleanup()
	                                                                                 
