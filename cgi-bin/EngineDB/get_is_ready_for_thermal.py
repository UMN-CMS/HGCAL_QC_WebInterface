#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions_engine
import os

#cgi header
print("Content-type: text/json\n")

#base.header(title='Get Latest Test Results')
#base.top(False)

form = cgi.FieldStorage()

if form.getvalue('full_id'):
    full_id = html.escape(form.getvalue('full_id'))

    test_results = add_test_functions_engine.get_is_ready_for_thermal(full_id)

    print(test_results)


else:
    print('No serial number sent.')
#base.bottom(False)
