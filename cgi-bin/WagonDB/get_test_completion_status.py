#!/usr/bin/python3

import cgi
import base
import module_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Completion Status')
base.top()

tests = module_functions.get_test_completion_status()

print('Begin')

for t in tests:
    print(t)

print('End')

base.bottom()
