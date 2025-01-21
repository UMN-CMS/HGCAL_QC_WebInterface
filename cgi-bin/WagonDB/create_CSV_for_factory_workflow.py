#!./cgi_runner.sh

import numpy as np
from connect import connect
import sys
import cgitb
import mysql
import csv
import cgi

form = cgi.FieldStorage()
print('Content-Type: text/plain')
print('Content-Disposition: attachment; filename=wagon_workflow.csv')
print()

db = connect(0)
cur=db.cursor()

columns = "'Subtype', 'Number Received', 'Number In Progress', 'Number Passed and not Shipped', 'Number Shipped', 'Number Failed'"
print(columns)

cur.execute('select distinct type_id from Board order by type_id')
subtypes = cur.fetchall()
for s in subtypes:
    cur.execute('select full_id from Board where type_id="%s"' % s[0])
    boards = cur.fetchall()

    cur.execute('select type_id from Board_type where type_sn="%s"' % s[0])
    type_id = cur.fetchall()[0][0]
    cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
    temp = cur.fetchall()
    stitch_types = []
    for test in temp:
        stitch_types.append(test[0])
    
    t_passed = 0
    t_failed = 0
    shipped = 0
    shipped_without = 0
    for b in boards:
        run = {}
        outcomes = {}
        # makes an array of falses the length of the number of tests
        for t in stitch_types:
            outcomes[t] = False
            run[t] = False

        cur.execute('select board_id from Board where full_id="%s"' % b)
        board_id = cur.fetchall()[0][0]
        cur.execute('select test_type_id, successful, day from Test where board_id=%s order by day desc, test_id desc' % board_id)
        temp = cur.fetchall()
        ids = []
        for t in temp:
            if t[0] not in ids:
                if t[1] == 1:
                    outcomes[t[0]] = True
                else:
                    run[t[0]] = True
            ids.append(t[0])

        num = list(outcomes.values()).count(True)
        total = len(outcomes.values())
        r_num = list(run.values()).count(True)

        if num == total:
            t_passed += 1
        
        if r_num != 0:
            t_failed += 1
        
        cur.execute('select board_id from Check_Out where board_id=%s' % board_id)
        checked_out = cur.fetchall()
        if checked_out:
            if num != total:
                shipped_without += 1
            else:
                shipped += 1

    awaiting = len(boards) - t_passed - t_failed - shipped_without
    print("%s, %s, %s, %s, %s, %s" % (s[0], len(boards), awaiting, (t_passed-shipped), (shipped+shipped_without), t_failed))

