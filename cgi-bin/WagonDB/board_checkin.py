#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import home_page_list
import board_check_functions 


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
#url = form.getvalue("url")
#try:
sn = cgi.escape(form.getvalue("serial_num"))
board_id = base.cleanCGInumber(form.getvalue("board_id"))
#except:
#    board_id = None

base.header(title='Board Check In')
base.top()

if sn:
    board_check_functions.board_checkin_form_sn(sn)
else:
    board_check_functions.board_checkin_form_sn("")

base.bottom()
