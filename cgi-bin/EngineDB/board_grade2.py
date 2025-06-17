#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
import add_test_functions
import os
from connect import connect, get_base_url

base_url = get_base_url()
db = connect(0)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

# grabs the information from the form and calls board_checkin() to enter info into the DB
form = cgi.FieldStorage()
try:
    full = form.getvalue('full_id')
    cur.execute('select board_id from Board where full_id="%s"' % full)
    board_id = cur.fetchall()[0][0]
except:
    board_id = base.cleanCGInumber(form.getvalue("board_id"))
try:
    person_id = base.cleanCGInumber(form.getvalue("person_id"))
except:
    person_id = form.getvalue('person_id')
    cur.execute('select person_id from People where person_name="%s"' % person_id)
    person_id = cur.fetchall()[0][0]

grade = form.getvalue("grade")
comments = html.escape(form.getvalue("comment"))
passwd = html.escape(form.getvalue("password"))

base.header(title='Board Grade')
base.top()

add_test_functions.add_board_grade(passwd, board_id, person_id, grade, comments)

base.bottom()
