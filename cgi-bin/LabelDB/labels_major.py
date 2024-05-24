#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base

from connect import connect

db = connect(0)
cur = db.cursor()
   
form = cgi.FieldStorage()

# Get subtype id to grab all labels
m = form.getvalue('major_type_id')

print("content-type: text/html\n\n")
base.header(title="Labels by Major Type")
base.top()

cur.execute('select name from Major_Type where major_type_id=%s' % m)
maj_name = cur.fetchall()[0][0]

cur.execute('select major_code from Major_Type where major_type_id=%s' % m)
maj_code = cur.fetchall()[0][0]

print('<div class = "row">')
print('<div class = "col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2> Labels for {}</h2>'.format(maj_name))
print('</div>')
print('</div>')

print('<div class="row">')
print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
print('<tr><th> Name <th> Code <th>Total Labels Made<th>Total Boards with Labels</tr>')

cur.execute('select sub_type_id from Major_Sub_Stitch where major_type_id=%s' % m)
sub_types = cur.fetchall()

query = 'select sub_type_id, sub_code from Sub_Type where '
for s in sub_types:
    query += 'sub_type_id={}'.format(s[0])
    if s is not sub_types[-1]:
        query += ' or '
query += ' order by sub_code'
cur.execute(query)

for s in cur.fetchall():
        cur.execute('select sub_code, name, identifier_name from Sub_Type where sub_type_id=%s' % s[0])
        a0 = cur.fetchall()[0]
        cur.execute('select label_id,count(*) from Label where sub_type_id=%s and major_type_id=%s' % (s[0],m))
        a1 = cur.fetchall()[0]
        cur.execute('select full_label,count(DISTINCT Label.full_label) from Label where sub_type_id=%s and major_type_id=%s' % (s[0],m))
        a3 = cur.fetchall()[0]

        print('<tr><td><a href="./labels_subtype.py?major_type_id=%s&sub_type_id=%s">%s</a></td>' % (m, s[0], a0[1]))
        
        code = maj_code + a0[0] 
        print('<td>%s' % code)
        try:
            print('<td>%s' % (a1[1]))
        except IndexError as e: 
            print('<td> %s' % e)
        try:
            print('<td>%s' % (a3[1]))
        except IndexError:
            print('<td>0')

        print('</tr>')
print('</table></div>')
print('</div>')

base.bottom()

     
