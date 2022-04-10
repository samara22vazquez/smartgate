from config import *
from time import sleep

def debug():
    while True:
        file = open("debug.txt", "w")

        for key in config:
            file.write(str(key) + "\t\t\t- " + str(config[key]) + "\n")

        file.close()
        sleep(0.5)
