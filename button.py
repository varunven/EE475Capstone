import RPi.GPIO as GPIO
import threading
import time

# The button class represent's a physical button on the SEE glasses. It abstracts away GPIO
# setup, and is instantiated with a the GPIO Pin number and  on_press function, which is a callback\
# that is executed once the button is pressed.
class Button:
	def __init__(self, gpio_pin, on_press):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(gpio_pin, GPIO.FALLING, callback=on_press, bouncetime=3000)
		threading.Thread(target=self.read_btn).start()
	
	# Constantly read btn
	def read_btn(self):
		try:
			while True:
				time.sleep(0.1)
		finally:
			GPIO.cleanup()
	                                                                                 
