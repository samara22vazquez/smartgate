#Imports
from time import sleep
from datetime import datetime
import time
import terminableThread
import threading
import config
import gateControl
import SmartHome
import app
import alarm
import vision
import debug_interface

#issues demand position to open the gate to the widest possible
def open_widest():
    if config.read_config('open_angle_left') > config.read_config('open_angle_right'):
        config.write_config('position', 'open_left')
    else:
        config.write_config('position', 'open_right')

#repeatedly open the gate in both directions - violently
def aggressive_bashing():
    if config.read_config('status') == 'closed' and config.read_config('position') == 'closed':
        config.write_config('position', 'open_left')
    elif config.read_config('status') == 'open_left':
        config.write_config('position', 'open_right')
    elif config.read_config('status') == 'open_right':
        config.write_config('position', 'open_left')

#get the mode based on a time set override
def get_timed_mode():
    now = time.localtime(time.time())
    #determine mode
    for preset in config.config['preset_mode']:
        if now > preset.start_time and now < preset.end_time:
            return preset.mode
    return 'active'

#wake threads that are set to sleep to resume
def wake_threads():
    print "Waking threads"
    global fd, gc, at
    if not fd.isAlive():
        fd = terminableThread.TerminableThread(name = 'vision', target = vision_placeholder) #don't ask
        fd.start()
    if not gc.isAlive():
        gc = terminableThread.TerminableThread(name = 'gate_control', target = gateControl.gate_control)
        gc.start()
    if not at.isAlive():
        at = terminableThread.TerminableThread(name = 'alarm', target = alarm.alarm)
        at.start()
    print "Threads awoken"

#deactivate threads that are not critical in sleep
def sleep_threads():
    print "Setting threads to sleep"
    if fd.isAlive():
        fd.end()
    if gc.isAlive():
        gc.end()
    print "Sleeping alarm"
    if at.isAlive():
        at.end()
    print "Threads set to sleep"


#Placeholder thread entry points
def web_app_placeholder():
    sleep(0.1)
    for i in range (0, 10):
        print "Pass " + str(i) + " in web app"
        sleep(1)

def gate_control_placeholder():
    sleep(0.2)
    i = 0
    while config.can_run('gate_control'):
        print "Pass " + str(i) + " in gate control"
        i += 1
        sleep(1)

def vision_placeholder():
    sleep(0.3)
    i = 0
    while config.can_run('vision'):
        #print "Pass " + str(i) + " in vision"
        i += 1
        sleep(1)

def smarthome_placeholder():
    sleep(0.4)
    for i in range(0, 10):
        #print "Pass " + str(i) + " in smarthome integration"
        sleep(1)

def alarm_placeholder():
    sleep(0.5)
    i = 0
    while config.can_run('alarm'):
        #print "Pass " + str(i) + " in alarm"
        i += 1
        sleep(1)


#Thread initialisation
wa = threading.Thread(name = 'webapp', target = app.webapp)
gc = terminableThread.TerminableThread(name = 'gate_control', target = gateControl.gate_control)
si = threading.Thread(name = 'smarthome', target = smarthome_placeholder)
fd = terminableThread.TerminableThread(name = 'vision', target = vision_placeholder)
at = terminableThread.TerminableThread(name = 'alarm', target = alarm.alarm)
db = threading.Thread(name = 'debug', target = debug_interface.debug)


#start threads
wa.start()
gc.start()
si.start()
fd.start()
at.start()
db.start()


#Control loop frequency in Hz
loop_frequency = 4
pass_number = 0
open_time_count = 0
closed_timeout = 0


#Main control loop
while True:
    
    #Check fire
    if config.read_config('on_fire'):
        open_widest()

    
    #Preset time of day
    elif get_timed_mode() == 'off':
        open_widest()
        #print 'The gate is preset to be open'
    elif get_timed_mode() == 'aggressive':
        aggressive_bashing()
        #print 'Grrrrrr! I\'m preset to be angry!'
    elif get_timed_mode() == 'secure':
        #print 'You shall not pass! (preset)'
        
            
    #Configured off     
    elif config.read_config('mode') == 'off':
        open_widest()
        #print 'opening gate according to webapp command'

            
    #Active mode control
    elif config.read_config('mode') == 'active':

        if config.read_config('status') == 'closed':
            if closed_timeout == 0:
                if config.read_config('adult_there_left') and not config.read_config('adult_there_right'):
                    if config.read_config('open_angle_right') > 0:
                        config.write_config('position', 'open_right')
                    else:
                        config.write_config('position','open_left')
                        
                elif config.read_config('adult_there_right') and not config.read_config('adult_there_left'):
                    if config.read_config('open_angle_left') > 0:
                        config.write_config('position','open_left')
                    else:
                        config.write_config('position','open_right')
            else:
                close_timeout -= 1

        elif config.read_config('status') == 'open_left' or config.read_config('status') == 'open_right':
            if open_time_count < config.read_config('stay_open_time'):
                open_time_count += 1.0/loop_frequency
            elif open_time_count == config.read_config('stay_open_time'):
                if not config.read_config('adult_there_left') and not config.read_config('adult_there_right'):
                    config.write_config('position','closed')
                    closed_time_out = loop_frequency*5
            else:
                openTimeCount = 0
    elif config.read_config('mode') == 'secure':
        #print 'securing gate according to webapp command'
        
    elif config.read_config('mode') == 'aggressive':
        aggressive_bashing()
        #print 'going nuclear according to webapp command'


    #sleep according to the loop frequency
    sleep(1.0/loop_frequency)


    #for test purposes
    #print "Pass " + str(pass_number) + " in main control"
    pass_number += 1
    #if pass_number == 5:
    #   sleep_threads()
    #if pass_number == 8:
    #   wake_threads()
    #if pass_number == 30:
    #    config.write_config('adult_there_left', True)
    #if pass_number == 35:
    #    config.write_config('adult_there_left', False)
    
