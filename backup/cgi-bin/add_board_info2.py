#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import os

cgitb.enable()

print("Location: http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/summary.py\n\n")
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
sn = base.cleanCGInumber(form.getvalue("serial_num"))
board_id = base.cleanCGInumber(form.getvalue("board_id"))
location = form.getvalue("location")
daqid = form.getvalue("daq_chip_id")
trig1id = form.getvalue("trigger_chip_1_id")
trig2id = form.getvalue("trigger_chip_2_id")
comments = cgi.escape(form.getvalue("comments"))

base.header(title='Add Board Info')
base.top()

print(location, daqid, trig1id, trig2id, comments)

module_functions.add_board_info(board_id, str(sn), location, daqid, trig1id, trig2id, comments)

base.bottom()
