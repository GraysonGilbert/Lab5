import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

pins = [18,21,22,23] # controller inputs: in1, in2, in3, in4
for pin in pins:
  GPIO.setup(pin, GPIO.OUT, initial=0)

sequence = [ [1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],
      [0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1] ]

state = 0



class Stepper:

  def __init__(motor,pins,sequence,state):
    motor.pins = pins
    motor.sequence = sequence
    motor.state = state 

def delay_us(tus): # use microseconds to improve time resolution
  endTime = time.time() + float(tus)/ float(1E6)
  while time.time() < endTime:
    pass

  def halfstep(dir):
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
  

  def turnSteps(motor,steps, dir):
    #move the actuation sequence a given number of half steps
    for step in range(steps):
      motor.halfstep(dir)



  #def goAngle():
    #mve a specified angle, taking the shortest path at a user defined speed

  #def zero():
    #Turn the motor until the photoresistor is occluded by the cardboard piece






  
myStepper = Stepper(pins,sequence,state)

try:
  myStepper.turnSteps(4096,1)
except:
  pass
GPIO.cleanup() 