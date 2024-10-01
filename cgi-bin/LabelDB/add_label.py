#!/usr/bin/python3

import cgi
import base
import json
from add_label_functions import upload_label

#cgi header
print("Content-type: text/html\n")

# gets label from Labeling GUI and uploads it to the database

form = cgi.FieldStorage()
label = form.getvalue('labels')

label_dict = json.loads(label)


print("Received label file")
print("Uploading...")

for label in label_dict.keys():
    upload_label(label)

print("Done")
