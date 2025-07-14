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

columns = '"Subtype", "Total Checked In", "Awaiting Testing", "QC Passed, Awaiting Registration", "Ready for Shipping", "Shipped", "Failed QC", "Shipped to CERN", "Shipped to Fermilab"'
print(columns)

cur.execute('''
    select B.full_id, B.type_id, B.board_id, BT.name as nickname, BT.type_id as bt_type_id 
    from Board B
    join Board_type BT on B.type_id=BT.type_sn
    order by B.type_id
''')
all_boards = cur.fetchall()

boards_by_type_sn = {}
board_info = {}
for full_id, type_sn, board_id, nickname, bt_type_id in all_boards:
    boards_by_type_sn.setdefault(type_sn, []).append(full_id)
    board_info[full_id] = {
            'board_id': board_id,
            'type_sn': type_sn,
            'bt_type_id': bt_type_id,
            'nickname': nickname,
    }

cur.execute('''
    select T.board_id, T.test_type_id, T.successful
    from Test T
    join (
        select board_id, test_type_id, MAX(test_id) as latest_test_id
        from Test
        group by board_id, test_type_id
    ) latest on T.test_id = latest.latest_test_id
''')

test_results = {}
for board_id, test_type_id, successful in cur.fetchall():
    test_results.setdefault(board_id, {})[test_type_id] = successful

cur.execute('''
    select TTS.type_id, TT.test_type, TT.name
    from Type_test_stitch TTS
    join Test_Type TT on TTS.test_type_id = TT.test_type
''')
stitch_types_by_subtype = {}
for type_id, test_type_id, test_name in cur.fetchall():
    stitch_types_by_subtype.setdefault(type_id, []).append((test_type_id, test_name))

cur.execute('select board_id, comment from Check_Out')
x = cur.fetchall()
shipped_board_ids = set(row[0] for row in x)
locations_by_id = {}
for board_id, comment in x:
    locations_by_id.setdefault(board_id, {})['Location'] = comment

subtypes = []
cur.execute('select type_sn from Board_type where type_sn like "WE%" order by type_sn')
for x in cur.fetchall():
    subtypes.append(x[0])
cur.execute('select type_sn from Board_type where type_sn like "WW%" order by type_sn')
for x in cur.fetchall():
    subtypes.append(x[0])
cur.execute('select type_sn from Board_type where type_sn like "WH%" order by type_sn')
for x in cur.fetchall():
    subtypes.append(x[0])
cur.execute('select type_sn from Board_type where type_sn like "ZP%" order by type_sn')
for x in cur.fetchall():
    subtypes.append(x[0])
for type_sn in subtypes:
    try:
        boards = boards_by_type_sn[type_sn]
    except KeyError:
        print(f'{type_sn}, 0, 0, 0, 0, 0, 0, 0, 0')
        continue

    bt_type_id = board_info[boards[0]]['bt_type_id']
    stitch_types = stitch_types_by_subtype.get(bt_type_id, [])

    fermilab = 0
    cern = 0

    status_map = {}
    for full_id in boards:
        board_id = board_info[full_id]['board_id']
        failed = {}
        outcomes = {}
        for test_type_id, test_name in stitch_types:
            result = test_results.get(board_id, {}).get(test_type_id)
            outcomes[test_name] = result == 1
            failed[test_name] = result == 0

        num_tests_passed = sum(outcomes.values())
        num_tests_req = len(outcomes)
        num_tests_failed = sum(failed.values())

        if board_id in shipped_board_ids:
            status = 'Shipped'
            location = locations_by_id.get(board_id, {})['Location']
            if 'Fermilab' in location or 'FNAL' in location:
                fermilab += 1
            if 'CERN' in location:
                cern += 1

        elif num_tests_failed != 0:
            status = 'Failed'
        elif num_tests_passed == num_tests_req:
            status = 'Passed'
        elif (num_tests_passed == num_tests_req - 1 and not outcomes.get('Registered', False)):
            status = 'Not Registered'
        else:
            status = 'Awaiting'

        status_map[full_id] = status


    awaiting = len([k for k,v in status_map.items() if v == 'Awaiting'])
    not_registered = len([k for k,v in status_map.items() if v == 'Not Registered'])
    passed = len([k for k,v in status_map.items() if v == 'Passed'])
    shipped = len([k for k,v in status_map.items() if v == 'Shipped'])
    failed = len([k for k,v in status_map.items() if v == 'Failed'])
        
    print(f'{type_sn}, {len(boards)}, {awaiting}, {not_registered}, {passed}, {shipped}, {failed}, {cern}, {fermilab}')

