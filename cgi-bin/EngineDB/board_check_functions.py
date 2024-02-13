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

    #print("<div class='row'>")
    #print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    #print("<label for='test_type'>Test Type</label>")
    #cur.execute("select test_type, name from Test_Type order by relative_order ASC;")
    #print('<select class="form-control" name="test_type">')
    #for test_type in cur:
    #    print('<option value="%s">%s</option>' % (test_type[0], test_type[1]))
    #print('</select>')
    #print("</div>")
    #print("</div>")

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

def board_checkout(board_id, person_id, comments):
    db = connect(1)
    cur = db.cursor()
   
    try:
        #cur.execute("SELECT board_id FROM Board WHERE '%s' = full_id" % serial_num)
        #board_id = cur.fetchall()[0][0]
        #print(board_id)
        cur.execute('select checkin_id from Check_In where board_id=%s' % board_id)
        checkin_id = cur.fetchall()[0][0]
        print(checkin_id)
      
        sql = "SELECT checkin_id, person_id FROM Check_Out WHERE board_id = %s" % board_id
        cur.execute(sql)
        checkouts = cur.fetchall()
        if checkouts:
            checkout_id = checkouts[-1][0]
            checkout_person = checkouts[-1][1]
            print('Error: This board has already been checked out.')

            #sql = "SELECT Check_In.checkout_id FROM Check_In, Check_Out WHERE Check_In.checkout_id = %s AND Check_Out.checkout_id = %s" % (checkout_id, checkout_id)
            #cur.execute(sql)
            #results = cur.fetchall()
            #if results:
#        else:
#            sql = "INSERT INTO Check_Out (board_id, person_id, comment, checkout_date) VALUES (%s, %s, '%s', NOW())" % (board_id, person_id, comments)        
#            cur.execute(sql)
#
#            db.commit()
#                cur.execute("SELECT People.person_name FROM People WHERE People.person_id = %s" % person_id)
#                tester = cur.fetchone()[0]
#
#                print('<div class ="row">')
#                print('<div class = "col-md-12 pt-4 ps-4 mx-2 my-2">')
#                print('<h3> This board is currently checked out by %s </h3>' % tester)
#                print('</div>')
#                print('</div>')
#
#                print('<div class ="row">')
#                print('<div class="col-md-2 ps-5 pb-3 mx-2 my-2">')
#                print('<a href="board_checkout.py">')
#                print('<button class="btn btn-dark"> Return to Checkout </button>')
#                print('</a>')
#                print('</div>')
#                print('</div>')

        else:
            sql = "INSERT INTO Check_Out (checkin_id, board_id, person_id, comment, checkout_date) VALUES (%s, %s, %s, '%s', NOW())" % (checkin_id, board_id, person_id, comments)        
            cur.execute(sql)

            db.commit()
            
            cur.execute('select checkin_id from Check_Out where board_id=%s' % board_id)
            c_id = cur.fetchall()[0][0]
            print('Begin')
            print(c_id)
            print('End') 

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

    #print("<div class='row'>")
    #print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    #print("<label for='test_type'>Test Type</label>")
    #cur.execute("select test_type, name from Test_Type order by relative_order ASC;")
    #print('<select class="form-control" name="test_type">')
    #for test_type in cur:
    #    print('<option value="%s">%s</option>' % (test_type[0], test_type[1]))
    #print('</select>')
    #print("</div>")
    #print("</div>")

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

def board_checkin(board_id, person_id, comment):
    db = connect(1)
    cur = db.cursor()
   
    try:
        sql = "SELECT checkin_id, person_id FROM Check_In WHERE board_id = %s" % board_id
        cur.execute(sql)
        checkins = cur.fetchall()
        if checkins:
            checkin_id = checkins[-1][0]
            checkin_person = checkins[-1][1]
            print('Error: This board has already been checked in.')
        else:
            sql = "INSERT INTO Check_In (board_id, person_id, comment, checkin_date) VALUES (%s, %s, '%s', NOW())" % (board_id, person_id, comment)        
            cur.execute(sql)

            db.commit()        

            cur.execute('select checkin_id from Check_In where board_id=%s' % board_id)
            c_id = cur.fetchall()[0][0]
            print('Begin')
            print(c_id)
            print('End') 

    except Exception as e:
        print(e)    
        #print(cur.fetchall())

        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please ensure all fields are filled. </h3>')
        print('</div>')
        print('</div>')
