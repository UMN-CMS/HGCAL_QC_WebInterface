#!/usr/bin/python3

import cgi
import base
import os
from connect import connect

#cgi header
print("Content-type: text/html\n")

base.header(title='Add Engine Components')
base.top(False)

db = connect(1)
cur = db.cursor()

form = cgi.FieldStorage()

barcode = form.getvalue('barcode')
full_id = form.getvalue('full_id')

cur.execute('update Board set LDO="%s" where full_id="%s"' % (barcode, full_id))
db.commit()

base.bottom(False)
