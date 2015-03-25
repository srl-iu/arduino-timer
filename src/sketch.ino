/*
*2015.02.16 15:49:56 
to find accurate thresholds, (or to see what values your arduino is reading)
enable the DEBUG mode of this sketch while connected via a serial monitor
this will print the analogRead values from the specified pin

(be sure configure the analog pin configuration
to be the same one you have your audio output plugged in to)

Can use arduino serial monitor, or can use a python equivalent, to see output:
serial_tester.py

Note that Arm, Start and Stop should all be set to different pins
the results could be unpredictable if two triggers are set to the same pin
(both may trigger simultaneously... no automated reset / debouncing involved)

*/

// We need this even if we're not using a SoftwareSerial object
// Due to the way the Arduino IDE compiles
#include <SoftwareSerial.h> 
// http://awtfy.com/2011/05/23/a-minimal-arduino-library-for-processing-serial-commands/
#include <SerialCommand.h>

// http://playground.arduino.cc/Code/Timer1
// https://github.com/PaulStoffregen/TimerOne
#include <TimerOne.h>

// how often to call update_ticks in microseconds:
int timer_frequency = 256;

SerialCommand SCmd; // The demo SerialCommand object

#define LED_PIN_1		13 // LED connected to digital pin 13

int initialized = 0;
int armed = 0;
int started = 0;
int stopped = 0;

unsigned long init_time = 0;
unsigned long arm_time = 0;
unsigned long start_time = 0;
unsigned long stop_time = 0;

unsigned long init_micros = 0;
unsigned long arm_micros = 0;
unsigned long start_micros = 0;
unsigned long stop_micros = 0;

// if the pins are Analog or Digital
char* arm_type = "A";
char* start_type = "A";
char* stop_type = "D";

int arm_pin = -1;
int start_pin = -1;
int stop_pin = -1; // assumed to be a digital input with button???

int arm_threshold = 0;
int start_threshold = 0;
int stop_threshold = 0;

int cur_value = 0;

int debug = 0;
char* debug_type = "A";
int debug_pin = -1;
String debug_string;
int debug_cur = 0;
int debug_last = 0;

float adjustment;
// first run python generate_play_collect.py with clock_adjust set to 0:
float clock_adjust = 0;
// then, once measurments have been collected, find the frequency mismatch:
// python compare_times.py output/timer_test-20150216.csv
// and change it here:
//float clock_adjust = 0.00177294096517;
//float clock_adjust = -0.000538398670211;
// don't forget to reflash your arduino after changing that!


volatile unsigned long ticks = 0; // use volatile for shared variables

void update_ticks(void)
{
  ticks = ticks + 1;  // count the number of interrupts

  /*
  // if number of ticks excedes long range, can tally every x number of ticks
  if (ledState == LOW) {
    ledState = HIGH;
  } else {
    ledState = LOW;
  }
  */

}

void setup()
{
  Timer1.initialize(timer_frequency);
  Timer1.attachInterrupt(update_ticks); 

  pinMode(LED_PIN_1,OUTPUT); // Configure the onboard LED for output
  digitalWrite(LED_PIN_1,LOW); // default to LED off
  Serial.begin(9600);
  
  // Setup callbacks for SerialCommand commands
  SCmd.addCommand("ON",LED_on); // Turns LED on
  SCmd.addCommand("OFF",LED_off); // Turns LED off

  //SCmd.addCommand("P",process_command); // Converts two arguments to integers and echos them back

  //configure the trigger and thresholds for arming the timer
  SCmd.addCommand("ARM",process_arm); 

  //configure the trigger and thresholds for starting the timer
  SCmd.addCommand("START",process_start); 

  //configure the trigger and thresholds for stopping the timer
  SCmd.addCommand("STOP",process_stop); 

  //Initialize... set everthing in motion
  SCmd.addCommand("RUN",run); 

  SCmd.addCommand("DEBUG",debug_start); 
  SCmd.addCommand("DEBUG_STOP",debug_stop); 

  // Handler for command that isn't matched (says "What?")
  SCmd.addDefaultHandler(unrecognized); 

  Serial.println("lablibduino.0.2"); // keep track of what is loaded
  Serial.println("Ready");
}

void LED_on()
{
  Serial.println("LED on");
  digitalWrite(LED_PIN_1,HIGH);
}

void LED_off()
{
  Serial.println("LED off");
  digitalWrite(LED_PIN_1,LOW);
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized()
{
  Serial.println("What?");
}

void handle_type(char* arg) 
{
  //better to just pass the parameter in with character arrays
  //otherwise, if trying to return values
  //they may be deallocated after the function call
  //resulting in empty variables in calling function
  //http://forum.arduino.cc/index.php?topic=44303.0
  
  //make room for one character:
  //char *arg = malloc(sizeof(char));
  arg = SCmd.next();
  if (arg == NULL) {
    Serial.println("No Type specified");
  }
  //else {
  //  Serial.println(arg);
  //}    
  //return arg;
}

int handle_pin() 
{
  int aNumber;
  char *arg;
  aNumber = NULL;
  arg = SCmd.next();
  if (arg != NULL)
    {
      //TODO:
      // rather than atoi, it may be better to specify 
      //if it's an analog or digital input (A / D)
      //followed by the corresponding pin number
      aNumber = atoi(arg); // Converts a char string to an integer
      //Serial.print("First argument was: ");
      //Serial.println(aNumber);
    }
  else {
    Serial.println("No Pin #");
  }
  return aNumber;
}

int handle_threshold() 
{
  int aNumber;
  char *arg;
  aNumber = NULL;
  arg = SCmd.next();
  if (arg != NULL)
    {
      //aNumber = atoi(arg); // Converts a char string to an integer
      aNumber = atol(arg);
    }
  else {
    Serial.println("No Threshold");
  }
  return aNumber;
}

void process_arm()
{
  //Serial.println("We're in process_arm");

  Serial.print("ARM TYPE: ");
  //arm_type = handle_type();
  handle_type(arm_type);
  Serial.println(arm_type);

  Serial.print("ARM PIN: ");
  arm_pin = handle_pin();
  Serial.println(arm_pin);

  Serial.print("ARM THRESHOLD: ");
  arm_threshold = handle_threshold();
  Serial.println(arm_threshold);
}

void process_start()
{
  //Serial.println("We're in process_start");

  Serial.print("START TYPE: ");
  //start_type = handle_type();
  handle_type(start_type);
  Serial.println(start_type);

  Serial.print("START PIN: ");
  start_pin = handle_pin();
  Serial.println(start_pin);

  Serial.print("START THRESHOLD: ");
  start_threshold = handle_threshold();
  Serial.println(start_threshold);
}

void process_stop()
{
  //Serial.println("We're in process_stop");

  Serial.print("STOP TYPE: ");
  //stop_type = handle_type();
  handle_type(stop_type);
  Serial.println(stop_type);

  Serial.print("STOP PIN: ");
  stop_pin = handle_pin();
  Serial.println(stop_pin);

  Serial.print("STOP THRESHOLD: ");
  stop_threshold = handle_threshold();
  Serial.println(stop_threshold);

}

void run()
{
  //same approach as in main loop()
  unsigned long tickCopy;  
  noInterrupts();
  //go ahead and reset this here... 
  //not a requirement to track when the controller was powered on
  ticks = 0;
  tickCopy = ticks;
  interrupts();

  //make sure debug is disabled now
  debug = 0;

  //init_time = millis();
  init_time = tickCopy;
  if (arm_pin == -1) {
    arm_time = init_time;
    armed = 1;
  }

  start_time = 0;
  stop_time = 0;
  
  Serial.print("time_i_post: ");
  //Serial.println(micros());
  //Serial.println(time_i);
  Serial.println(init_time);

  initialized = 1;

  Serial.println("Running...");

}

void debug_start()
{

  //debug_type = handle_type();
  handle_type(debug_type);
  //Serial.println(debug_type);
  
  debug_pin = handle_pin();

  debug_cur = 0;
  debug_last = 0;

  debug = 1;
  Serial.println("DEBUG MODE STARTED");

}

void debug_stop()
{
  debug = 0;
  Serial.println("DEBUG MODE STOPPED");

}

void loop()
{
  //remember that analogRead takes ~100 microseconds
  //http://arduino.cc/en/Reference/analogRead

  //make sure that loop / interrupts doesn't go faster than ~200 microseconds

  unsigned long tickCopy;  // holds a copy of ticks value

  // to read a variable which the interrupt code writes, we
  // must temporarily disable interrupts, to be sure it will
  // not change while we are reading.  To minimize the time
  // with interrupts off, just quickly make a copy, and then
  // use the copy while allowing the interrupt to keep working.
  noInterrupts();
  tickCopy = ticks;
  interrupts();

  if (initialized) {    
    //Serial.println("All ready to go!");

    if (armed) {
      //Serial.println("Waiting for start trigger");

      if (started) {
	//Serial.println("Waiting for stop trigger");

	if (stopped) {
	  //Serial.println("All done!");
	  //send results here

          if (clock_adjust) {
            init_micros = init_time * timer_frequency;
            adjustment = init_micros * clock_adjust;
            init_micros += adjustment;

            arm_micros = arm_time * timer_frequency;
            adjustment = arm_micros * clock_adjust;
            arm_micros += adjustment;

            start_micros = start_time * timer_frequency;
            adjustment = start_micros * clock_adjust;
            start_micros += adjustment;

            stop_micros = stop_time * timer_frequency;
            adjustment = stop_micros * clock_adjust;
            stop_micros += adjustment;

          }
          else {            
            init_micros = init_time * timer_frequency;
            arm_micros = arm_time * timer_frequency;
            start_micros = start_time * timer_frequency;
            stop_micros = stop_time * timer_frequency;
          }

	  Serial.print("initialized: ");
	  Serial.print(init_micros);
	  Serial.print(" armed: ");
	  Serial.print(arm_micros);
	  Serial.print(" started: ");
	  Serial.print(start_micros);
	  Serial.print(" stopped: ");
	  Serial.print(stop_micros);
	  Serial.println();
	  
	  initialized = 0;
	  armed = 0;
	  started = 0;
	  stopped = 0;
	  arm_pin = -1;
	  start_pin = -1;
	  stop_pin = -1;
	}
	else {
	  //check for stop trigger
	  cur_value = analogRead(stop_pin);
	  if (cur_value > stop_threshold) {
	    //stop_time = millis();
	    stop_time = tickCopy;
	    stopped = 1;
	  }
	}
      }
      else {
	//check for start trigger
	cur_value = analogRead(start_pin);
	if (cur_value > start_threshold) {
	  //start_time = millis();
	  start_time = tickCopy;
	  started = 1;
	}
      }
    }
    else {
      //check for arm trigger
      cur_value = analogRead(arm_pin);
      if (cur_value > arm_threshold) {
	//arm_time = millis();
	arm_time = tickCopy;
	armed = 1;
      }
    }
      
  }
  else { 
    SCmd.readSerial(); // This is what processes serial commands

    if (debug) { 

      //debug_string = "->";
      //debug_string += debug_type;
      //debug_string += "<-";
      //Serial.println(debug_type);
      //Serial.println(debug_string);
      if (debug_type == "A") {
	debug_cur = analogRead(debug_pin);
      
      }
      else if (debug_type == NULL) { 
	Serial.println("debug_type = NULL");
      }
	
      else
      {
	//debug_type should == "D";
	debug_cur = digitalRead(debug_pin);

      }

      if (debug_cur != debug_last) {
	debug_string = "";
	debug_string += debug_cur;
	debug_string += ",";
	debug_string += micros();
	Serial.println(debug_string);
	delayMicroseconds(10);
	debug_last = debug_cur;
      }
    }
  }

}

