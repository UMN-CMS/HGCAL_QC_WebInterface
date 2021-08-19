#!/usr/bin/python3

from connect import connect
import mysql.connector
import sys

def fetch_list_tests():
    db = connect(0)
    cur=db.cursor()
    cur.execute("select Test_Type.name,COUNT(*),COUNT(DISTINCT Test.board_id) from Test,Test_Type WHERE Test.successful=1 and Test.test_type_id=Test_Type.test_type  GROUP BY Test.test_type_id ORDER BY Test_Type.relative_order");
    rows = cur.fetchall()
    cur.execute("select Test_Type.name,COUNT(*) from Test,Test_Type WHERE Test.test_type_id=Test_Type.test_type  GROUP BY Test.test_type_id ORDER BY Test_Type.relative_order");
    rows2 = cur.fetchall()
    finalrows = ()
    for i in range (0,len(rows)):
        arow=(rows[i][0], rows[i][1],rows[i][2],rows2[i][1])
        finalrows=finalrows+(arow,)
    return finalrows

def render_list_tests():
    rows = fetch_list_tests()
    
    print('<div class="row">')
    print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
    print('<tr><th>Test<th>Total Tests<th>Total Successful Tests<th>Total Wagons with Successful Tests</tr>')
#    print            '<div class="col-md-3"><b>Total Tests</b></div>'
#    print            '<div class="col-md-3"><b>Total Successful Tests</b></div>'
#    print            '<div class="col-md-3"><b>Total Cards with Successful Tests</b></div>'
    for test in rows:
#            print    '<div class="row">'
            print('<tr><td>%s' % (test[0]))
            print('<td>%s' % (test[3]))
            print('<td>%s' % (test[1]))
            print('<td>%s' % (test[2]))
            print('</tr>'            )
    print('</table></div>')

def fetch_list_module():
    db = connect(0)
    cur = db.cursor()

    cur.execute("SELECT sn, Board_id FROM Board ORDER by Board.sn ASC")
    rows = cur.fetchall()
    return rows


def render_list_module():

    row = fetch_list_module()
    n = 0

    col1=''
    col2=''
    col3=''
    if len(sys.argv) == 1: 
        for boards in row:
            temp_col = '<a class="d-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="module.py?board_id=%(id)s&serial_num=%(serial)s"> %(serial)s <span class="badge bg-primary rounded-pill">3</span></a>' %{'serial':boards[0], 'id':boards[1]}
            if n%3 == 0:
                col1 += temp_col
            if n%3 == 1:
                col2 += temp_col
            if n%3 == 2:
                col3 += temp_col
            n += 1
    else:
        for boards in row:
            temp_col = '<a class="d-flex list-group-item list-group-item-action text-decorate-none justify-content-between" href="board_%(serial)s.html"> %(serial)s<span class="badge bg-primary rounded-pill">3</span></a>' %{'serial':boards[0]}
            if n%3 == 0:
                col1 += temp_col
            if n%3 == 1:
                col2 += temp_col
            if n%3 == 2:
                col3 += temp_col
            n += 1   
    print('<div class="d-flex flex-row justify-content-around py-4 my-2">')
    print('<div class="col-md-3">')
    print('<ul class="list-group">')
    print(col1)
    print('</ul></div><div class="col-md-3">')
    print('<div class="list-group">')
    print(col2)
    print('</div></div><div class="col-md-3">')
    print('<div class="list-group">')
    print(col3)
    print('</ul></div></div>')
    print('</div>')

def add_module_form():
    
    print('<form method="post" class="sub-card-form" action="add_module2.py">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Adding a new Test Board</h2>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class = "col-md-3 ps-5 mx-2 my-2">')
    print('<input type="int" name="serial_number" placeholder="Serial Number">')
    print('</div>')
    print('<div class="col-md-1 sub-card-submit">')
    print('<button type="submit" class="btn btn-dark">Submit</button>')
    print('</div>')
    print('</div>')

    print('</form>')

    print('<hr>')


def add_module(serial_number):
    try:
        db = connect(1)
        cur = db.cursor()

        cur.execute("INSERT INTO Board set sn = '%s'; " % (serial_number)) 
        #print '<div> INSERT INTO Card set sn = %s; </div>' %(serial_number)
        db.commit()
        db.close()
    except mysql.connector.Error as err:
       print("<h3>Serial number already exists!</h3>")
    
    
