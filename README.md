Arduino Timer
===================

Arduino Timer is a simple, accurate and flexible timing system using an inexpensive arduino microcontroller. The arduino is open hardware with open source software that supports it. It is also a stand alone system that only does one thing. This means it will not be interrupted or disturbed by any processes running on other systems. This is a common problem when trying to make time measurements using the same system that is generating events to be timed. 

This timer accepts configuration commands via a serial interface. Most programming languages and environments offer serial connection libraries. This enables you to use the timer and collect the results with any system with a serial interface library. 

The commands sent over the serial connection are minimalistic and look like:

````
  START A 0 5
  STOP A 1 5
````

'START' and 'STOP' are the main configuration commands, and each of these takes three parameters:

 1. 'A' or 'D' 
    (specify if the input pin is analog or digital)
 2. 0 - 12
    (the pin number)
 3. 0 - 1024
    (the threshold value to look for)

Once all of the configuration commands have been set, the timer is started with the 'RUN' command:

````
  RUN
````

Once all of the configured events have triggered, the result is printed back to the serial connection for logging. 

We use a stereo audio file as an example source for events. It is easy to play back a stereo audio file, and it is easy to measure the onset of the events within audio editing software. This enables a way to test the system and verify the results. It also makes for a nice introduction to distilling events down to a simple voltage level. 

The primary limitation of this system is that only one timer can be active and scheduled at a time. However, this limitation is also what ensures accurate timing and keeps the interface simple. 

Resources used (copies included):

  - [ArduinoSerialCommand](https://github.com/scogswell/ArduinoSerialCommand)
  - [TimerOne](https://github.com/PaulStoffregen/TimerOne)
  - [Audiogen](https://github.com/casebeer/audiogen)  

More documentation coming soon...

See: [http://srl-iu.github.io/arduino-timer/](http://srl-iu.github.io/arduino-timer/) for more details.
