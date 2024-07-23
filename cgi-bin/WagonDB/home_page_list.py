#!/usr/bin/python3

import numpy as np
from connect import connect
import sys
import cgitb
import mysql

cgitb.enable()
db = connect(0)
cur=db.cursor()

def fetch_list_tests():
    # gets the number of successful tests and number of boards with successful tests for each test
    cur.execute("select Test_Type.name,COUNT(DISTINCT Test.test_id),COUNT(DISTINCT Test.board_id) from Test,Test_Type WHERE Test.successful=1 and Test.test_type_id=Test_Type.test_type GROUP BY Test.test_type_id ORDER BY Test_Type.relative_order");
    rows = cur.fetchall()
    # gets total tests done for each test
    cur.execute("select Test_Type.name,COUNT(*) from Test,Test_Type WHERE Test.test_type_id=Test_Type.test_type  GROUP BY Test.test_type_id ORDER BY Test_Type.relative_order");
    rows2 = cur.fetchall()
    # gets revoked tests
    cur.execute("select Test_Type.name,Count(*) from TestRevoke,Test_Type,Test WHERE Test.test_type_id=Test_Type.test_type and Test.successful=1 and Test.test_id=TestRevoke.test_id GROUP BY Test.test_type_id ORDER BY Test_Type.relative_order")
    rows3 = cur.fetchall()
   
    # iterates over test types
    for i,r in enumerate(rows):
        # if there are revoked tests
        if rows3:
            # iterate over revoked tests
            for row in rows3:
                # if the revoked test is the same type of test
                if row[0] == r[0]:
                    # subtract off the number of revoked tests
                    rows[i] = (r[0], r[1]-row[1], r[2])
        else:
            rows[i] = (r[0], r[1], r[2])
    # creates final set of data before returning it
    finalrows = ()
    for i in range (0,len(rows)):
        # returns test type, number of successful tests, number of boards with successful tests, total tests
        arow=(rows[i][0], rows[i][1],rows[i][2],rows2[i][1])
        finalrows=finalrows+(arow,)
    return finalrows

def render_list_tests():
    # gets data for the table
    rows = fetch_list_tests()
    
    print('<div class="row">')
    print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
    print('<tr><th>Test<th>Total Tests<th>Total Successful Tests<th>Total Wagons with Successful Tests</tr>')
    for test in rows:
            print('<tr><td>%s' % (test[0]))
            print('<td>%s' % (test[3]))
            print('<td>%s' % (test[1]))
            print('<td>%s' % (test[2]))
            print('</tr>'            )
    print('</table></div>')

def add_module_form():
    
    # calls add_module2.py and sends it the new serial number
    print('<form method="post" class="sub-card-form" action="add_module2.py">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Adding a new Test Board</h2>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class = "col-md-3 ps-5 mx-2 my-2">')
    print('<input type="int" name="full_id" placeholder="Full ID">')
    print('</div>')
    print('<div class="col-md-1 sub-card-submit">')
    print('<button type="submit" class="btn btn-dark">Submit</button>')
    print('</div>')
    print('</div>')

    print('</form>')

    print('<hr>')

def add_board_info_form(full_id, board_id):
    
    # creates a form for board info and calls add_board_info2.py to submit it
    print('<form method="post" class="sub-card-form" action="add_board_info2.py">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-4 mx-2 my-2">')
    print('<h2>Adding Extra Board Information</h2>')
    print('</div>')
    print('</div>')

    print('<input type="hidden" name="full_id" value="%s">' % full_id)
    print('<input type="hidden" name="board_id" value="%s">' % board_id)
    print('<div class="row">')
    print('<div class = "col-md-10 ps-5 pt-2 mx-2 my-2">')
    print('<input type="text" name="comments" placeholder="Comments">')
    print('</div>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-1 ps-5 pt-2 mx-2 my-2 sub-card-submit">')
    print('<button type="submit" class="btn btn-dark">Submit</button>')
    print('</div>')
    print('</div>')

    print('<div class="row pt-4">')
    print('</div>')
    
    print('</form>')

    print('<hr>')

def add_module(serial_number):
    try:
        db = connect(1)
        cur = db.cursor()
        
        # grabs correct sections of the full id to add it to the database
        if len(serial_number) == 15:
            sn = serial_number[9:15]
            type_id = serial_number[3:9]

            # makes sure serial number doesn't already exist
            cur.execute("SELECT board_id FROM Board WHERE Board.full_id = '%s'" % (serial_number))

            rows = cur.fetchall()

            if not rows:
                cur.execute("INSERT INTO Board (sn, full_id, type_id) VALUES (%s, '%s', '%s'); " % (sn, serial_number, type_id)) 
                #print '<div> INSERT INTO Card set sn = %s; </div>' %(serial_number)
                db.commit()
                db.close()
                return 'Board entered successfully!'
            else:
                print("<h3>Board already exists!<h3>")
                return 'Board already exists!'
        else:
            return 'Barcode is not the correct length.'
    except mysql.connector.Error as err:
        print("<h3>Board already exists!</h3>")
        print(err)
        return 'Failed to enter Board'
    
def allboards(static, major):
    # sorts all the boards by subtype and puts all the serial numbers in a dictionary under their subtype
    subtypes = []
    if major == 'LD':
        cur.execute('select board_id from Board where full_id like "%WW%" or full_id like "%WE%"')
    if major == 'HD':
        cur.execute('select board_id from Board where full_id like "%WH%"')
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
    
    # creates all of the lists
    columns={}
    for s in subtypes:
        columns[s] = []
        cur.execute('select type_id from Board_type where type_sn="%s"' % s)
        type_id = cur.fetchall()[0][0]
        for sn in serial_numbers[s]:
            # determines how many tests there are and which ones have passed
            cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
            temp = cur.fetchall()
            outcomes = {}
            run = {}
            for t in temp:
                # makes an array of falses the length of the number of tests
                outcomes[t[0]] = False
                run[t[0]] = False

            cur.execute('select board_id from Board where full_id="%s"' % sn)
            board_id = cur.fetchall()[0][0]
            cur.execute('select test_type_id, successful, day from Test where board_id=%s order by day desc' % board_id)
            temp = cur.fetchall()
            prev_ids = []
            for t in temp:
                # only uses the most recent of all the tests
                if t[0] not in prev_ids:
                    if t[1] == 1:
                        outcomes[t[0]] = True
                    else:
                        run[t[0]] = True
                prev_ids.append(t[0])

            num = list(outcomes.values()).count(True)
            total = len(outcomes.values())
            r_num = list(run.values()).count(True)
            failed = total - num - r_num
            
            if static:
                if num == total:
                    temp_col = '<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="./%(id)s_%(serial)s_module.html"> %(serial)s <span class="badge bg-success rounded-pill">Done</span></a>' %{'serial':sn, 'id':s}
                else:
                    temp_col = '<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="./%(id)s_%(serial)s_module.html"> %(serial)s <span class="badge bg-success rounded-pill">%(success)s/%(total)s</span><span class="badge bg-danger rounded-pill">%(run)s/%(total)s</span><span class="badge bg-secondary rounded-pill">%(failed)s/%(total)s</span></a>' %{'serial':sn, 'id':s, 'success': num, 'total': total, 'run': r_num, 'failed': failed}
            else:
                if num == total:
                    temp_col = '<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="module.py?board_id=%(id)s&full_id=%(serial)s"> %(serial)s <span class="badge bg-success rounded-pill">Done</span></a>' %{'serial':sn, 'id':board_id}
                else:
                    temp_col = '<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="module.py?board_id=%(id)s&full_id=%(serial)s"> %(serial)s <span class="badge bg-success rounded-pill">%(success)s/%(total)s</span><span class="badge bg-danger rounded-pill">%(run)s/%(total)s</span><span class="badge bg-secondary rounded-pill">%(failed)s/%(total)s</span></a>' %{'serial':sn, 'id':s, 'success': num, 'total': total, 'run': r_num, 'failed': failed}

            columns[s].append(temp_col)

    counter = 0
    print('<div class="row">')
    for s in subtypes:
        counter += 1
        print('<div class="col mx-1">')
        print('<div class="list-group">')
        # subtype header
        print('<a class="d-inline-flex list-group-item list-group-item-action text-decorate-none justify-content-between" data-bs-toggle="collapse" href="#boards%(id)s"><b>%(id)s</b></a>' %{'id':s})
        print('</div>')
        print('<div class="collapse" id="boards%s">' % s)
        print('<div class="list-group">')
        for c in columns[s]:
            print(c)
        print('</div>')
        print('</div></div>')
        if counter == 5:
            counter = 0
            print('</div>')
            print('<div class="row">')
    print('</div>')

