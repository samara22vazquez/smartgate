import RPi.GPIO as GPIO
import time 
from config import *
from threading import Thread

#Module import initialisation
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(25,GPIO.OUT,initial=0)   #set pin as output, RED LED
GPIO.setup(23,GPIO.OUT,initial=0)   #set pin as output, YELLOW LED
GPIO.setup(24,GPIO.OUT,initial=0)   #set pin as output, GREEN LED
GPIO.setup(18,GPIO.OUT,initial=0)   #set pin as output, ALARM
pwm1=GPIO.PWM(18,900)               #enable pwm on alarm pin

#Entry point
def alarm():
    global pwm1
    
    while can_run('alarm'):
        pwm1.stop()    
        
        while can_run('alarm') and (read_config('status')=='opening' or read_config('status')=='closing'):
            GPIO.output(23,GPIO.LOW) #yellow LED off
            #flashing green LED
            GPIO.output(24,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(24,GPIO.LOW)
            time.sleep(0.5)

            if read_config('on_fire')==True:
                GPIO.output(25,GPIO.HIGH) #red LED on
                #while loop for intermittent tone
                while can_run('alarm') and (read_config('on_fire')==True and (read_config('status')=='opening' or read_config('status')=='closing')):
                    pwm1=GPIO.PWM(18,900)
                    pwm1.start(70)
                    time.sleep(0.5)
                    pwm1.stop()
                    time.sleep(0.5)
            else:
                GPIO.output(25,GPIO.LOW) #red LED off

            if read_config('adult_there_left')==True and read_config('adult_there_right')==True:
                
                #lower tone alarm
                pwm1=GPIO.PWM(18,200)
                pwm1.start(70)
                #flashing yellow LED
                GPIO.output(23,GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(23,GPIO.LOW)
                time.sleep(0.5)

            

        while can_run('alarm') and (read_config('status')=='open_left'or read_config('status')=='open_right'):
            GPIO.output(23,GPIO.LOW)
            GPIO.output(24,GPIO.HIGH)
            #print 'open'

            if read_config('on_fire')==True:
                GPIO.output(25,GPIO.HIGH)
                while can_run('alarm') and (read_config('on_fire')==True and (read_config('status')=='open_left'or read_config('status')=='open_right')):
                    pwm1=GPIO.PWM(18,900)
                    pwm1.start(70)
                    time.sleep(0.2)
                    pwm1.stop()
                    time.sleep(0.2)

            else:
                GPIO.output(25,GPIO.LOW)

            if read_config('adult_there_left')==True and read_config('adult_there_right')==True:
                GPIO.output(23,GPIO.HIGH)
                pwm1=GPIO.PWM(18,200)
                pwm1.start(70)
                time.sleep(0.5)
                GPIO.output(23,GPIO.LOW)
                time.sleep(0.5)       

        while can_run('alarm') and (read_config('status')=='closed'):
            GPIO.output(23,GPIO.LOW)
            GPIO.output(24,GPIO.LOW)

            if read_config('on_fire')==True:
                GPIO.output(25,GPIO.HIGH)
                while can_run('alarm') and (read_config('on_fire')==True and read_config('status')=='closed'):
                    pwm1=GPIO.PWM(18,900)
                    pwm1.start(70)
                    time.sleep(0.2)
                    pwm1.stop()
                    time.sleep(0.2)            

            else:
                GPIO.output(25,GPIO.LOW)

            if read_config('adult_there_left')==True and read_config('adult_there_right')==True:
                GPIO.output(23,GPIO.HIGH)
                pwm1=GPIO.PWM(18,200)
                pwm1.start(70)
                time.sleep(0.5)
                GPIO.output(23,GPIO.LOW)
                time.sleep(0.5)

        while can_run('alarm') and (read_config('status')=='obstruction'):

            pwm1=GPIO.PWM(18,900)

            GPIO.output(23,GPIO.HIGH)
            GPIO.output(24,GPIO.LOW)
            while can_run('alarm') and (read_config('on_fire')==False and read_config('status')=='obstruction'):
                pwm1.start(70)
                
            if read_config('on_fire')==True:
                GPIO.output(25,GPIO.HIGH)
                while can_run('alarm') and (read_config('on_fire')==True and read_config('status')=='obstruction'):
                    pwm1.start(70)
                    time.sleep(0.2)
                    pwm1.stop()
                    time.sleep(0.2)   

            else:
                GPIO.output(25,GPIO.LOW)
        pwm1.stop()
        #GPIO.output(23,GPIO.LOW)
 

