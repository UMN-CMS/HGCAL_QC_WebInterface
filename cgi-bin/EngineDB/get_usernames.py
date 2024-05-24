#!/usr/bin/python3

import cgi
import base
import add_test_functions 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Usernames')
base.top(False)

usernames = add_test_functions.get_usernames()

print('Begin')

for t in usernames:
    print(t[0])

print('End')

base.bottom(False)
