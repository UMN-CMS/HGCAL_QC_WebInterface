#!/usr/bin/python3

import cgi
import cgitb
cgitb.enable()
import base
from connect import connect
import os
import sys

db = connect(0)
cur = db.cursor()

#cgi header
print("content-type: text/html\n\n")

base.header(title='Search Results')
base.top()
form = cgi.FieldStorage()
try:
    serial_num = cgi.escape(form.getvalue('serial_num'))
except:
    serial_num = form.getvalue('serial_num')
how = cgi.escape(form.getvalue('query'))

print('<div class="row">')
print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2>Search Results for %s</h2>' % serial_num)
print('</div>')
print('</div>')

if how == 'Contains':
    query = 'select full_label from Label where full_label like "%{}%" order by full_label'.format(serial_num)

if how == 'Starts with':
    query = 'select full_label from Label where full_label like "{}%" order by full_label'.format(serial_num)

if how == 'Ends with':
    query = 'select full_label from Label where full_label like "%{}" order by full_label'.format(serial_num)

cur.execute(query)
labels = cur.fetchall()
print('''
<div class="row">
    <div class="col-md-10 pt-4 ps-5 mx-2 my-2">

''')

if labels != []:
    print('<ul class="list-group">')
    for label in labels:
        print('<li class="list-group-item">%s</li>' % label[0])

    print('</ul>')
   
else:
    print("<h3>No labels found matching this pattern.</h3>")
 
print('''
    </ul>
    </div>
</div>
''')
        
base.bottom()
