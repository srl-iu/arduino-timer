#!/usr/bin/env python
"""
#
# Description:

Generate a stereo wave file using python

set the arduino timer to listen for the wave

Use PyAudio to play the generated sound:
http://people.csail.mit.edu/hubert/pyaudio/

collect the results for comparison


# By: Charles Brandt [ccbrandt at indiana dot edu]
# On: *2015.01.05 12:30:48 
# License:  GPLv3

# Requires:
pyaudio

"""
import sys, os, re, random

import pyaudio
import wave

import audiogen
import itertools

from time import sleep
from datetime import datetime

import serial

#ser = serial.Serial('/dev/tty.usbmodem411', 115200, timeout=1)
#ser = serial.Serial('/dev/tty.usbmodem411', 9600, timeout=1)
#ser = serial.Serial('/dev/tty.usbmodem621', 115200, timeout=1)
#ser = serial.Serial('/dev/tty.usbmodem621', 9600, timeout=1)
ser = serial.Serial('/dev/tty.usbserial-12KP0390', 9600, timeout=1)

CHUNK = 1024

ready = False

#make sure the timer has been intialized and is ready to go..
while not ready:
    line = ser.readline()

    if not ready and line == "lablibduino.0.2\r\n":
        print "Connection to Arduino Timer established."
        ready = True
    elif not ready:
        #print "->%s<- != ->%s<-" % (line, "lablibduino.0.2\r\n")
        pass


def silence_tone(silence):
    """
    parameter is the length of time in seconds
    """

    return itertools.chain( audiogen.silence(silence), audiogen.tone(440), )

def make_wave(destination, silence, total_length):
    
##     # mix 440 Hz and 445 Hz tones to get 5 Hz beating
##     beats = audiogen.util.mixer(
##         (audiogen.tone(440), audiogen.tone(445)),
##         [(audiogen.util.constant(1), audiogen.util.constant(1)),]
##         )

    output = audiogen.util.mixer(
        # first parameter is all of the source generators
        ( silence_tone(0), silence_tone(silence), ),
        #next is a list of parameters for each channel
        #to specify levels for each of the previous source generators:
        (
            (audiogen.util.constant(1), audiogen.util.constant(0)),
            (audiogen.util.constant(0), audiogen.util.constant(1)),
            )
        )

    with open(destination, "wb") as f:
        #crop will set the maximum length of the file (so not infinite)
        audiogen.sampler.write_wav(f, audiogen.util.crop(output, total_length))


def play(wavefile):
    wf = wave.open(wavefile, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()

def setup_timer(debug=False):

    running = False

    #where analog port is plugged in:
    # ser.writelines(["ARM A 5 512\r"])
    if debug:
        print "setting up start"
    #these thresholds are a bit low
    #ser.writelines(["START A 4 4\r"])
    ser.writelines(["START A 4 20\r"])

    #currently, silence is inserted to Right audio channel
    #make sure right channel is plugged into A5 on arduino
    if debug:
        print "setting up stop"
    #setting a lower threshold may result in stop triggering early from noise
    #this is more common when timing longer periods.
    #ser.writelines(["STOP A 5 6\r"])
    ser.writelines(["STOP A 5 20\r"])

    #skipping an arm command... just run it
    if debug:
        print "requesting run"
    ser.writelines(["RUN\r"])

    while not running:
        line = ser.readline()

        if line and re.search("Running", line):
            running = True
        elif line and line != "Waiting for start trigger\r\n":
            if debug:
                print line

def get_results(debug=False):
    found_results = False
    diff1 = ''
    diff2 = ''
    diff3 = ''

    while not found_results:
        line = ser.readline()
        if debug:
            print "looking for results in: %s" % line
        
        if line and re.search("initialized:", line):
            parts = line.split(" ")
            if debug:
                print parts
            (junk, init_time, junk, arm_time, junk, start_time, junk, stop_time) = parts
            diff1 = int(arm_time) - int(init_time)
            diff2 = int(start_time) - int(arm_time)
            diff3 = int(stop_time) - int(start_time)
            if debug: 
                print diff1
                print diff2
                print diff3

            started = False
            found_results = True

        sleep(.2)

    if line == "All done!\r\n":
        if debug:
            print line
        #no longer running
        started = False
    
    return (diff1, diff2, diff3)

def one_trial(count, millis, total_length):

    now = datetime.now()

    destination = "output/%03d-%s-output.wav" % (count, millis)

    seconds = (millis*1.0) / 1000

    #having an issue with audiogen library
    #where length of silence is cut by half...
    #fixing by doubling here:
    adjusted_seconds = seconds * 2.0

    print ""
    print "making a wave with %s seconds of silence" % seconds
    make_wave(destination, adjusted_seconds, total_length)

    results = []

    for i in range(3):
        print "try: %s" % i
        
        setup_timer()

        play(destination)

        sub_results = get_results()

        results.extend(sub_results)
    
    print results

    return (results, destination)

def run_many():
    base = 'output'
    if not os.path.exists(base):
        os.makedirs(base)
    
    now = datetime.now()
    log_name = 'timer_test-' + now.strftime('%Y%m%d') + '.csv'
    log_file = os.path.join(base, log_name)
    log = file(log_file, 'w+')

    #title for log
    title = [ 'number', 'length', 'measured1', 'measured2', 'measured3', 'destination', 'date' ]
    log.write(','.join( title ) + '\n')
    log.close()

    count = 1

    tested = [0, ]
    option = 0
    
    for i in range(1000):

        while option in tested:
            #range in milliseconds
            option = random.randrange(1, 20000)

        print
        print "starting trial: %04d" % i
        total_length = (option / 1000.0) + 1
        #(results, destination) = one_trial(1, 823, 2)
        (results, destination) = one_trial(count, option, total_length)
        #(init_to_arm, arm_to_start, start_to_stop) = results
        (init_to_arm1, arm_to_start1, start_to_stop1, init_to_arm2, arm_to_start2, start_to_stop2, init_to_arm3, arm_to_start3, start_to_stop3) = results
        #row = [str(count), str(option), str(start_to_stop), str(destination)]
        row = [ str(count), str(option), str(start_to_stop1), str(start_to_stop2), str(start_to_stop3), str(destination), str(datetime.now()) ]
        log = file(log_file, 'a+')
        log.write(','.join( row ) + '\n')
        log.close()
        tested.append(option)
        count += 1

    #log.close()

    print tested
    
run_many()
    
## print audiogen.sampler.wave_module_patched()
## source = wave.open(destination, 'r')
## print source.getsampwidth()
