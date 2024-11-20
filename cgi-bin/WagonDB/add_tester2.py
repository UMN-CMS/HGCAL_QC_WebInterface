#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions_wagon
import os
import connect
import sys
sys.path.append(0, '../EngineDB/')
import add_test_functions_engine

base_url = connect.get_base_url()

#print("Location: %s/testers.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
person_name = html.escape(form.getvalue("person_name"))
password = html.escape(form.getvalue("password"))

base.header(title='Add Tester')
base.top(False)


print(person_name)
add_test_functions_wagon.add_tester(person_name, password)
add_test_functions_engine.add_tester(person_name, password)

base.bottom(False)
