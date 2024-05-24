#!/usr/bin/python3

import cgi
import base
import home_page_list

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
serial_num = base.cleanCGInumber(form.getvalue('serial_num'))
board_id = base.cleanCGInumber(form.getvalue('board_id'))

base.header(title='Add extra information about board')
base.top(False)

home_page_list.add_board_info_form(serial_num, board_id)

print('<div class="row">')
print('<div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
print('<h2>List of All Boards</h2>' )
print('<b><em>(Sorted by Serial Number)</em></b>&emsp;<badge class="badge bg-primary">Successful Tests</badge>')
print('</div>')
print('</div>')

home_page_list.render_list_module()

base.bottom(False)

