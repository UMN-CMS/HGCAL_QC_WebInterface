#!/usr/bin/python3

import cgi, html
import base
import module_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Add New User')
base.top(False)

tests = module_functions.add_new_user_ID()

base.bottom(False)
