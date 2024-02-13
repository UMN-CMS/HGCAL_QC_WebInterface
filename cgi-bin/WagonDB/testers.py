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

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/testers.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Testers')
base.top()

print('<div class="row">')
print('<div class="col-md-8 ps-4 pt-4 mx-2 my-2"><h2>Tester Summary</h2></div>')
print('<div class="col-md-3 pt-2 ps-2">')
print('<br>')
print('<a href="password_entry.py?url=add_tester.py">')
print('<button type="button" class="btn btn-dark text-light">Add New Tester</button>')
print('</a>')
print('</div>')
print('</div>')


cur.execute('select person_id from Test')
temp = cur.fetchall()
person_ids = []
for t in temp:
    person_ids.append(t[0])
people = np.unique(person_ids).tolist()

for p in people:
    if p != 0:
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
        print('<th colspan=2> Tests Completed </th>')
        print('</tr>')
        print('</thead>')
        print('<tbody>')
        subtypes = []
        cur.execute('select board_id from Test where person_id=%s' % p)
        temp = cur.fetchall()
        for t in temp:
            cur.execute('select type_id from Board where board_id="%s"' % t[0])
            new = cur.fetchall()
            subtypes.append(new[0][0])
        subtypes = np.unique(subtypes).tolist()
        
        serial_numbers = {}
        for s in subtypes:
            cur.execute('select full_id from Board where type_id="%s"' % s)
            li = []
            for l in cur.fetchall():
                cur.execute('select board_id from Test where person_id=%s' % p)
                temp = cur.fetchall()
                temp_ids = []
                for t in temp:
                    temp_ids.append(t[0])
                temp_ids = np.unique(temp_ids).tolist()
                cur.execute('select board_id from Board where full_id="%s"' % l[0])
                b = cur.fetchall()[0][0]
                if b in temp_ids:
                    li.append(l[0])
            serial_numbers[s] = np.unique(li).tolist()
            print('<tr><td colspan=2><b>%s</b></td></tr>' %s)
            for sn in serial_numbers[s]:
                cur.execute('select board_id from Board where full_id="%s"' % sn)
                b = cur.fetchall()[0][0]
                cur.execute('select test_type_id from Test where person_id=%(p)s and board_id=%(b)s' %{'p':p, 'b':b})
                tests_completed = cur.fetchall()
                print('<tr>')
                print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(sn)s> %(sn)s </a></td>' %{'id':s, 'sn':sn})
                print('<td>')
                print('<ul>')
                for t in tests_completed:
                    cur.execute('select name from Test_Type where test_type=%s' %t)
                    n = cur.fetchall()[0][0]
                    print('<li>%s' %n)
                print('</ul>')
                print('</td>')
                print('</tr>')
        print('</tbody></table></div></div>')

base.bottom()
