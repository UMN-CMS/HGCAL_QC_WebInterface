#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions
import os
import connect

base_url = connect.get_base_url()

print("Location: %s/summary.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
test_name = html.escape(form.getvalue("test_name"))
required = base.cleanCGInumber(form.getvalue("required"))
test_desc_short = html.escape(form.getvalue("test_desc_short"))
test_desc_long = html.escape(form.getvalue("test_desc_long"))
password = html.escape(form.getvalue("password"))

base.header(title='Add New Test Template')
base.top()

test_id=add_test_functions.add_new_test(test_name, required, test_desc_short, test_desc_long, password)
    
base.bottom()
