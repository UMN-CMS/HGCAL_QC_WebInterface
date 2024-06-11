#!/usr/bin/python3

import cgi
import base
from add_label_functions import decode_label

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
label = form.getvalue('label')

data = decode_label(label)

print('Begin')

for i in data:
    print(i)

print('End')
