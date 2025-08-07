#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions
import os
import sys

#cgi header
print("Content-type: text/json\n")

#base.header(title='Get Latest Test Results')
#base.top()

form = cgi.FieldStorage()

if form.getvalue('full_id'):
    full_id = html.escape(form.getvalue('full_id'))

    num_failures = add_test_functions.get_thermal_failures(full_id)

    print(num_failures)


else:
    print('No serial number sent.')
#base.bottom()
