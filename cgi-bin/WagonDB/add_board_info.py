#!/usr/bin/python3

import cgi
import base
import home_page_list

#cgi header
print("Content-type: text/html\n")

# gets board info
form = cgi.FieldStorage()
serial_num = cgi.escape(form.getvalue('serial_num'))
board_id = base.cleanCGInumber(form.getvalue('board_id'))

base.header(title='Add extra information about board')
base.top(False)

# sends board info here
home_page_list.add_board_info_form(serial_num, board_id)

base.bottom(False)

