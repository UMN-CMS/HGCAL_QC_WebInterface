#!/usr/bin/python3

import cgi
import base
import module_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Test Completion Status')
base.top(False)

tests = module_functions.get_test_completion_status()

# tells the GUI where to look
print('Begin')

for t in tests:
    print(t)

print('End')

base.bottom(False)
