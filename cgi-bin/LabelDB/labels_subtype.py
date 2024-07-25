#!/usr/bin/python3

import cgi
import cgitb; cgitb.enable()
import base
from get_labels import get_labels
from connect import connect
import numpy as np
import sys

sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

print("content-type: text/html\n\n")
base.header(title="Labels by Subtype")
base.top()

db = connect(0)
cur = db.cursor()
   
form = cgi.FieldStorage()

# Get subtype id to grab all labels
m = form.getvalue('major_code')
sub_name = form.getvalue('sub_code')
sub_name = sub_name.replace('_', ' ')

# gets the inputted major type and subtype
major = la.getMajorType(m)

temp_subtypes = major.getAllSubtypes()
subtypes = []
for st in temp_subtypes:
    temp = major.getSubtypeByCode(st)
    if sub_name == major.name:
        subtypes.append(temp)
    else:
        if temp.name == sub_name:
            subtypes.append(temp)


cur.execute('select major_type_id from Major_Type where major_code="%s"' % m)
major_type_id = cur.fetchall()[0][0]

cur.execute('select sub_type_id from Major_Sub_Stitch where major_type_id="%s"' % major_type_id)
db_subtypes = []
for i in cur.fetchall():
    db_subtypes.append(i[0])

try:
    sub_type_ids = []
    for sub in subtypes:
        cur.execute('select sub_type_id from Sub_Type where sub_code="%s"' % (sub.code))
        temp = cur.fetchall()[0][0]
        if temp in db_subtypes: 
            sub_type_ids.append(temp)

    labels = get_labels(major_type_id, sub_type_ids)
except Exception as e:
    labels = []

print('<div class = "row">')
print('<div class = "col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2> Labels for {}: {}</h2>'.format(major.name, sub_name))
print('</div>')
print('</div>')

schema = subtypes[0].serial_schema

print('<div class="row">')
print('<div class="col-md-10 mx-2 my-2 pt-4 ps-5"><h4>Serial Schema</h4><table class="table table-bordered table-hover table-active">')
print('<tr><th> Field Name <th> Description <th> Characters <th> Possible Values</tr>')
names = []
widths = []
descs = []
vals = {}
for field in schema.parts:
    # checks whether the part of the serial schema is a mapping field or a numeric field
    if isinstance(field,la.serial_schema.MappingField):
        names.append(field.name)
        widths.append(field.width)
        descs.append(field.description)
        values = field.getValueOptions()
        temp = []
        keys = []
        # some labels have multiple characters encoding the same thing
        # this is necessary for bijectivity when encoding and decoding labels
        # this determines whether the label type is one of those or not
        bij_excpt = False
        for k,v in field.mapping.items():
            # if there's parentheses, it grabs the value that preceeds them
            if '(' in v:
                x = v.split('(')
                temp.append(x[0][:-1])
                bij_excpt = True
            # otherwise the entire string is the value
            else:
                keys.append(k)
                temp.append(v)

        # sets up a string with the serial schema
        text = ''
        if bij_excpt == True:
            # gets a range of values that could correspond to the possible value
            options = np.unique(temp).tolist()
            opt_dict = {}
            for o in options:
                temp = []
                for v in values:
                    if o in v.value:
                        temp.append(v.value.split('(')[1][0])
                opt_dict[o] = temp[0] + '-' + temp[-1]

            for d in opt_dict:
                text += d + ': ' + opt_dict[d]
                if d is not list(opt_dict)[-1]:
                    text += '<br>'

        # otherwise just lists the character that corresponds to the value
        else:
            options = temp
            for i in range(len(options)):
                text += options[i] + ': ' + keys[i]
                if i != len(options)-1:
                    text += '<br>'
                
                    
        vals[field.name] = text

    if isinstance(field,la.serial_schema.NumericField):
        names.append(field.name)
        widths.append(field.width)
        descs.append(field.description)
        values = field.getValueOptions()
                
        # gets range of values that the numeric field could take on
        vals[field.name] = str(0) + '-' + str(len(values)-1)
        

for i in range(len(names)):
    print('<tr>')
    print(f"<td>{names[i]}</td><td>{descs[i]}</td><td>{widths[i]}</td><td>{vals[names[i]]}</td>")
    print('</tr>')

print('</table>')

# color codes the different parts of the serial number
print('<h5>')
print('<a style="color:black;">CMS Code</a>')
print('<a style="color:maroon;">Major Type</a>')
print('<a style="color:green;">Sub Type</a>')

id_string = ''
id_string += '<a style="color:black;">320</a>'
id_string += '<a style="color:maroon;">%s</a>' % m
id_string += '<a style="color:green;">%s</a>' % subtypes[0].code

colors = ('purple', '#e67e22', 'teal', 'navy')

for i in range(len(names)):
    print('<a style="color:%s;">%s</a>' % (colors[i], names[i]))
    id_string += '<a style="color:%s;">%s</a>' % (colors[i], '0' * widths[i])

print('</h5>')
print('<h5>')
print(id_string)
print('</h5>')
print('</div>')
print('</div>')

# prints all labels made for this subtype
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
    print("<h5>No labels created for this specific subtype</h5>")
 
print('''
    </ul>
    </div>
</div>
''')

base.bottom()

     
