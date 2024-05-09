#!/usr/bin/python3

import cgi
import base
import home_page_list
import module_functions
from connect import connect

#cgi header
print("Content-type: text/html\n")


form = cgi.FieldStorage()
test_id = base.cleanCGInumber(form.getvalue('test_id'))
base.header(title='Wagon DB')
base.top()

module_functions.add_revoke(test_id)

base.bottom()
