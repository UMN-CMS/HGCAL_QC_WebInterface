#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import os
import connect

cgitb.enable()

base_url = connect.get_base_url()

print("Location: %s/summary.py\n\n"%(base_url))
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
full_id = cgi.escape(form.getvalue("full_id"))
board_id = base.cleanCGInumber(form.getvalue("board_id"))
location = form.getvalue("location")
daqid = form.getvalue("daq_chip_id")
trig1id = form.getvalue("trigger_chip_1_id")
trig2id = form.getvalue("trigger_chip_2_id")
comments = cgi.escape(form.getvalue("comments"))

base.header(title='Add Board Info')
base.top(False)

# sends board info here to be sent to DB
module_functions.add_board_info(board_id, str(full_id), location, daqid, trig1id, trig2id, comments)

base.bottom(False)

