#!/usr/bin/python3

import cgi
import base
from add_label_functions import decode_label

#cgi header
print("Content-type: text/html\n")

# takes in a label and prints out the decoded information
# this goes to the GUI and is really only used for Wagons and Engines
form = cgi.FieldStorage()
label = form.getvalue('label')

data = decode_label(label)

print('Begin')

for i in data:
    print(i)

print('End')
