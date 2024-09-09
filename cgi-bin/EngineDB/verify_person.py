#!/usr/bin/python3

import cgi, html
import base
import add_test_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Types')
base.top(False)

form = cgi.FieldStorage()
print("\n\n\n\n\n\n\n\n\n\n\n\n\nABSOLUTELY MASSIVE", form, "\n\n\n\n\n\n\n\n\n")


name = html.escape(form.getvalue("tester"))

tests = add_test_functions.verify_person(name)

print('Begin')

print(tests)

print('End')

base.bottom(False)
