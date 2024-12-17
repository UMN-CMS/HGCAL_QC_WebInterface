#!./cgi_runner.sh

import cgi
import base
import settings
import os.path
import sys
import json
import connect
import base64
import csv

db=connect.connect(0)
cur=db.cursor()

cur.execute('select board_id, full_id, type_id from Board')
all_boards = cur.fetchall()
good_boards = []

cur.execute('select test_type from Test_Type where name="Registered"')
registered_testid = cur.fetchall()[0][0]

for board in all_boards:
    cur.execute('select test_id from Test where test_type_id=%s and board_id=%s' % (registered_testid, board[0]))
    is_registered = cur.fetchall()
    if is_registered:
        continue

    cur.execute('select type_id from Board_type where type_sn="%s"' % board[2])
    type_id = cur.fetchall()[0][0]

    cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
    temp = cur.fetchall()
    stitch_types = []
    for test in temp:
        # delete this if statement once boards can start passsing the thermal cycle test
        if test[0] == 24:
            continue
        stitch_types.append(test[0])

    outcomes = {}
    for t in stitch_types:
        outcomes[t] = False

    cur.execute('select test_type_id, successful, day from Test where board_id=%s order by day desc, test_id desc' % board[0])
    temp = cur.fetchall()
    ids = []
    for t in temp:
        if t[0] in stitch_types:
            if t[0] not in ids:
                if t[1] == 1:
                    outcomes[t[0]] = True
            ids.append(t[0])

    num = list(outcomes.values()).count(True)
    total = len(outcomes.values())

    if num == total:
        good_boards.append(board[1])


with open("boards_for_registration.csv", 'w') as csv_file:
    columns = ['Serial Number']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    for b in good_boards:
        writer.writerow([b])
