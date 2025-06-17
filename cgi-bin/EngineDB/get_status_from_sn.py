#!./cgi_runner.sh

import numpy as np
from connect import connect
import sys
import cgitb
import cgi
import base

cgitb.enable()
db = connect(0)
cur=db.cursor()

base.header('')
base.top()

form = cgi.FieldStorage()

full_id = form.getvalue('full_id')

cur.execute('''
    select board_id
    from Board
    where full_id="%s"
''' % full_id)
board_id = cur.fetchall()[0][0]

cur.execute('''
    select T.board_id, T.test_type_id, T.successful
    from Test T
    join (
        select board_id, test_type_id, MAX(test_id) as latest_test_id
        from Test
        group by board_id, test_type_id
    ) latest on T.test_id = latest.latest_test_id
    where T.board_id=%s
''' % board_id)

test_results = {}
for board_id, test_type_id, successful in cur.fetchall():
    test_results.setdefault(board_id, {})[test_type_id] = successful

cur.execute('''
    select BT.type_sn, TT.test_type, TT.name
    from Type_test_stitch TTS
    join Test_Type TT on TTS.test_type_id = TT.test_type
    join Board_type BT on BT.type_id = TTS.type_id
''')
stitch_types_by_subtype = {}
for type_id, test_type_id, test_name in cur.fetchall():
    stitch_types_by_subtype.setdefault(type_id, []).append((test_type_id, test_name))

cur.execute('select board_id from Check_Out')
shipped_board_ids = set(row[0] for row in cur.fetchall())

stitch_types = stitch_types_by_subtype.get(full_id[3:9], [])

failed = {}
outcomes = {}
for test_type_id, test_name in stitch_types:
    result = test_results.get(board_id, {}).get(test_type_id)
    outcomes[test_name] = result == 1
    failed[test_name] = result == 0

num_tests_passed = sum(outcomes.values())
num_tests_req = len(outcomes)
num_tests_failed = sum(failed.values())

print('Begin')

if board_id in shipped_board_ids:
    print('Shipped')
elif num_tests_failed != 0:
    print('Failed')
elif num_tests_passed == num_tests_req:
    print('Passed')
elif (
    outcomes.get('Thermal Cycle') is False and 
    sum(v for k,v in outcomes.items() if k != 'Thermal Cycle' and k != 'Registered') == num_tests_req - 2
):
    print('Thermal')
elif (num_tests_passed == num_tests_req - 1 and not outcomes.get('Registered', False)):
    print('Not Registered')
else:
    print('Awaiting')

print('End')

base.bottom()
