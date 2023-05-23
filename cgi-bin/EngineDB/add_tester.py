#!/usr/bin/python3

import cgi
import base
import home_page_list
import add_test_functions

#cgi header
print("Content-type: text/html\n")

base.header(title='Add Tester')
base.top()

add_test_functions.add_tester_template()

base.bottom()
