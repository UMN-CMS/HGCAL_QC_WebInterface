#!/usr/bin/python3

import cgi
import cgitb
import base
import sys
import tempfile
import os

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Total Tests Over Time')
base.top()
try:
    import matplotlib
except Exception as e2:
    print(e2)

base.bottom()
