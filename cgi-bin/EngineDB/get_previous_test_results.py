#!/usr/bin/python3

import cgi
import base
import add_test_functions
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Previous Test Results')
base.top()

form = cgi.FieldStorage()

if form.getvalue('serial_number'):
    serial_number = cgi.escape(form.getvalue('serial_number'))

    add_test_functions.get_previous_test_results(serial_number)

else:
    print('No serial number sent.')
base.bottom()
