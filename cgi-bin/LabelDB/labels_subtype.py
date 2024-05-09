#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base

from get_labels import get_labels
from connect import connect

def get_header(major_type_id, sub_type_id):

    db = connect(0)
    cur = db.cursor()

    query = "SELECT name FROM Major_Type WHERE major_type_id = %s"
    args = (major_type_id,)

    cur.execute(query, args)
    maj_name = cur.fetchall()[0][0]

    query = "SELECT name FROM Sub_Type WHERE sub_type_id = %s"
    args = (sub_type_id,)

    cur.execute(query, args)
    sub_name = cur.fetchall()[0][0]

    return maj_name, sub_name
   
form = cgi.FieldStorage()

# Get subtype id to grab all labels
major_type_id = form.getvalue('major_type_id')
sub_type_id = form.getvalue('sub_type_id')

maj_name, sub_name = get_header(major_type_id, sub_type_id)
labels = get_labels(major_type_id, sub_type_id)

print("content-type: text/html\n\n")
base.header(title="Labels by Subtype")
base.top()

print('<div class = "row">')
print('<div class = "col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2> Labels for {}: {}</h2>'.format(maj_name, sub_name))
print('</div>')
print('</div>')

print('''
<div class="row">
    <div class="col-md-10 pt-4 ps-5 mx-2 my-2">

''')

if labels != []:
    print('    <ul class="list-group">')
    for label in labels:
        print('<li class="list-group-item">{}</li>'.format(label[0]))

    print('    </ul>')
   
else:
    print("<h3>No labels created for this specific subtype</h3>")
 
print('''
    </ul>
    </div>
</div>
''')

base.bottom()

     
