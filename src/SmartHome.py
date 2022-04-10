import config
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(7,GPIO.IN)

def smarthome():
    while True:
        a=open('message.txt')
       
        if (GPIO.input(7)==False) or ('fire' in a.read()):
            config.write_config('on_fire',True)
            #print(config.read_config('on_fire'))
        else:
            config.write_config('on_fire',False)
            #print(config.read_config('on_fire'))
        a.close()
        sleep(0.5)
