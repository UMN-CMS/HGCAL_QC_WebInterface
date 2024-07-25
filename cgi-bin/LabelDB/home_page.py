#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import label_functions
import sys
import numpy as np
from connect import connect
import sys

sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

db = connect(0)
cur = db.cursor()

#cgi header
print("content-type: text/html\n\n")

base.header(title='HGCAL Labeling Home Page')
base.top()

print('<div class="row">')
print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
print('<tr><th>Major Type<th>Major Code<th>Total Labels Made<th># of Subtypes<th>Total Boards with Labels</tr>')

# gets all the major types from the label library
major_types = la.getAllMajorTypes()

# m is the major type code, major is a MajorType object
for m, major in major_types.items():
    # gets the major type id
    try:
        cur.execute('select major_type_id from Major_Type where major_code="%s"' % m)
        m_id = cur.fetchall()[0][0]
        # gets the label and subtype counts for each major type
        cur.execute('select label_id,count(*) from Label where major_type_id=%s' % m_id)
        a1 = cur.fetchall()[0]
        cur.execute('select sub_type_id,count(*) from Major_Sub_Stitch where major_type_id=%s' % m_id)
        a2 = cur.fetchall()[0]
        cur.execute('select full_label,count(distinct full_label) from Label where major_type_id=%s' % m_id)
        a3 = cur.fetchall()[0]
    except IndexError:
        a1 = [0,'Not in DB']
        a2 = [0,0]
        a3 = [0,0]


    print('<tr><td><a href="labels_major.py?major_code=%s">%s</a>' % (m, major.name))
    print('<td>%s' % m)
        
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
print('</table></div>')
print('</div>')

# adds a form to decode labels given a full id
print('<div class="row">')
print('<div class="col-md-11 mx-4 my-4">')
print('<h4> Label Decoder</h4>')
print('<h5> Enter Board ID</h5>')

print('<form action="label_decoder.py" method="post" enctype="multipart/form-data">')

print('<div class=">ow">')
print('<input type="text" name="board_id">')
print('<input type="submit" class="btn btn-dark" value="Decode">')
print('</div>')
print('</form>')

print('</div>')
print('</div>')

base.bottom()
