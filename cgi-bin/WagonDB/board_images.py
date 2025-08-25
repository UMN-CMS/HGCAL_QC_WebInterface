#!./cgi_runner.sh

import cgi, html
import base
from connect import connect
import module_functions
import sys
import numpy as np

#cgi header
print("Content-type: text/html\n")

base.header(title='Board Images')
base.top()

db = connect(0)
cur = db.cursor()

print('<div class="row">')
print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Board Photo Repository</h2></div>')
print('</div>')

form = cgi.FieldStorage()
if form.getvalue('type_id'):
    type_id = form.getvalue('type_id')

    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> Full ID </th>')
    print('<th colspan=2> Top View </th>')
    print('<th colspan=2> Bottom View </th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')
    
    print('<table>')

    cur.execute('SELECT full_id, board_id FROM Board WHERE type_id="%s" ORDER BY full_id' % type_id)
    for sn, board_id in cur.fetchall():
        print('<tr>')
        print('<td> <a href=module.py?full_id=%(full_id)s> %(full_id)s </a></td>' %{'full_id':sn})
        print('<td colspan=2>')
        print('<img src="get_image.py?board_id=%s&view=%s" width=800 height=auto>' % (board_id, 'Top'))
        print('</td>') 
        print('<td colspan=2>')
        print('<img src="get_image.py?board_id=%s&view=%s" width=800 height=auto>' % (board_id, 'Bottom'))
        print('</td>') 
        print('</tr>')

    print('</table>')
    print('</div>')
    print('</td></tr>')
    print('</tbody></table></div>')


else:
    print('<div class="row">')
    print('<div class="col-md-5 ps-5 mx-2"><h4>Select a Subtype</h4></div>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> LD West Wagons </th>')
    print('<th> LD East Wagons </th>')
    print('<th> HD Wagons </th>')
    print('<th> Zippers </th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')

    # gets all the subtypes and makes a row for each one
    cur.execute('select type_sn, name from Board_type where type_sn like "WE%" order by type_sn')
    east_subtypes = cur.fetchall()

    cur.execute('select type_sn, name from Board_type where type_sn like "WW%" order by type_sn')
    west_subtypes = cur.fetchall()

    cur.execute('select type_sn, name from Board_type where type_sn like "ZP%" order by type_sn')
    zp_subtypes = cur.fetchall()

    cur.execute('select type_sn, name from Board_type where type_sn like "WH%" order by type_sn')
    hd_subtypes = cur.fetchall()


    m = max([len(zp_subtypes), len(west_subtypes), len(east_subtypes), len(hd_subtypes)])

    for s in range(m):
        print('<tr>')
        # links each subtype to it's own page
        print('<td>')
        try:
            print('<a href="board_images.py?type_id=%(id)s">%(id)s, (%(name)s)</a>' %{'id':west_subtypes[s][0], 'name': west_subtypes[s][1]})
        except:
            pass
        print('</td>')
        print('<td>')
        try:
            print('<a href="board_images.py?type_id=%(id)s">%(id)s, (%(name)s)</a>' %{'id':east_subtypes[s][0], 'name': east_subtypes[s][1]})
        except:
            pass
        print('</td>')
        print('<td>')
        try:
            print('<a href="board_images.py?type_id=%(id)s">%(id)s, (%(name)s)</a>' %{'id':hd_subtypes[s][0], 'name': hd_subtypes[s][1]})
        except:
            pass
        print('</td>')
        print('<td>')
        try:
            print('<a href="board_images.py?type_id=%(id)s">%(id)s, (%(name)s)</a>' %{'id':zp_subtypes[s][0], 'name': zp_subtypes[s][1]})
        except:
            pass
        print('</td>')
        print('</tr>')

    print('</tbody>')
    print('</table>')
    print('</div>')
    print('</div>')


print('</div>')

base.bottom()
    
