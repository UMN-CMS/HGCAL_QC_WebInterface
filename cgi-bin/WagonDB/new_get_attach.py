#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")


form = cgi.FieldStorage()
attach_id = base.cleanCGInumber(form.getvalue('attach_id'))

print(attach_id)
