import sys
import time
import config
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
coilPins = [2, 3, 4, 17]

GPIO.setup(2,GPIO.OUT)  # Stepper coil 1
GPIO.setup(3,GPIO.OUT)  # Stepper coil 2
GPIO.setup(4,GPIO.OUT)  # Stepper coil 3
GPIO.setup(17,GPIO.OUT) # Stepper coil 4
GPIO.setup(13,GPIO.OUT) # Servo motor
GPIO.setup(27,GPIO.IN)  # Rail Switches
GPIO.setup(22,GPIO.IN)  # Roller Switch

stepMove = [[1, 1, 0, 0],   # Stepper motor rotation array
	    [0, 1, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1]]

currentStep = 0             # Chooses what sequence needs to start from from array stepMove
maxDis = 50                 # Maximum distance from then closed point
DemandPosition = 0          # Position the gate needs to go to
CurrentPosition = 0         # CurrentPosition of the gate; 0 = closed, -1 = open_left, 1 = open_right
sleepTime = 0.005           # Wavelength of rotation
enable = 1
angle = 0
rail = 0

def moveGate():
    global DemandPosition                             # Makes function use global variables
    global CurrentPosition
    global maxDis
    global currentStep
    global sleepTime
    global angle
    global rail
    wait = 0
    print("moving gate")
    direction = (DemandPosition - CurrentPosition)
    if direction == 2:                                # If the gate goes from open_right to open_left
        maxDis = 100                                  # Then double the distance and reset direction to unit magnitude
        direction = 1
    if direction == -2:                               # If the gate goes from open_left to open_right
        maxDis = 100                                  # Then double the distance and reset direction to unit magnitude
        direction = -1
    if (DemandPosition != CurrentPosition):           # If there is a difference in the two variables then move so they are the same
        for angle in range(0,(maxDis + 10)):                 # Only move the stepper motor a certain amount
            currentStep += direction                  # change the segment in the array to make it move in a certain direction
            if(currentStep == 4 and direction == 1):  # If in last element of array then reset
                    currentStep = 0
            if(currentStep == -1 and direction == -1):# If in zeroth element then reset to third element
                    currentStep = 3
            print "Angle %d, maxDis %d" % (angle, maxDis)
            for pinChoose in range(0, 4):             # Selects pin to output
                pin = coilPins[pinChoose]                     # Selects BCM output pin
                while(rail):                                  # If there is something in the way then stop moving gate
                    wait + 1
                    wait - 1
                if stepMove[currentStep][pinChoose]:          # If the pin sould be high in the segment of the array
                    GPIO.output(pin, True)                    # Then make it high
                else:                                         # Otherwise
                    GPIO.output(pin, False)           # Keep it low

            time.sleep(sleepTime)                     # Sets the frequency of rotation of the motor
            if GPIO.input(22) and CurrentPosition != 0 and abs(DemandPosition - CurrentPosition) != 2:               # When the angle is equal to the max angle
                print('Roller high!')
                CurrentPosition = DemandPosition    # Then set the current position to the demanded one
                maxDis = 50
                return
            if CurrentPosition == 0 and angle > (maxDis - 1):
                CurrentPosition = DemandPosition    # Then set the current position to the demanded one
                maxDis = 50
                return
            if abs(DemandPosition - CurrentPosition) == 2 and angle > (maxDis - 1):
                CurrentPosition = DemandPosition    # Then set the current position to the demanded one
                maxDis = 50
                return

def openGate():
    for i in range(0, 20):
        GPIO.output(13, True)
        time.sleep(0.001)
        GPIO.output(13, False)
        time.sleep(0.02)
    time.sleep(0.5)
    
def closeGate():
    time.sleep(0.5)
    for i in range(0, 20):
        GPIO.output(13, True)
        time.sleep(0.0013)
        GPIO.output(13, False)
        time.sleep(0.02)

def RailHandler(channel):
    global rail                 # Use global rail variable
    time.sleep(0.1)             # Wait 0.1 seconds for debouncing
    if GPIO.input(27):          # If input is high (object in the way)
        print "Rail high"
        rail = 1                # Set rail flag to stop gate moving
        config.write_config('status', 'obstruction') # Sets status to obstruction
    else:
        print "Rail low"
        #time.sleep(2)          # Wait two seconds for safety
        rail = 0                # Reset rail to 0

def convertRead(posName):
    global CurrentPosition
    if posName == 'open_right':
        return 1
    if posName == 'open_left':
        return -1
    if posName == 'closed':
        return 0
    else:
        return CurrentPosition  # If posName is none of above stay in same place 

def convertWrite(currentPos, demandPos):
    if currentPos == 0 and demandPos == 0:
        return 'closed'
    if currentPos == 1 and demandPos == 1:
        return 'open_right'
    if currentPos == -1 and demandPos == -1:
        return 'open_left'
    if currentPos == 0 and (currentPos != demandPos):
        return 'opening'
    if demandPos == 0 and (currentPos != demandPos):
        return 'closing'
    if (currentPos + demandPos) == 0:
        return 'opening'
    print 'currentPos is' + str(currentPos) + ' demandPos is' + str(demandPos)

GPIO.add_event_detect(27, GPIO.BOTH, callback=RailHandler) # Link interrupt handle thread to pin

def gate_control():
    global DemandPosition
    global maxDis
    for i in range(0, 4):
        pin = coilPins[i]
        GPIO.output(pin, False)
    while config.can_run('gate_control'):
        DemandPosition = convertRead(config.read_config('position'))
        config.write_config('status', convertWrite(CurrentPosition, DemandPosition))
        if DemandPosition != CurrentPosition:
            if CurrentPosition == 0:
                if DemandPosition == 1:
                    maxDis = int(config.read_config('open_angle_right')/1.8)
                if DemandPosition == -1:
                    maxDis = int(config.read_config('open_angle_left')/1.8)
                openGate()
            if CurrentPosition == 1:
                maxDis = int(config.read_config('open_angle_right')/1.8)
            if CurrentPosition == -1:
                maxDis = int(config.read_config('open_angle_left')/1.8)
            moveGate()
            if(CurrentPosition == 0):
                closeGate()
            for i in range(0, 4):
                pin = coilPins[i]
                GPIO.output(pin, False)















