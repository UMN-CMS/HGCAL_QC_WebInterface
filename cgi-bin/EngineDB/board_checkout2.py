#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import board_check_functions
import os
from connect import connect, get_base_url

base_url = get_base_url()
db = connect(0)
cur = db.cursor()

#print("Location: %s/summary.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
try:
    full = form.getvalue('full_id')
    cur.execute('select board_id from Board where full_id="%s"' % full)
    board_id = cur.fetchall()[0][0]
except:
    board_id = base.cleanCGInumber(form.getvalue("board_id"))
try:
    person_id = base.cleanCGInumber(form.getvalue("person_id"))
    print(person_id)
except:
    person_id = form.getvalue('person_id')
    cur.execute('select person_id from People where person_name="%s"' % person_id)
    person_id = cur.fetchall()[0][0]

comments = form.getvalue("comments")

base.header(title='Board Check Out')
base.top(False)

board_check_functions.board_checkout(board_id, person_id, comments)

base.bottom(False)
