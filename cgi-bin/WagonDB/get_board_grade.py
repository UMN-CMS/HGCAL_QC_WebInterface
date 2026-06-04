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

cur.execute('select grade from Grades where board_id=%s' % board_id)
grade = cur.fetchone()[0]

print(grade)
