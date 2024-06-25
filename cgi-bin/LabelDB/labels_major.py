#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
import label_authority as la
import numpy as np

from connect import connect

db = connect(0)
cur = db.cursor()
   
form = cgi.FieldStorage()

m = form.getvalue('major_code')
# gets MajorType object
major = la.getMajorType(m)

# gets major type id
cur.execute('select major_type_id from Major_Type where major_code="%s"' % m)
major_id = cur.fetchall()[0][0]

# gets all the subtypes for the major type from the database
cur.execute('select sub_type_id from Major_Sub_Stitch where major_type_id="%s"' % major_id)
db_subtypes = []
for i in cur.fetchall():
    db_subtypes.append(i[0])

print("content-type: text/html\n\n")
base.header(title="Labels by Major Type")
base.top()

print('<div class = "row">')
print('<div class = "col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2> Labels for {}</h2>'.format(str(major.name + ' (' + m + ')')))
print('</div>')
print('</div>')

print('<div class="row">')
print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
print('<tr><th> Subtype Name <th> Code <th>Total Labels Made<th>Total Boards with Labels</tr>')

# gets all the subtypes for this major type
subtypes = major.getAllSubtypes()
codes_dict = {}

# makes a dictionary assigning an array of codes to each subtype name
# this is nice because sometimes there are multiple codes that all mean the same thing
for s in subtypes:
    sub = major.getSubtypeByCode(s)
    codes_dict[sub.name] = []

for s in subtypes:
    sub = major.getSubtypeByCode(s)
    codes_dict[sub.name].append(s)

for name,codes in codes_dict.items():

    # makes a string with all the subtype codes
    s = ''
    for c in codes:
        s += c
        if c is not codes[-1]:
            s += ', '
    
        # gets all the subtype ids from the sub codes for this subtype
        query = 'select sub_type_id from Sub_Type where '
        for c in codes:
            query += 'sub_code="%s"' % c
            if c is not codes[-1]:
                query += ' or '
        cur.execute(query)
        sub_ids = cur.fetchall()

        count1 = 0
        count2 = 0
        for sub_id in sub_ids:
            # checks that the subtype id is valid for this major type before getting label counts
            if sub_id[0] in db_subtypes:
                cur.execute('select label_id,count(*) from Label where sub_type_id=%s and major_type_id=%s' % (sub_id[0], major_id))
                a1 = cur.fetchall()[0][1]
                count1 += a1
                cur.execute('select full_label,count(DISTINCT Label.full_label) from Label where sub_type_id=%s and major_type_id=%s' % (sub_id[0], major_id))
                a3 = cur.fetchall()[0][1]
                count2 += a3

    url = name.replace(' ', '_')
    # prints out row with information
    print('<tr><td><a href="./labels_subtype.py?major_code=%s&sub_code=%s">%s</a></td>' % (m, url, name))
    
    print('<td>%s' % str(s))
    print('<td>%s' % count1)
    print('<td>%s' % count2)

    print('</tr>')

print('</table></div>')
print('</div>')

base.bottom()

     
