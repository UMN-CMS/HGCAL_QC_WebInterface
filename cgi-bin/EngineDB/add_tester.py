#!./cgi_runner.sh

import cgi, html
import base
import home_page_list
import add_test_functions_engine

#cgi header
print("Content-type: text/html\n")

base.header(title='Add Tester')
base.top(False)

add_test_functions_engine.add_tester_template()

base.bottom(False)
