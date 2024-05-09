#!/usr/bin/python3

import cgi
import base
import home_page_list
import module_functions
from connect import connect
import pandas as pd
import numpy as np

#cgi header
print("Content-type: text/html\n")


form = cgi.FieldStorage()
board_id = base.cleanCGInumber(form.getvalue('board_id'))
serial_num = form.getvalue('serial_num')
base.header(title='Wagon DB')
base.top()
#print('card_id = ', card_id)
#print  'serial_num = ', serial_num

module_functions.add_test_tab(serial_num, board_id)

db = connect(0)
cur = db.cursor()

revokes=module_functions.Portage_fetch_revokes(serial_num)

module_functions.board_info(serial_num)

cur.execute('select test_type, name from Test_Type where required = 1 order by relative_order ASC')
test_types = cur.fetchall()
for t in test_types:
	module_functions.ePortageTest(t[0], serial_num, t[1], revokes)

base.bottom()
