#Importing all modules required for lab
import RPi.GPIO as GPIO
import time
import smbus
import json
from urllib.request import urlopen
from urllib.parse import urlencode

#Thingspeak API Code
api = "6E5CGYMRINBCUCBP"

GPIO.setmode(GPIO.BCM)
#STEPPER MOTOR SETUP
pins = [18,21,22,23] # controller inputs: in1, in2, in3, in4
for pin in pins:
  GPIO.setup(pin, GPIO.OUT, initial=0)

sequence = [ [1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],
      [0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1] ]

state = 0

#LED SETUP
ledPin = 4
GPIO.setup(ledPin, GPIO.OUT, initial = 0)

#MICROSECOND DELAY FUNCTION
def delay_us(tus): # use microseconds to improve time resolution
  endTime = time.time() + float(tus)/ float(1E6)
  while time.time() < endTime:
    pass

#ADC CLASS from lab 3
class PCF8591:

  def __init__(self,address):
    self.bus = smbus.SMBus(1)
    self.address = address

  def read(self,chn): #channel
      try:
          self.bus.write_byte(self.address, 0x40 | chn)  # 01000000
          self.bus.read_byte(self.address) # dummy read to start conversion
      except Exception as e:
          print ("Address: %s \n%s" % (self.address,e))
      return self.bus.read_byte(self.address)

  def write(self,val):
      try:
          self.bus.write_byte_data(self.address, 0x40, int(val))
      except Exception as e:
          print ("Error: Device address: 0x%2X \n%s" % (self.address,e))

#LED CLASS - used to get photoresistor reading from adc 
class LedReading:
  def __init__(led,address):
    led.address = PCF8591(address)

  def ledBrightness(led):
    return led.address.read(0)


#STEPPER MOTOR CLASS
class Stepper:

  def __init__(motor,angle):
    motor.angle = angle

  def halfstep(motor, dir):
    #dir = +/- 1 for cw or cw respectfully
    global state
    state = state + dir
    if state > 7:
      state = 0
    if state < 0:
      state = 7

    for pin in range(4):    # 4 pins that need to be energized
      GPIO.output(pins[pin],sequence[state][pin])
    delay_us(1000)
  

  def turnSteps(motor, steps, dir):
    #move the actuation sequence a given number of half steps
    for step in range(steps):
      motor.halfstep(dir)


  def goAngle(motor, new_angle):
    #mve a specified angle, taking the shortest path at a user defined speed
    #1 step = .703 degrees of an angle
    #0 and 360 degrees is at the 0 point located at led

    #steps:
    # 1. if desired angle - current angle <= 180 degrees, the move ccw towards angle. if it is > 180 degrees move cw towards final angle
    # 2. steps required to move angle in ccw direction (direction 0) is 8 * (desired angle - current angle) / .703 
    #3.5 if faster to move other way aka difference greater than 180, steps required is 8 * (360 - angle difference)/.703 in direction 0
    # 3. call turnsteps with direction and number of steps to move to new location

    angle_diff = new_angle - motor.angle
    print(angle_diff)

    if angle_diff > 180:
      angle_diff = 360 - angle_diff
    if angle_diff < -180:
      angle_diff = 360 + angle_diff
    steps = 8*(int(angle_diff/.703))

    if steps < 0:
      motor.turnSteps(-steps, -1)
    else:
      motor.turnSteps(steps, 1)

# Zeros the motor based on the reading from the photoresistor and LED
  def zero(motor,pin):
    GPIO.output(pin, 1)
    time.sleep(.5)
    led_blocked = 0
    while led_blocked == 0:
      myLed = LedReading(0x48)
      brightness = myLed.ledBrightness()
      print(brightness)
      if brightness > 15:
        if motor.angle < 180:
          motor.turnSteps(4,1)
        else:
          motor.turnSteps(4,1)
      else:
        
        GPIO.output(pin, 0)
        led_blocked = 1
        motor.angle = 0
        print(motor.angle)
        
    

def ThingSpeakWrite(angle):
  parameters = {1: angle, "api_key":api}
  parameters = urlencode(parameters)
  url = "https://api.thingspeak.com/update?" + parameters
  response = urlopen(url)
  print(response.status, response.reason)



try:
  myStepper = Stepper(0)
  time.sleep(1)
  myStepper.zero(ledPin)

  old_data = 0
  while True:
    with open('step_info.txt', 'r') as f:
      data = json.load(f)
      sub_button = str(data['sub_button'])
      newangle = int(data['slider1'])
    print(data)
    
    if data != old_data:
      if sub_button == 'Yes, Move Motor to Zero Position':
        myStepper.zero(ledPin)
        old_data = data
        ThingSpeakWrite(myStepper.angle)
      if sub_button == 'Yes, Change Angle':
        myStepper.goAngle(newangle)
        old_data = data
        ThingSpeakWrite(myStepper.angle)
    time.sleep(.1)

except KeyboardInterrupt:
  pass
  GPIO.cleanup()
  