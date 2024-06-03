#!/usr/bin/python3

import cgi
import base
from add_label_functions import upload_label

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
label = form.getvalue('label')

upload_label(label)
