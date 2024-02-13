#!/usr/bin/python3

import cgi
import base
from connect import connect
from summary_functions import get
import module_functions
import sys
import numpy as np

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Board Images')
base.top()

print('<div class="row">')
print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Board Photo Repository</h2></div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-12">')
print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
print('<thead class="table-dark">')
print('<tr>')
print('<th> S/N </th>')
print('<th colspan=2> Top View </th>')
print('<th colspan=2> Bottom View </th>')
print('</tr>')
print('</thead>')
print('<tbody>')

db = connect(0)
cur = db.cursor()

subtypes = []
cur.execute('select board_id from Board')
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
        li.append(l[0])
    serial_numbers[s] = np.unique(li).tolist()

    print('<tr><td colspan=5><a class="btn btn-dark" data-bs-toggle="collapse" href="#col%(id)s">%(id)s</a></td></tr>' %{'id':s})

    print('<tr><td class="hiddenRow" colspan=5>')
    print('<div class="collapse" id="col%s">' %s)
    print('<table>')

    for sn in serial_numbers[s]:
        cur.execute('select board_id from Board where full_id="%s"' % sn)
        board_id = cur.fetchall()[0][0]
        try:
            cur.execute('select image_name,date from Board_images where board_id=%s and view="Top" order by date desc' % board_id)
            name_top = cur.fetchall()[0][0]
            cur.execute('select image_name,date from Board_images where board_id=%s and view="Bottom" order by date desc' % board_id)
            name_bottom = cur.fetchall()[0][0]
            print('<tr>')
            print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(serial)s> %(serial)s </a></td>' %{'serial':sn, 'id':s})
            print('<td colspan=2>')
            print('<a href="../../static/files/wagondb/%(img)s"><img src="../../static/files/wagondb/%(img)s" width=400 height=auto></a>' % {'img':name_top})
            print('</td>') 
            print('<td colspan=2>')
            print('<a href="../../static/files/wagondb/%(img)s"><img src="../../static/files/wagondb/%(img)s" width=400 height=auto></a>' % {'img':name_bottom})
            print('</td>') 
            print('</tr>')
        except:
            print('<tr>')
            print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(serial)s> %(serial)s </a></td>' %{'serial':sn, 'id':s})
            print('<td colspan=4>')
            print('<a>This board has no images.</a>')
            print('</td>') 
            print('</tr>')
            

    print('</table>')
    print('</div>')
    print('</td></tr>')
print('</tbody></table></div></div>')

base.bottom()
