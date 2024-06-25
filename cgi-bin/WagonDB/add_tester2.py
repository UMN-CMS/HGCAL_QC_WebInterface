#!/usr/bin/python3

import cgi
import base
import add_test_functions
import os
import connect
import sys
sys.path.insert(0, '../EngineDB/')
import add_test_functions as engine_add_test_functions

base_url = connect.get_base_url()

print("Location: %s/testers.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
person_name = cgi.escape(form.getvalue("person_name"))
password = cgi.escape(form.getvalue("password"))

base.header(title='Add Tester')
base.top(False)


print(person_name)
add_test_functions.add_tester(person_name, password)
engine_add_test_functions.add_tester(person_name, password)

base.bottom(False)
