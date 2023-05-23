#!/usr/bin/python3

import cgi
import base
import module_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Types')
base.top()

tests = module_functions.get_test_types()

print('Begin')

for t in tests:
    print(t)

print('End')

base.bottom()
