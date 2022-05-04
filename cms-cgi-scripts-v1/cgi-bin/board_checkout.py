#!/usr/bin/python3

import cgi
import base
import home_page_list
import board_check_functions 


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
#url = form.getvalue("url")
serial_num = base.cleanCGInumber(form.getvalue("serial_num"))

base.header(title='Board Checkout')
base.top()

if serial_num:
    board_check_functions.board_checkout_form_sn(serial_num)
else:
    board_check_functions.board_checkout_form_sn("")

base.bottom()
