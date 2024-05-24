#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import label_functions
import sys

#cgi header
print("content-type: text/html\n\n")

base.header(title='HGCAL Labeling Home Page')
base.top()

label_functions.label_type_table()

base.bottom()
