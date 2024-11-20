#!./cgi_runner.sh

import cgi, html
import base
import home_page_list
import add_test_functions_wagon

#cgi header
print("Content-type: text/html\n")

base.header(title='Add New Test Template')
base.top(False)

add_test_functions_wagon.add_new_test_template()

base.bottom(False)

