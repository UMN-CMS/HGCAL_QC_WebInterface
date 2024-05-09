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

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/testers.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Testers')
base.top()

print('<div class="row">')
print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Tester Summary</h2></div>')
print('<div class="col-md-2 ps-4 pt-4 my-2">')
print('<a href="tester_summary.py">')
print('<button type="button" class="btn btn-dark text-light">Back to Tester List</button>')
print('</a>')
print('</div>')
print('<div class="col-md-3 pt-2 ps-2">')
print('<br>')
print('<a href="password_entry.py?url=add_tester.py">')
print('<button type="button" class="btn btn-dark text-light">Add New Tester</button>')
print('</a>')
print('</div>')
print('</div>')


cur.execute('select person_name from People where person_id=%s' % p)
name = cur.fetchall()[0][0]
print('<div class="row">')
print('<div class="col-md-12 ps-5 py-2 mx-2 my-2">')
print('<h3>%s</h3>' % name)
print('</div>') 
print('<div class="col-md-11 ps-5 py-2 my-2"><table class="table table-hover">')
print('<thead class="table-dark">')
print('<tr>')
print('<th> Board ID </th>')
print('<th> Test </th>')
print('<th> Date </th>')
print('<th> Outcome </th>')
print('<th> Attachment </th>')
print('</tr>')
print('</thead>')
print('<tbody>')
subtypes = []
cur.execute('select board_id,test_type_id,day,successful,test_id from Test where person_id=%s order by day desc' % p)
for c in cur.fetchall():
    print('<tr>')
    cur.execute('select full_id from Board where board_id=%s' % c[0])
    sn = cur.fetchone()
    print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(sn)s> %(sn)s </a></td>' %{'id':c[0], 'sn':sn[0]})

    cur.execute('select name from Test_Type where test_type=%s' %c[1])
    test_name = cur.fetchone()
    print('<td>%s</td>' % test_name)
    print('<td>%s</td>' % c[2])
    
    if c[3] == 1:
        print('<td> Successful </td>')
    else:
        print('<td> Unsuccessful </td>')
    
    cur.execute('select attach_id from Attachments where test_id=%s' % c[4])
    attach_id = cur.fetchone()
    print('<td><a href="get_attach.py?attach_id=%s">Attach</a></td>' % attach_id)
    print('</tr>')
print('</tbody></table></div></div>')

base.bottom()
