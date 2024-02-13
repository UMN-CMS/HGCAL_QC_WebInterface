#!/usr/bin/python3

import module_functions
import cgi
import base

#print("Location: %s/home_page.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
sn = cgi.escape(form.getvalue("serial_number"))
location = cgi.escape(form.getvalue("location"))

base.header(title='Change Board Location')
base.top()
try:
    module_functions.change_board_location(str(sn), location)
except Exception as e:
    print("Issue updating board location")
    print(e)

base.bottom()
