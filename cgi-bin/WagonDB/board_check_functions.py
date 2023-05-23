#!/usr/bin/python3

from connect import connect
import cgi
import cgitb; cgitb.enable()
import base
import home_page_list
import add_test_functions

def board_checkout_form_sn(sn):
    db = connect(0)
    cur = db.cursor()

    print('<form action="board_checkout2.py" method="post" enctype="multipart/form-data">')
    print("<div class='row'>")
    print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
    print('<h2>Board Checkout</h2>')
    print("</div>")
    print("</div>")

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label for="sn">Serial Number</label>')
    print('<input type="text" name="serial_number" value="%s">'%sn)
    print("</div>")

    cur.execute("Select person_id, person_name from People;")

    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Tester')
    print('<select class="form-control" name="person_id">')
    for person_id in cur:
        print("<option value='%s'>%s</option>" % ( person_id[0] , person_id[1] ))
                        
    print('</select>')
    print('</label>')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    print("<label for='test_type'>Test Type</label>")
    cur.execute("select test_type, name from Test_Type order by relative_order ASC;")
    print('<select class="form-control" name="test_type">')
    for test_type in cur:
        print('<option value="%s">%s</option>' % (test_type[0], test_type[1]))
    print('</select>')
    print("</div>")
    print("</div>")

    print("<div class='row'>")
    print('<div class="col-md-9 pt-2 ps-5 mx-2 my-2">')
    print('<label>Comments</label><p>')
    print('<textarea rows="5" cols="50" name="comments"></textarea>')
    print('</div>')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Checkout">')
    print("</div>")
    print("</div>")
    print("<div class='row pt-4'>")
    print("</div>")
    print("</form>")

def board_checkout(serial_num, person_id, test_type, comments):
    db = connect(1)
    cur = db.cursor()
   
    try:
        cur.execute("SELECT sn FROM Board WHERE '%s' = full_id" % serial_num)
        board_id = cur.fetchone()[0]
      
        sql = "SELECT checkout_id, person_id FROM Check_Out WHERE board_id = %s" % board_id
        cur.execute(sql)
        checkouts = cur.fetchall()
        if checkouts:
            checkout_id = checkouts[-1][0]
            checkout_person = checkouts[-1][1]
            sql = "SELECT Check_In.checkout_id FROM Check_In, Check_Out WHERE Check_In.checkout_id = %s AND Check_Out.checkout_id = %s" % (checkout_id, checkout_id)
            cur.execute(sql)
            results = cur.fetchall()
            if results:
                sql = "INSERT INTO Check_Out (board_id, test_type, person_id, comment, checkout_date) VALUES (%s, %s, %s, '%s', NOW())" % (board_id, test_type, person_id, comments)        
                cur.execute(sql)

                db.commit()
            else:
                cur.execute("SELECT People.person_name FROM People WHERE People.person_id = %s" % person_id)
                tester = cur.fetchone()[0]

                print('<div class ="row">')
                print('<div class = "col-md-12 pt-4 ps-4 mx-2 my-2">')
                print('<h3> This board is currently checked out by %s </h3>' % tester)
                print('</div>')
                print('</div>')

                print('<div class ="row">')
                print('<div class="col-md-2 ps-5 pb-3 mx-2 my-2">')
                print('<a href="board_checkout.py">')
                print('<button class="btn btn-dark"> Return to Checkout </button>')
                print('</a>')
                print('</div>')
                print('</div>')
        else:
                sql = "INSERT INTO Check_Out (board_id, test_type, person_id, comment, checkout_date) VALUES (%s, %s, %s, '%s', NOW())" % (board_id, test_type, person_id, comments)        
                cur.execute(sql)

                db.commit()
            

    except Exception as e:
        print(e)    

        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please ensure all fields are filled. </h3>')
        print('</div>')
        print('</div>')
    

def board_checkin_form_sn(sn):
    db = connect(0)
    cur = db.cursor()

    print('<form action="board_checkin2.py" method="post" enctype="multipart/form-data">')
    print("<div class='row'>")
    print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
    print('<h2>Board Checkin</h2>')
    print("</div>")
    print("</div>")

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label for="sn">Serial Number</label>')
    print('<select class="form-control" name="board_id">')
    if sn == "":
        cur.execute("SELECT board_id FROM Check_Out WHERE NOT EXISTS (SELECT * FROM Check_In WHERE Check_Out.checkout_id = Check_In.checkout_id)")
        print(cur)
        try:
            board_ids = cur.fetchall()
            board_ids[0]

        except Exception as e:
            print('<option value="-1">No boards checked out</option>')

        last = None
        for board_id in board_ids:
            sql = "SELECT full_id FROM Board WHERE board_id = '%s'" % board_id[0]
            cur.execute(sql)
            full_id = cur.fetchall()[0][0]
            if full_id == last:
                continue
            print('<option value="%s">%s</option>' % (board_id[0], full_id))
            last = full_id
    else:
        cur.execute("SELECT full_id FROM Board where board_id = %s" % sn)
        full_id = cur.fetchall()[0][0]
        print('<option value="%s">%s</option>' % (sn, full_id))
    print('</select>')
    print("</div>")
    print("</div>")

    print("<div class='row'>")
    print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" "value="Check In">')
    print("</div>")
    print("</div>")
    print("<div class='row pt-4'>")
    print("</div>")
    print("</form>")

def board_checkin(board_id):
    db = connect(1)
    cur = db.cursor()
   
    try:
        cur.execute("SELECT checkout_id FROM Check_Out WHERE board_id = %s" % board_id)
        checkout_id = cur.fetchall()[0]

        sql = "INSERT INTO Check_In (checkout_id, checkin_date) VALUES (%s, NOW())" % (checkout_id)        
        cur.execute(sql)

        db.commit()        

    except Exception as e:
        print(e)    
        print(cur.fetchall())

        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please ensure all fields are filled. </h3>')
        print('</div>')
        print('</div>')
