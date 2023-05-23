#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import board_check_functions
import os
import connect

base_url = connect.get_base_url()

#print("Location: %s/summary.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
board_id = base.cleanCGInumber(form.getvalue("board_id"))

base.header(title='Board Check In')
base.top()

board_check_functions.board_checkin(board_id)

base.bottom()
