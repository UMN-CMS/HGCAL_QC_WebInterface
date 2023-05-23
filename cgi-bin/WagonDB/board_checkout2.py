#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import board_check_functions
import os
import connect

base_url = connect.get_base_url()

print("Location: %s/summary.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
serial_num = cgi.escape(form.getvalue("serial_number"))
person_id = base.cleanCGInumber(form.getvalue("person_id"))
test_type = base.cleanCGInumber(form.getvalue("test_type"))
comments = form.getvalue("comments")

if comments:
    comments = cgi.escape(comments)

base.header(title='Board Checkout')
base.top()

board_check_functions.board_checkout(serial_num, person_id, test_type, comments)

base.bottom()
