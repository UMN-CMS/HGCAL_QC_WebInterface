#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions
import os
from connect import connect

print("Content-type: text/html\n")

db = connect(0)
cur = db.cursor()

form = cgi.FieldStorage()

full_id = form.getvalue('full_id')

cur.execute('select board_id from Board where full_id="%s"' % full_id)
board_id = cur.fetchone()

# board_id is a (id,) tuple when the barcode is known, else None.
if board_id:
    cur.execute('select comments from Grades where board_id=%s order by grade_id desc limit 1' % board_id)
    row = cur.fetchone()
    print(row[0] if row and row[0] is not None else "")
else:
    print("")

