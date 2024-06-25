#!/usr/bin/python3

import cgi
import base
import add_test_functions
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Previous Test Results')
base.top(False)

form = cgi.FieldStorage()

if form.getvalue('full_id'):
    full_id = cgi.escape(form.getvalue('full_id'))

    add_test_functions.get_previous_test_results(full_id)

else:
    print('No serial number sent.')
base.bottom(False)
