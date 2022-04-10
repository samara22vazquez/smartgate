import numpy as np
import cv2
import time 
import threading
import os 
from config import *

from picamera.array import PiRGBArray
from picamera import PiCamera
from distance import *

disable_proximity = False # For debugging camera. Proximity sensors will always return true if this is enabled.

disable_masking = True

#config
min_distance = 10 # Minimum distance in metres to acknowledge persons existance
resolution = (320 , 240 )
#resolution = (640, 480)
intruder_timeout = 30.0 # No of seconds to wait before taking another intruder image 

# Low pass filter to remove false-positives and give stable output 
def lp_filter(avg, sample, N=10):
    #return ((avg * (N-1)) + (sample * 10)) / N
    return sample

#front_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
#profile_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_profileface.xml')

front_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')
profile_cascade = cv2.CascadeClassifier('lbpcascade_profileface.xml')

#profile_cascade = cv2.CascadeClassifier('haarcascade_mcs_upperbody.xml')
# OpenCV threads

features = []

def _find_front_faces(gray):
    front_faces = front_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=1)
    for f in front_faces:
        features.append(f)

def _find_profile_faces(gray):
    profile_faces = profile_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=10)
    for f in profile_faces:
        features.append(f)

# Distance sensor threads

adult_near_left = False
adult_near_right = False
   
def proximity():
    global adult_near_left
    global adult_near_right

    while can_run('vision'):

        if disable_proximity:
            adult_near_left = True
            adult_near_right = True
        else:
            dist_left = distance(PROX_LEFT)
            dist_right = distance(PROX_RIGHT)
            adult_near_left = dist_left < min_distance
            adult_near_right = dist_right < min_distance
            print('Left: '+str(dist_left))
            print('Right: '+str(dist_right))
        
        time.sleep(0.5)

# Camera thread

fgbg = cv2.BackgroundSubtractorMOG(history = 10, nmixtures=5, backgroundRatio=0.1)

def vision(demo=True):

    global features
    global adult_near_left
    global adult_near_right
    
    adult_seen_left = 0
    adult_seen_right = 0

    adult_there_left = False
    adult_there_right = False

    last_intruder_time = 0.0 # Last time when image of intruder was saved. Used to ensure photo only taken every 30s.
    last_intruder_no = 1

    print("Started CV Thread")

    distance_thread = threading.Thread(target=proximity)
    distance_thread.start()

    camera = PiCamera(resolution=resolution, framerate=10)
    raw_frame = PiRGBArray(camera, size=resolution)

    while can_run('vision'):
      
        # Read in frame from camera and apply OpenCV face detection
        camera.capture(raw_frame, format="bgr", resize=resolution)
        frame = raw_frame.array
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        if not disable_masking:
            fgmask = fgbg.apply(frame)
            fgmask = cv2.blur(fgmask, (20,20))
            _, fgmask = cv2.threshold(fgmask, 40, 255, cv2.THRESH_BINARY)
            fgframe = cv2.bitwise_and(gray, fgmask)
            
            gray = fgframe
            #frame = fgframe
	
        features=[]
        t1 = threading.Thread(target=_find_front_faces, args=(gray,)) 
	t2 = threading.Thread(target=_find_profile_faces, args=(gray,))

	t1.start()
	t2.start()
        t1.join()
        t2.join()
 
        # Determine whether face detected on left or right side of screen
        # Then use low pass filter on face detection to remove false-positives
        if len(features) > 0:
            for (fx, fy, fw, fh) in features:
                if (fx + fh) < (resolution[0]/ 2):
                    adult_seen_right = lp_filter(adult_seen_left, 1)
                    #adult_seen_left = lp_filter(adult_seen_right, 0)
                else:
                    adult_seen_left = lp_filter(adult_seen_right, 1)
                    #adult_seen_right = lp_filter(adult_seen_left, 0)

        else:
            adult_seen_left = lp_filter(adult_seen_left, 0)
            adult_seen_right = lp_filter(adult_seen_right, 0)
    
        adult_there_left = (adult_seen_left > 0.2) and adult_near_left
        adult_there_right = (adult_seen_right > 0.2) and adult_near_right

        write_config('adult_there_left', adult_there_left)
        write_config('adult_there_right', adult_there_right)

        
        # If running as demo then display window with preview
        if (demo):
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            cv2.putText(frame, 'See Left:  ' + ('Yes' if adult_seen_left > 0.2 else 'No'), (10, 20), font, 0.5, 
                color=(0, 255, 0) if adult_there_left else (0, 0, 255), thickness = 1)

            cv2.putText(frame, 'See Right: ' + ('Yes' if adult_seen_right > 0.2 else 'No'), (10, 40), font, 0.5,
                color=(0, 255, 0) if adult_there_right else (0, 0, 255), thickness = 1)

            cv2.putText(frame, 'Near Left:  ' + ('Yes' if adult_near_left else 'No'), (200, 20), font, 0.5, 
                color=(0, 255, 0) if adult_near_left else (0, 0, 255), thickness = 1)

            cv2.putText(frame, 'Near Right: ' + ('Yes' if adult_near_right else 'No'), (200, 40), font, 0.5,
                color=(0, 255, 0) if adult_near_right else (0, 0, 255), thickness = 1)


            for (fx, fy, fw, fh) in features:
                cv2.rectangle(frame, (fx, fy), ((fx+fw), (fy+fh)), (255, 0, 0))

            cv2.imshow('Face Detection Demo', frame)
	    cv2.imshow('Mask', gray)
            cv2.waitKey(1)

        else:
            for (fx, fy, fw, fh) in features:
                cv2.rectangle(frame, (fx, fy), ((fx+fw), (fy+fh)), (255, 0, 0))

            if adult_there_left:
                print('Adult on left')
            if adult_there_right:
                print('Adult on right')

        raw_frame.truncate(0)
        
        # Save intruders face if it needs to

        current_time = time.time()
        
        if read_config('mode') == 'secure' and (adult_there_left or adult_there_right) and (current_time > last_intruder_time + intruder_timeout):
            print('Caught an intruder')
            last_intruder_time = current_time

            while os.path.exists('static/{}.jpg'.format(last_intruder_no)):
                last_intruder_no += 1
            cv2.imwrite('static/{}.jpg'.format(int(last_intruder_no)), frame)
        
        # Slow it down
        #time.sleep(0.1)

    # Clean up
    distance_thread.join()
    cv2.destroyAllWindows()

# Example Useage
if __name__ == '__main__':
    global disable_proximity
    disable_proximity = True
    write_config('mode', 'secure')
    t = threading.Thread(target=vision, name='Vision')
    t.start()
    set_to_start('vision')
    # Call p.end() to end face detection thread
    t.join()
