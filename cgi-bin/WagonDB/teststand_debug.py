#!./cgi_runner.sh

import cgi, html
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

base.header(title='Test Stands')
base.top()

# set up page header
print('<div class="row">')
print('<div class="col-md-12 ps-5 pt-4 mx-2 my-2"><h2>List of Current Tester Setups</h2></div>')
print('<div class="col-md-11 ps-5 py-2 my-2"><table class="table table-hover">')
print('<thead class="table-dark">')
print('<tr>')
print('<th> Test Stand </th>')
print('<th> Kria Controller </th>')
print('<th> Wagon Tester </th>')
print('<th> Interposer </th>')
print('<th> Wagon Wheel 1 </th>')
print('<th> Wagon Wheel 2 </th>')
print('<th> Wagon Wheel 3 </th>')
print('<th> Wagon Wheel 4 </th>')
print('</tr>')
print('</thead>')
print('<tbody>')
cur.execute('select teststand_id, name from Teststand')
for c in cur.fetchall():
    if c[1] == 'None':
        continue

    parts = {}
    print('<tr>')
    print('<td>%s</td>' % c[1])
    cur.execute('select component_id, role_id from Tester_Configuration where teststand_id=%s' % c[0])
    parts['Interposer'] = ''
    for t in cur.fetchall():
        cur.execute('select full_id from Tester_Component where component_id=%s' % t[0])
        sn = cur.fetchall()[0][0]

        cur.execute('select description from Tester_Roles where role_id=%s' % t[1])
        role = cur.fetchall()[0][0]
        if 'Interposer' in role:
            p = role.split()
            parts['Interposer'] += p[0] + ': ' + sn + '<br>'
        else:
            parts[role] = sn

    print('<td>%s</td>' % parts['Kria Controller'])
    print('<td>%s</td>' % parts['Wagon Tester'])
    print('<td>%s</td>' % parts['Interposer'])
    try:
        print('<td>%s</td>' % parts['Wagon Wheel 1'])
    except KeyError:
        continue
    try:
        print('<td>%s</td>' % parts['Wagon Wheel 2'])
    except KeyError:
        continue
    try:
        print('<td>%s</td>' % parts['Wagon Wheel 3'])
    except KeyError:
        continue
    try:
        print('<td>%s</td>' % parts['Wagon Wheel 4'])
    except KeyError:
        continue


    print('</tr>')

print('</tbody></table></div></div>')

base.bottom()

