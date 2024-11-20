#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions_wagon 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Types')
base.top(Fals)

form = cgi.FieldStorage()
print("\n\n\n\n\n\n\n\n\n\n\n\n\nABSOLUTELY MASSIVE", form, "\n\n\n\n\n\n\n\n\n")


name = html.escape(form.getvalue("tester"))

tests = add_test_functions_wagon.verify_person(name)

# tells the GUI where to look
print('Begin')

print(tests)

print('End')

base.bottom(False)
