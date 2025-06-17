#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
import home_page_list
import board_check_functions 


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
try:
    board_id = base.cleanCGInumber(form.getvalue("board_id"))
except:
    board_id = None

base.header(title='Board Check In')
base.top()

if board_id:
    board_check_functions.board_checkin_form_sn(board_id)
else:
    board_check_functions.board_checkin_form_sn("")

base.bottom()
