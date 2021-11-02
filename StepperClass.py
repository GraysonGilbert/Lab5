import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

pins = [18,21,22,23] # controller inputs: in1, in2, in3, in4
for pin in pins:
  GPIO.setup(pin, GPIO.OUT, initial=0)

# Define the pin sequence for counter-clockwise motion, noting that
# two adjacent phases must be actuated together before stepping to
# a new phase so that the rotor is pulled in the right direction:
sequence = [ [1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],
        [0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1] ]

state = 0 #current positon in the stator sequence


def delay_us(tus): # use microseconds to improve time resolution
  endTime = time.time() + float(tus)/ float(1E6)
  while time.time() < endTime:
    pass

def halfstep(dir):
  #dir = +/- 1 for ccw or cw respectfully
  global state
  state = state + dir
  if state > 7:
    state = 0
  if state < 0:
    state = 7

  for pin in range(4):    # 4 pins that need to be energized
    GPIO.output(pins[pin],sequence[state][pin])
  delay_us(1000)
  
def turnSteps(steps, dir):
  #move the actuation sequence a given number of half steps
  for step in range(steps):
    halfstep(dir)


class Stepper:
  def __init__(motor):

  def goAngle(angle): #moves to a specified angle
    #1 step = .703 degrees of an angle
    #0 and 360 degrees is at the 0 point located at led

    #steps:
    # 1. read current angle
    # 2. if desired angle - current angle <= 180 degrees, the move ccw towards angle. if it is > 180 degrees move cw towards final angle
    # 3. steps required to move angle in ccw direction (direction 0) is (desired angle - current angle) / .703 
    #3.5 if faster to move other way aka difference greater than 180, steps required is (360 - angle difference)/.703 in direction 0
    # 4. call turnsteps with direction and number of steps to move to new location
    # . update current angle

  def zero():
    #turns motor untl photoresistor is blocked by cardboard
    



try:
  turnSteps(4096,1)
except:
  pass
GPIO.cleanup() 
