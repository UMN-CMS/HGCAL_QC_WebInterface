#!./cgi_runner.sh

from connect import connect
import cgi, html
import cgitb; cgitb.enable()
import base
import home_page_list
import add_test_functions

def board_checkout_form_sn(full):
    db = connect(0)
    cur = db.cursor()

    # creates a form that sends the information to board_checkout2.py on submitting
    print('<form action="board_checkout2.py" method="post" enctype="multipart/form-data">')
    print("<div class='row'>")
    print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
    print('<h2>Board Checkout</h2>')
    print("</div>")
    print("</div>")

    print('<input type="hidden" name="webpage" value="True">')

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label for="sn">Full ID</label>')
    print('<input type="text" name="full_id" value="%s">'%full)
    print("</div>")

    # creates a form to select the person checking the board out
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
    print('<div class="col-md-9 pt-2 ps-5 mx-2 my-2">')
    print('<label>Location</label><p>')
    print('<textarea rows="1" cols="20" name="location"></textarea>')
    print('</div>')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print("<label for='password'>Admin Password</label>")
    print("<input type='password' name='password'>")
    print("</div>")
    print("</div>")

    print("<div class='row'>")
    print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    # submits the form on click
    print('<input type="submit" class="btn btn-dark" value="Checkout">')
    print("</div>")
    print("</div>")
    print("<div class='row pt-4'>")
    print("</div>")
    print("</form>")

def board_checkout(board_id, person_id, comments, location=None):
    db = connect(1)
    cur = db.cursor()
    board_location = location if location else comments

    print("BOARD_ID", board_id)
    print("PERSON_ID", person_id)
    print("COMMENTS:", comments) 
    try:
        cur.execute('select checkin_id from Check_In where board_id=%s' % board_id)
        checkin_id = cur.fetchall()[0][0]
        print(checkin_id)
      
        sql = "SELECT checkin_id, person_id FROM Check_Out WHERE checkin_id = %s AND board_id = %s" % (checkin_id, board_id)
        cur.execute(sql)
        checkouts = cur.fetchall()
        if checkouts:
            sql = "UPDATE Check_Out SET comment='%s', person_id=%s, checkout_date=NOW() WHERE checkin_id=%s AND board_id=%s" % (comments, person_id, checkin_id, board_id)
            cur.execute(sql)
            sql = "UPDATE Board SET location='%s' WHERE board_id=%i" % (board_location, board_id)
            cur.execute(sql)
            db.commit()
            print('Updated')

        else:
            sql = "INSERT INTO Check_Out (checkin_id, board_id, person_id, comment, checkout_date) VALUES (%s, %s, %s, '%s', NOW())" % (checkin_id, board_id, person_id, comments)        
            cur.execute(sql)

            sql = "UPDATE Board SET location='%s' WHERE board_id=%i" % (board_location, board_id)
           
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
    

def board_checkin_form_sn(full):
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
    print('<label for="sn">Full ID</label>')
    print('<input type="text" name="full_id" value="%s">'%full)
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

        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please ensure all fields are filled. </h3>')
        print('</div>')
        print('</div>')
