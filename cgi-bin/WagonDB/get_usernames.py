#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions_wagon 
import os

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Usernames')
base.top(False)

usernames = add_test_functions_wagon.get_usernames()

print('Begin')

for t in usernames:
    try:
        print(t[0])
    except:
        print("No users available")

print('End')

base.bottom(False)
