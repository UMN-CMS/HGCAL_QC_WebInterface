#!/usr/bin/python3

import cgi
import base
import home_page_list
import module_functions
from connect import connect
import pandas as pd
import numpy as np
 
if __name__ == '__main__':
    #cgi header
    print("Content-type: text/html\n")

    # gets serial number and board_id
    form = cgi.FieldStorage()
    serial_num = form.getvalue('serial_num')
    base.header(title='Wagon DB')
    base.top(False)

    db = connect(0)
    cur = db.cursor()
    cur.execute('select board_id from Board where full_id="%s"' % serial_num)
    board_id = cur.fetchall()[0][0]
    # adds the top row with header and buttons
    module_functions.add_test_tab(serial_num, board_id, False)


    # gets revoked tests
    revokes=module_functions.Portage_fetch_revokes(serial_num)

    # adds info table and images
    module_functions.board_info(serial_num, False)

    # gets all test types
    cur.execute('select test_type, name from Test_Type where required = 1 order by relative_order ASC')
    test_types = cur.fetchall()
    # iterates over test types and displays each test done on the board sorted by test
    for t in test_types:
        module_functions.ePortageTest(t[0], serial_num, t[1], revokes, False)

    base.bottom(False)

def run(serial_num, board_id):
    # gets serial number and board_id
    base.header(title='Wagon DB')
    base.top(True)

    # adds the top row with header and buttons
    module_functions.add_test_tab(serial_num, board_id, True)

    db = connect(0)
    cur = db.cursor()

    # gets revoked tests
    revokes=module_functions.Portage_fetch_revokes(serial_num)

    # adds info table and images
    module_functions.board_info(serial_num, True)

    # gets all test types
    cur.execute('select test_type, name from Test_Type where required = 1 order by relative_order ASC')
    test_types = cur.fetchall()
    # iterates over test types and displays each test done on the board sorted by test
    for t in test_types:
        module_functions.ePortageTest(t[0], serial_num, t[1], revokes, True)

    base.bottom(True)
