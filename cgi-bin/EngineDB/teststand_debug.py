#!/usr/bin/python3

import cgi
import cgitb
import base
import sys
import pandas as pd
import numpy as np
from connect import connect

cgitb.enable()
db = connect(0)
cur = db.cursor()

form = cgi.FieldStorage()
p = form.getvalue('person_id')

#cgi header
print("Content-type: text/html\n")

base.header(title='Test Stand Debug')
base.top(False)

# set up page header
print('<div class="row">')
print('<div class="col-md-12 ps-5 pt-4 mx-2 my-2"><h2>Test Stand Debug</h2></div>')
print('<div class="col-md-11 ps-5 py-2 my-2"><table class="table table-hover">')
print('<thead class="table-dark">')
print('<tr>')
print('<th> Board ID </th>')
print('<th> Test </th>')
print('<th> Date </th>')
print('<th> Outcome </th>')
print('<th> Attachment </th>')
print('<th> Test Stand Info </th>')
print('</tr>')
print('</thead>')
print('<tbody>')
# gets info from Test and sorts by date, newest first
cur.execute('select board_id,test_type_id,day,successful,test_id,config_id from Test where config_id is not NULL order by day desc')
for c in cur.fetchall():
    print('<tr>')
    cur.execute('select full_id from Board where board_id=%s' % c[0])
    sn = cur.fetchone()
    # links board page
    print('<td> <a href=module.py?board_id=%(id)s&full_id=%(sn)s> %(sn)s </a></td>' %{'id':c[0], 'sn':sn[0]})

    cur.execute('select name from Test_Type where test_type=%s' %c[1])
    test_name = cur.fetchone()
    print('<td>%s</td>' % test_name)
    print('<td>%s</td>' % c[2])
    
    # successful is either a 1 or a 0 in the DB, this converts
    if c[3] == 1:
        print('<td> Successful </td>')
    else:
        print('<td> Unsuccessful </td>')
    
    # gets attachment and links it
    cur.execute('select attach_id from Attachments where test_id=%s' % c[4])
    attach_id = cur.fetchone()
    print('<td><a href="get_attach.py?attach_id=%s">Attach</a></td>' % attach_id)
 
    print('<td><a href="get_teststand_info.py?config_id=%s">Configuration</a></td>' % c[5])

    print('</tr>')
print('</tbody></table></div></div>')

base.bottom(False)

