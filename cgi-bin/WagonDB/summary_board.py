#!/usr/bin/python3

import cgi
import base
from connect import connect
from summary_functions import get
import module_functions
import sys
import numpy as np

if __name__ == '__main__':
    #cgi header
    print("Content-type: text/html\n")

    # gets type_id from previous page
    form = cgi.FieldStorage()
    type_id = form.getvalue('type_id')
    base.header(title='Summary')
    base.top(False)

    db = connect(0)
    cur = db.cursor()

    print('<div class="row">')
    print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Test Summary</h2></div>')
    print('<div class="col-md-2 ps-4 pt-4 my-2">')
    print('<a href="summary.py">')
    print('<button type="button" class="btn btn-dark text-light">Back to Subtype List</button>')
    print('</a>')
    print('</div>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> Full ID </th>')
    print('<th> Tests</th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')

    s = type_id

    cur.execute('select full_id from Board where type_id="%s"' % s)
    li = []
    for l in cur.fetchall():
        li.append(l[0])
    serial_numbers = np.unique(li).tolist()

    for sn in serial_numbers:
        # same structure as home page, now with a variable to see if that test has been run
        cur.execute('select name from Test_Type')
        temp = cur.fetchall()
        names = []
        outcomes = []
        run = []
        for t in temp:
            names.append(t[0])
            outcomes.append(False)
            run.append(False)
        print('<tr>')
        cur.execute('select board_id from Board where full_id="%s"' % sn)
        board_id = cur.fetchall()[0][0]
        cur.execute('select test_type_id, successful,day from Test where board_id=%s order by day desc' % board_id)
        temp = cur.fetchall()
        ids = []
        for t in temp:
            if t[0] not in ids:
                run[t[0]] = True
                if t[1] == 1:
                    outcomes[t[0]] = True
            ids.append(t[0])
        
        # only difference is that all tests are printed out
        print('<td> <a href=module.py?board_id=%(id)s&full_id=%(serial)s> %(serial)s </a></td>' %{'serial':sn, 'id':s})
        print('<td><ul>')
        for idx,o in enumerate(outcomes): 
            # if the test was successful it's printed green 
            if o == True and run[idx] == True:
                print('<li class="list-group-item-success">%s' %names[idx])
            # if test was done and didn't pass, red with a link to add a test of that type
            elif o == False and run[idx] == True:
                print('<li class="list-group-item-danger"> <a href="add_test.py?full_id=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':idx, 'name':names[idx]})
            # if no test has been run, gray with a link
            else:
                print('<li class="list-group-item-dark"> <a href="add_test.py?full_id=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':idx, 'name':names[idx]})
        
        print('</ul></td>') 

        print('</tr>')
    print('</tbody></table></div></div>')


    base.bottom(False)

def run(type_id):
    base.header(title='Summary')
    base.top(True)

    db = connect(0)
    cur = db.cursor()

    print('<div class="row">')
    print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Test Summary</h2></div>')
    print('<div class="col-md-2 ps-4 pt-4 my-2">')
    print('<a href="summary.py">')
    print('<button type="button" class="btn btn-dark text-light">Back to Subtype List</button>')
    print('</a>')
    print('</div>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> Full ID </th>')
    print('<th> Tests</th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')

    s = type_id

    cur.execute('select full_id from Board where type_id="%s"' % s)
    li = []
    for l in cur.fetchall():
        li.append(l[0])
    serial_numbers = np.unique(li).tolist()

    for sn in serial_numbers:
        # same structure as home page, now with a variable to see if that test has been run
        cur.execute('select name from Test_Type')
        temp = cur.fetchall()
        names = []
        outcomes = []
        run = []
        for t in temp:
            names.append(t[0])
            outcomes.append(False)
            run.append(False)
        print('<tr>')
        cur.execute('select board_id from Board where full_id="%s"' % sn)
        board_id = cur.fetchall()[0][0]
        cur.execute('select test_type_id, successful,day from Test where board_id=%s order by day desc' % board_id)
        temp = cur.fetchall()
        ids = []
        for t in temp:
            if t[0] not in ids:
                run[t[0]] = True
                if t[1] == 1:
                    outcomes[t[0]] = True
            ids.append(t[0])
        
        # only difference is that all tests are printed out
        print('<td> <a href=./%(id)s_%(serial)s_module.html> %(serial)s </a></td>' %{'serial':sn, 'id':s})
        print('<td><ul>')
        for idx,o in enumerate(outcomes): 
            # if the test was successful it's printed green 
            if o == True and run[idx] == True:
                print('<li class="list-group-item-success">%s' %names[idx])
            # if test was done and didn't pass, red with a link to add a test of that type
            elif o == False and run[idx] == True:
                print('<li class="list-group-item-danger">%s' %names[idx])
            # if no test has been run, gray with a link
            else:
                print('<li class="list-group-item-dark">%s' %names[idx])
        
        print('</ul></td>') 

        print('</tr>')
    print('</tbody></table></div></div>')


    base.bottom(True)
