#!/usr/bin/python3

import cgi
import base
import home_page_list
import board_check_functions 
import numpy
from connect import connect

db = connect(0)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
#url = form.getvalue("url")
try:
    bc = cgi.escape(form.getvalue("full_id"))
except:
    bc = None

base.header(title='Board Checkout')
base.top(False)

if bc:
    board_check_functions.board_checkout_form_sn(bc)
else:
    board_check_functions.board_checkout_form_sn("")

base.bottom(False)
