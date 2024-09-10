#!./cgi_runner.sh

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
try:
    serial_num = cgi.escape(form.getvalue("serial_num"))
except:
    serial_num = None

base.header(title='Board Checkout')
base.top(False)

if serial_num:
    board_check_functions.board_checkout_form_sn(serial_num)
else:
    board_check_functions.board_checkout_form_sn("")

base.bottom(False)
