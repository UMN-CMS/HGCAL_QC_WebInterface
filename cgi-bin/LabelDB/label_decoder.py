#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import label_authority as la
from get_labels import get_labels
from connect import connect
import numpy as np

print("content-type: text/html\n\n")
base.header(title="Decoded Label")
base.top()

db = connect(0)
cur = db.cursor()

form = cgi.FieldStorage()
sn = form.getvalue('board_id')

print('<div class = "row">')
print('<div class = "col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2> Decoded Label for {}:</h2>'.format(sn))
print('</div>')
print('</div>')

# makes a table with the decoded label information
try:
    decoded = la.decode(sn)
    m = decoded.major_type_code
    major = la.getMajorType(m)
    s = decoded.subtype_code
    sub = major.getSubtypeByCode(s)

    print('<div class="row">')
    print('<div class="col-md-10 mx-2 my-2 pt-4 ps-5">')
    print('<table class="table table-bordered table-hover table-active">')
    print('<tr>')
    print('<th>Prefix</th>')
    print('<th>Major Type</th>')
    print('<th>Subtype</th>')
    for k in decoded.field_values.keys():
        print('<th>%s</th>' % k)
        
    print('</tr>')
    print('<tr>')
    print('<td>320</td>')
    print('<td>%s</td>' % m)
    print('<td>%s</td>' % s)
    for v in decoded.field_values.values():
        if type(v) == str:
            x = v.split('(')
            print('<td>%s</td>' % x[1][0])
        else:
            print('<td>%s</td>' % v)
            
    print('</tr>')
    print('<tr>')
    print('<td>CMS Identification Code</td>')
    print('<td>%s</td>' % major.name)
    print('<td>%s</td>' % sub.name)
    for v in decoded.field_values.values():
        if type(v) == str:
            x = v.split('(')
            print('<td>%s</td>' % x[0])
        else:
            print('<td></td>')
            
    print('</tr>')
    print('</table>')
    print('</div>')
    print('</div>')

except Exception as e:
    print('<div class="row">')
    print('<div class="col-md-10 mx-2 my-2 pt-4 ps-5">')
    print('<h4>Error, Invalid Barcode.</h4>')
    print('<h5>%s</h5>' % e)
    print('</div>')
    print('</div>')

base.bottom()

     
