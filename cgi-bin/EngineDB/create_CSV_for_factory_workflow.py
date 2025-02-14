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
print('Content-Disposition: attachment; filename=engine_workflow.csv')
print()

db = connect(0)
cur=db.cursor()

columns = "'Subtype', 'Number Received', 'Number In Progress', 'Number Awaiting Thermal Test', 'Number Awaiting Registration', 'Number Passed and not Shipped', 'Number Shipped', 'Number Failed'"
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
    thermal = 0
    not_registered = 0
    for b in boards:
        failed = {}
        outcomes = {}
        # makes an array of falses the length of the number of tests
        for t in stitch_types:
            outcomes[t] = False
            failed[t] = False

        cur.execute('select board_id from Board where full_id="%s"' % b)
        board_id = cur.fetchall()[0][0]
        cur.execute('select test_type_id, successful from Test where board_id=%s order by day desc, test_id desc' % board_id)
        temp = cur.fetchall()
        ids = []
        for t in temp:
            if t[0] in stitch_types:
                if t[0] not in ids:
                    if t[1] == 1:
                        outcomes[t[0]] = True
                    else:
                        failed[t[0]] = True
                ids.append(t[0])

        num = list(outcomes.values()).count(True)
        total = len(outcomes.values())
        failed_num = list(failed.values()).count(True)

        if num == total:
            t_passed += 1
        else:
            if (num == total-1 and outcomes[24] == False) or (num == total - 2 and outcomes[24] == False and outcomes[26] == False):
                thermal += 1
            elif (num == total-1 and outcomes[26] == False):
                not_registered += 1
        
        if failed_num != 0:
            if (num == total-1 and outcomes[24] == False) or (num == total - 2 and outcomes[24] == False and outcomes[26] == False):
                thermal -= 1
            t_failed += 1

        cur.execute('select board_id from Check_Out where board_id=%s' % board_id)
        checked_out = cur.fetchall()
        if checked_out:
            shipped += 1
            if num != total:
                if (num == total-1 and outcomes[24] == False) or (num == total - 2 and outcomes[24] == False and outcomes[26] == False):
                    thermal -= 1
                elif (num == total-1 and outcomes[26] == False):
                    not_registered -= 1
                if failed_num != 0:
                    t_failed -= 1
            else:
                t_passed -= 1


    awaiting = len(boards) - t_passed - t_failed - thermal - shipped - not_registered
    print("%s, %s, %s, %s, %s, %s, %s, %s" % (s[0], len(boards), awaiting, thermal, not_registered, t_passed, shipped, t_failed))

