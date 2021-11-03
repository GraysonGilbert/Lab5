#!/usr/bin/python37all

#CGI Code

#importing required modules
import cgi
import json

data =cgi.FieldStorage()
#Key value variables
new_angle = data.getvalue("slider1")
sub_button = data.getvalue("sub_button")

#Dictionary for information to be stored
info = {}
info = {'slider1':new_angle, 'sub_button':sub_button}

#Using Json to write the key values and pass them to a text file
with open('step_info.txt', 'w') as f:
  json.dump(info, f)

#Creating a screen with a slider, buttons, and prompts on screen
print('Content-type: text/html\n\n')
print('<html>')
print('<form sub_button="/cgi-bin/stepper_control_back.py" method="POST">')
print('Click button to zero the motor <br>')
print('<input type="submit" name="sub_button" value= "Yes, Move Motor to Zero Position"><br><br>')
print('Select a motor angle using the slider. <br>')
print('input type="range" name="slider1" min="0" max="360" value= "%s" <br>' %new_angle)
print('input type="submit" name="sub_button" vlaue="Yes, Change Angle">')
print('</form>')

#ThingSpeak data

print('<iframe width="450" height="260" style="border: 1px solid #cccccc;" src="https://thingspeak.com/channels/1557663/widgets/375618"></iframe>')
print('<iframe width="450" height="260" style="border: 1px solid #cccccc;" src="https://thingspeak.com/channels/1557663/charts/1?bgcolor=%23ffffff&color=%23d62020&dynamic=true&results=60&timescale=15&title=Motor+Angle+Vs+Time&type=line&xaxis=Time+%28s%29&yaxis=Motor+Angle"></iframe>')

print('</html')