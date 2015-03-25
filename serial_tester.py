"""
*2014.04.28 17:07:05
based off of:
/c/clients/pylablib_performance_tests/read_serial-2.py


*2012.06.11 16:44:48
more complete version of read_serial

keeping this separate from the script that is running the stimulus generation

that way it only needs to do one thing... monitor the serial report from the arduino

"""
import re

from time import sleep
from datetime import datetime

import serial

#ser = serial.Serial('/dev/tty.usbmodem411', 115200, timeout=1)
#ser = serial.Serial('/dev/tty.usbmodem411', 9600, timeout=1)
#ser = serial.Serial('/dev/tty.usbmodem621', 115200, timeout=1)
ser = serial.Serial('/dev/tty.usbmodem621', 9600, timeout=1)


last = datetime.now()
last_micros = 0
started = False
ready = False

while True:
    line = ser.readline()
    #print dir(ser)

    if not ready and line == "lablibduino.0.2\r\n":
        print "MATCH!!!"
        ready = True
    elif not ready:
        print "->%s<- != ->%s<-" % (line, "lablibduino.0.2\r\n")

    if line and line != "Waiting for start trigger\r\n":
        print line

    if line and re.search("initialized:", line):
        parts = line.split(" ")
        print parts
        (junk, init_time, junk, arm_time, junk, start_time, junk, stop_time) = parts
        diff1 = int(arm_time) - int(init_time)
        diff2 = int(start_time) - int(arm_time)
        diff3 = int(stop_time) - int(start_time)
        print diff1
        print diff2
        print diff3
        
        started = False
    if line == "All done!\r\n":
        #no longer running
        started = False
        
    now = datetime.now()
    diff = now - last

    #print diff.seconds
    #print dir(diff)
    if diff.total_seconds() >= 1 and ready:
        #see if we need to re-set the triggers and start things running:
        
        #print "sending lines"
        #ser.writelines(["from computer"])
        #ser.writelines(["reaaaaaaallllllyyyyy longggggg line\r", "short line\r"])
        print line
        print "time diff: ", diff.total_seconds()
        
        if not started:
            #where analog port is plugged in:
            # ser.writelines(["ARM A 5 512\r"])
            # A 0 = photodiode
            # A 1 = VGA detector
            print "setting up start"
            ser.writelines(["START A 4 4\r"])
            #currently have buttons plugged in on 2 and 4
            #ser.writelines(["STOP D 2 6\r"])
            print "setting up stop"
            ser.writelines(["STOP A 5 6\r"])

            #skipping an arm command... just run it
            print "requesting run"
            ser.writelines(["RUN\r"])
            started = True

        last = now
