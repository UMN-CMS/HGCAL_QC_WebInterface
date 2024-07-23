#!/usr/bin/python3

import cgi
import base
import add_test_functions
import os
from connect import connect

print("Content-type: text/html\n")

base.header(title='is_new_board')
base.top(False)

db = connect(0)
cur = db.cursor()

form = cgi.FieldStorage()

daq_chip_id = form.getvalue('daq_chip_id')
cur.execute('select full_id from Board where daq_chip_id="%s"' % daq_chip_id)
full_id = cur.fetchall()[0][0]

print('Begin')
print(full_id)
print('End')


base.bottom(False)

