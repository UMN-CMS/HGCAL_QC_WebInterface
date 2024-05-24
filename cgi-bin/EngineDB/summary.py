#!/usr/bin/python3

import cgi
import base
from connect import connect
from summary_functions import get
import module_functions
import sys
import numpy as np

def run(static):
    base.header(title='Summary')
    base.top(static)

    db = connect(0)
    cur = db.cursor()

    print('<div class="row">')
    print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Test Summary</h2></div>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> Select a Subtype </th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')

    # gets all the subtypes and makes a row for each one
    subtypes = []
    cur.execute('select board_id from Board')
    temp = cur.fetchall()
    for t in temp:
        cur.execute('select type_id from Board where board_id="%s"' % t[0])
        new = cur.fetchall()
        subtypes.append(new[0][0])
    subtypes = np.unique(subtypes).tolist()

    for s in subtypes:
        print('<tr><td>')
        # links each subtype to it's own page
        if static:
            print('<a href="./%(id)s_summary_board.html">%(id)s</a>' %{'id':s})
        else:
            print('<a href="summary_board.py?type_id=%(id)s">%(id)s</a>' %{'id':s})
        print('</td></tr>')

    print('</tbody>')
    print('</table>')
    print('</div>')
    print('</div>')
    print('</div>')

    base.bottom(static)

if __name__ == '__main__':
    #cgi header
    print("Content-type: text/html\n")

    run(False)
