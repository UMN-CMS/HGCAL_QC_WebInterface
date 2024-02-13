#!/usr/bin/python3

import sys
import pandas as pd
import csv
import cgitb
import numpy as np
from connect import connect

cgitb.enable()
db = connect(0)
cur = db.cursor()

def renderlist():
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

    columns={}
    for s in subtypes:
        columns[s]=['<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between"><b>%(id)s</b></a>' %{'id':s}]
        for sn in serial_numbers[s]:
            cur.execute('select board_id from Board where full_id="%s"' % sn)
            board_id = cur.fetchall()[0][0]
            cur.execute('select test_type_id, successful from Test where board_id=%s' % board_id)
            temp = cur.fetchall()
            outcomes = [False, False, False, False, False]
            total = 5
            for t in temp:
                if t[1] == 1:
                    if t[0] == 0:
                        outcomes[0] = True
                    if t[0] == 1:
                        outcomes[1] = True
                    if t[0] == 2:
                        outcomes[2] = True
                    if t[0] == 3:
                        outcomes[3] = True
                    if t[0] == 4:
                        outcomes[4] = True
            num = outcomes.count(True)
            
            if num == total:
                temp_col = '<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="module.py?board_id=%(id)s&serial_num=%(serial)s"> %(serial)s <span class="badge bg-success rounded-pill">Done</span></a>' %{'serial':sn, 'id':board_id}
            else:
                temp_col = '<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="module.py?board_id=%(id)s&serial_num=%(serial)s"> %(serial)s <span class="badge bg-primary rounded-pill">%(success)s/%(total)s</span></a>' %{'serial':sn, 'id':board_id, 'success': num, 'total': total}

            columns[s].append(temp_col)

    print('<div class="row overflow-scroll py-4 my-2 mx-4">')
    for s in subtypes:
        print('<div class="col mx-1">')
        print('<div class="list-group">')
        for c in columns[s]:
            print(c)
        print('</div></div>')
    print('</div>')

