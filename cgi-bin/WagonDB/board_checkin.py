#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import home_page_list
import board_check_functions 


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()

# this page can be accessed from a link that autofills the serial number
# or it can be accessed normally, this checks which one it is
try:
    sn = cgi.escape(form.getvalue("serial_num"))
    board_id = base.cleanCGInumber(form.getvalue("board_id"))
except:
    sn = None
    board_id = None

base.header(title='Board Check In')
base.top(False)

if sn:
    board_check_functions.board_checkin_form_sn(sn)
else:
    board_check_functions.board_checkin_form_sn("")

base.bottom(False)
