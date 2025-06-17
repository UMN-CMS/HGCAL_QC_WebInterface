#!./cgi_runner.sh

import cgi, html
import base
from connect import connect
import module_functions
import sys
import numpy as np

#cgi header
print("Content-type: text/html\n")

base.header(title='Summary')
base.top()

db = connect(0)
cur = db.cursor()

print('<div class="row">')
print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Board Summary</h2></div>')
print('</div>')
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
east_subtypes = []
cur.execute('select board_id from Board where full_id like "%WE%"')
temp = cur.fetchall()
for t in temp:
    cur.execute('select type_id from Board where board_id="%s"' % t[0])
    new = cur.fetchall()
    east_subtypes.append(new[0][0])
east_subtypes = np.unique(east_subtypes).tolist()

west_subtypes = []
cur.execute('select board_id from Board where full_id like "%WW%"')
temp = cur.fetchall()
for t in temp:
    cur.execute('select type_id from Board where board_id="%s"' % t[0])
    new = cur.fetchall()
    west_subtypes.append(new[0][0])
west_subtypes = np.unique(west_subtypes).tolist()

zp_subtypes = []
cur.execute('select board_id from Board where full_id like "%ZP%"')
temp = cur.fetchall()
for t in temp:
    cur.execute('select type_id from Board where board_id="%s"' % t[0])
    new = cur.fetchall()
    zp_subtypes.append(new[0][0])
zp_subtypes = np.unique(zp_subtypes).tolist()

hd_subtypes = []
cur.execute('select board_id from Board where full_id like "%WH%"')
temp = cur.fetchall()
for t in temp:
    cur.execute('select type_id from Board where board_id="%s"' % t[0])
    new = cur.fetchall()
    hd_subtypes.append(new[0][0])
hd_subtypes = np.unique(hd_subtypes).tolist()

m = max([len(zp_subtypes), len(west_subtypes), len(east_subtypes), len(hd_subtypes)])

for s in range(m):
    print('<tr>')
    # links each subtype to it's own page
    print('<td>')
    try:
        print('<a href="summary_board.py?type_id=%(id)s">%(id)s</a>' %{'id':west_subtypes[s]})
    except:
        pass
    print('</td>')
    print('<td>')
    try:
        print('<a href="summary_board.py?type_id=%(id)s">%(id)s</a>' %{'id':east_subtypes[s]})
    except:
        pass
    print('</td>')
    print('<td>')
    try:
        print('<a href="summary_board.py?type_id=%(id)s">%(id)s</a>' %{'id':hd_subtypes[s]})
    except:
        pass
    print('</td>')
    print('<td>')
    try:
        print('<a href="summary_board.py?type_id=%(id)s">%(id)s</a>' %{'id':zp_subtypes[s]})
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
