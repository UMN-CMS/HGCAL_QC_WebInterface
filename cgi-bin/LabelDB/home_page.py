#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import label_functions
import sys
import numpy as np
from connect import connect

db = connect(0)
cur = db.cursor()

#cgi header
print("content-type: text/html\n\n")

base.header(title='HGCAL Labeling Home Page')
base.top()

print('<div class="row">')
print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
print('<tr><th>Major Type<th>Total Labels Made<th># of Subtypes<th>Total Boards with Labels</tr>')

cur.execute('select major_type_id,name from Major_Type order by name')
major_types = cur.fetchall()

# puts orphan at the top
for m in major_types:
        if m[1] == 'ORPHAN':
            cur.execute('select label_id,count(*) from Label where major_type_id=%s' % m[0])
            a1 = cur.fetchall()[0]
            cur.execute('select sub_type_id,count(*) from Major_Sub_Stitch where major_type_id=%s' % m[0])
            a2 = cur.fetchall()[0]
            cur.execute('select full_label,count(distinct full_label) from Label where major_type_id=%s' % m[0])
            a3 = cur.fetchall()[0]

            if a2[1] != 0:
                print('<tr><td><a href="labels_major.py?major_type_id=%s">%s</a>' % (m[0], m[1]))
            else:
                print('<tr><td>%s' % (m[1]))
                
            try:
                print('<td>%s' % (a1[1]))
            except IndexError:
                print('<td>0')
            try:
                print('<td>%s' % (a2[1]))
            except IndexError:
                print('<td>0')
            try:
                print('<td>%s' % (a3[1]))
            except IndexError:
                print('<td>0')

            print('</tr>')
        else:
            pass

for m in major_types:
        if m[1] != 'ORPHAN':
            cur.execute('select label_id,count(*) from Label where major_type_id=%s' % m[0])
            a1 = cur.fetchall()[0]
            cur.execute('select sub_type_id,count(*) from Major_Sub_Stitch where major_type_id=%s' % m[0])
            a2 = cur.fetchall()[0]
            cur.execute('select full_label,count(distinct full_label) from Label where major_type_id=%s' % m[0])
            a3 = cur.fetchall()[0]

            if a2[1] != 0:
                print('<tr><td><a href="labels_major.py?major_type_id=%s">%s</a>' % (m[0], m[1]))
            else:
                print('<tr><td>%s' % (m[1]))
                
            try:
                print('<td>%s' % (a1[1]))
            except IndexError:
                print('<td>0')
            try:
                print('<td>%s' % (a2[1]))
            except IndexError:
                print('<td>0')
            try:
                print('<td>%s' % (a3[1]))
            except IndexError:
                print('<td>0')

            print('</tr>')
        else:
            pass
print('</table></div>')
print('</div>')

base.bottom()
