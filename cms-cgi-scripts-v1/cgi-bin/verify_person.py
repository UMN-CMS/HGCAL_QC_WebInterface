#!/usr/bin/python3

import cgi
import base
import add_test_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Types')
base.top()

form = cgi.FieldStorage()
name = cgi.escape(form.getvalue("name"))

tests = add_test_functions.verify_person(name)

print('Begin')

print(tests)

print('End')

base.bottom()
