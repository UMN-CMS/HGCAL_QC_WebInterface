#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Types')
base.top()

form = cgi.FieldStorage()

name = html.escape(form.getvalue("tester"))

tests = add_test_functions.verify_person(name)

print('Begin')

print(tests)

print('End')

base.bottom()
