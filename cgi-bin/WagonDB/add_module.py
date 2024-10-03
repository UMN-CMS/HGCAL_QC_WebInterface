#!/usr/bin/python3

import cgi, html
import base
import home_page_list

#cgi header
print("Content-type: text/html\n")

base.header(title='Add a new module to HGCAL Wagon Test')
base.top(False)

# calls this function for the form
home_page_list.add_module_form()
base.bottom(False)

