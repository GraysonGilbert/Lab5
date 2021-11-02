#Importing all modules required for lab
import RPi.GPIO as GPIO
import time
import smbus
import json



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

    if angle_diff == 360 or angle_diff == -360:
      dir = 1
      steps = 0
      motor.turnSteps(steps, dir)
    elif angle_diff <= 180 and angle_diff > 0:
      dir = -1
      steps = 8 * int(angle_diff/0.703)
      print("Turning steps")
      motor.turnSteps(steps,dir)
    elif angle_diff > 180:
      dir = 1
      steps = 8 * int((360 - angle_diff)/.703)
      motor.turnSteps(steps, dir)
    elif angle_diff < 0 and angle_diff >= -180:
      dir = 1
      steps = 8 * (abs(int(360 - angle_diff) / .703))
      motor.turnSteps(steps, dir)
    elif angle_diff < -180:
      dir = -1
      steps = 8 * int(angle_diff / 0.703)
      motor.turnSteps(steps, dir)


  def zero(motor,pin):
    #Turn the motor until the photoresistor is occluded by the cardboard piece
    GPIO.output(pin, 1)
    time.sleep(.5)
    def loop(): 
      PCF8591.setup(0x48)
      while True:
        print(PCF8591.read(0))
        
    
        

    



  
myStepper = Stepper(0)

try:
  myStepper.goAngle(180)
  myStepper.zero(ledPin)
  print(PCF8591.read(0))
except KeyboardInterrupt:
  pass
  