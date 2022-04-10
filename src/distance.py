#https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/

import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
 
PROX_TRIG = (12, 20)
PROX_ECHO = (16, 21)

PROX_LEFT = 0
PROX_RIGHT = 1

GPIO.setup(PROX_TRIG[0], GPIO.OUT)
GPIO.setup(PROX_ECHO[0], GPIO.IN)
GPIO.setup(PROX_TRIG[1], GPIO.OUT)
GPIO.setup(PROX_ECHO[1], GPIO.IN)

def distance(no):
    # set Trigger to HIGH
    GPIO.output(PROX_TRIG[no], True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(PROX_TRIG[no], False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(PROX_ECHO[no]) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(PROX_ECHO[no]) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist_left = distance(PROX_LEFT)
            dist_left = distance(PROX_LEFT)

            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
