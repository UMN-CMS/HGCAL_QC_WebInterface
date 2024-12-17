#!./cgi_runner.sh
from connect import connect, connect_admin
#import mysql.connector
import base
import cgi, html, os
import cgitb; cgitb.enable()
import settings
import json


# Adds a new user to the DB
def add_new_user_ID():
    pass



# Returns the JSONs for a specified test ID
def get_test_attachments(test_ID):
    db = connect(0)
    cur = db.cursor()
    
    cur.execute("SELECT attach FROM Attachments,Test WHERE Attachments.test_id=Test.test_id AND Test.test_type_id={};".format(test_ID))

    all_attachments = cur.fetchall()

    decoded_attachments = []
    for attachment in all_attachments:
        decoded_attachments.append(json.loads(attachment[0].decode('UTF-8')))
    
    return decoded_attachments


# Returns the datetime objects for all of the completed tests
    # If issues, check if returning a tuple
def get_test_completion_times():
    db = connect(0)
    cur = db.cursor()
    
    cur.execute("SELECT day FROM Test;")

    all_test_times = cur.fetchall()

    if not all_test_times:
        print("Uh oh... there were no test times to be received")

    return all_test_times


# Returns the datetime objects for all of the successful tests
    # If issues, check if returning a tuple
def get_successful_times():
    
    db = connect(0)
    cur = db.cursor()
    
    cur.execute("SELECT day FROM Test WHERE successful = 1;")
    successful_tests = cur.fetchall()

    if not successful_tests:
        print("Uh oh... there were no successful test times to be received")
    
    return successful_tests


def verify_person(name):
    db = connect(0)
    cur = db.cursor()

    cur.execute("SELECT person_id FROM People WHERE person_name = '%s'"%name)
    people = cur.fetchone()

    if not people:
        print("Could not find tester")
        return "INVALID_TESTER"
    
    else:
        print(people)
        return people


def is_new_board(full_id):
    db = connect(0)
    cur = db.cursor()

    is_new_board_bool = False

    try:
        cur.execute("SELECT board_id FROM Board WHERE full_id = '{}'".format(full_id))
        board_id = cur.fetchone()
        cur.execute('select Checkin_id from Check_In where board_id=%s' % board_id)
        check_in_id = cur.fetchone()

        if not check_in_id:
            is_new_board_bool = True
    except:
        is_new_board_bool = True
        check_in_id = None

    return is_new_board_bool, check_in_id





def get_usernames():
    db = connect(0)
    cur = db.cursor()

    cur.execute("SELECT person_name FROM People")
    people = cur.fetchall()

    if not people:
        print("Could not find any testers")
    
    else:
        return people   


def get_test_completion_status(serial_num):
    db = connect(0)
    cur = db.cursor()

    # TODO
    cur.execute("SELECT board_id FROM Board WHERE full_id = '%s'" % (serial_num))
    board_ID = cur.fetchone()

    if not board_ID:
        return False
    else:
        return True


def get_previous_test_results(serial_num):

    db = connect(0)
    cur = db.cursor()

    cur.execute("SELECT board_id FROM Board WHERE full_id = '{}'".format(serial_num))
    board_id = cur.fetchone()[0]
    cur.execute('select type_id from Board where board_id=%s' % board_id)
    type_sn = cur.fetchall()[0][0]
    cur.execute('select type_id from Board_type where type_sn="%s"' % type_sn)
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT test_type_id, successful FROM Test WHERE board_id = {}".format(board_id))
    test_results_list = cur.fetchall()
    tests_run = []
    outcomes = []
    for i in test_results_list:
        temp = [0,1]
        cur.execute('select name from Test_Type where test_type = %s' % i[0])
        print(test_results_list)
        print(i[0])
        temp[0] = cur.fetchall()[0][0]
        if i[1] == 0:
            temp[1] = 'Failed'
        if i[1] == 1:
            temp[1] = 'Passed'
        tests_run.append(temp[0])
        outcomes.append(temp[1])

    print('Begin1')
    try:
        for i in tests_run:
            print(i)
    except:
        print('None')

    print('End1')

    print('Begin2')
    try:
        for i in outcomes:
            print(i)
    except:
        print('None')

    print('End2')

    print('Begin3')
    try:
        cur.execute('select test_type, name from Test_Type where required=1 order by relative_order ASC')
        test_types = cur.fetchall()
        cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
        temp = cur.fetchall()
        stitch_types = []
        for test in temp:
            stitch_types.append(test[0])

        for t in test_types:
            if t[0] in stitch_types:
                print(t[1])

    except:
        print('None')

    print('End3')

def set_daq_chip_id(sn, test_id):

    db = connect(0)
    cur = db.cursor()

    cur.execute('select Attach from Attachments where test_id=%s' % test_id)
    try:
        attach = cur.fetchall()[0][0]['test_data']
    except KeyError:
        attach = cur.fetchall()[0][0]
    attach = json.loads(attach)
    if sn[3:5] == 'EL':
        daq_chip_id = attach['DAQ'][-1]
    if sn[3:5] == 'EH':
        daq_chip_id = attach['DAQ1'][-1]
    cur.execute('update Board set daq_chip_id="%s" where full_id="%s"' % (daq_chip_id, sn))
    db.commit()


def add_test(person_id, test_type, serial_num, success, comments, config_id):
    if success:
        success = 1
    else:
        success = 0

    db = connect(1)
    cur = db.cursor()

    #cur.execute('select test_type from Test_Type where name="%s"' % test_type)
    #test_type_id = cur.fetchall()[0][0]

    # Expecting that the test_type_id is passed from previous file
    # If issues arrise, check whether the test_type is actually what you expect by printing
    test_type_id = test_type

    if type(person_id) == type(""):
        person_id = verify_person(person_id)

    if serial_num:
        print(serial_num)
        cur.execute("SELECT board_id FROM Board WHERE full_id = '{}'".format(serial_num))
        row = cur.fetchone()
        #print("The Card_ID=", row[0])
        card_id = row[0]
        
        if config_id:
            sql="INSERT INTO Test (person_id, test_type_id, board_id, successful, comments, day, config_id) VALUES (%s,%s,%s,%s,%s,NOW(),%s)"
            # This is safer because Python takes care of escaping any illegal/invalid text
            items=(person_id,test_type_id,card_id,success,comments,config_id)
            cur.execute(sql,items)
            test_id = cur.lastrowid

            print(test_id)

            db.commit()
        else:
            sql="INSERT INTO Test (person_id, test_type_id, board_id, successful, comments, day) VALUES (%s,%s,%s,%s,%s,NOW())"
            # This is safer because Python takes care of escaping any illegal/invalid text
            items=(person_id,test_type_id,card_id,success,comments)
            cur.execute(sql,items)
            test_id = cur.lastrowid

            print(test_id)

            db.commit()

        return test_id

    else:
        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please Specify Testers Name </h3>')
        print('</div>')
        print('</div>')

    # add_test_template(serial_num)


# Adds a tester person
def add_tester(person_name, passwd):
    try:
        db = connect_admin(passwd, 'Engine')
    except Exception as e:
        print(e)
        print("Administrative access denied")
        return
    cur = db.cursor()

    if person_name:
        sql="INSERT INTO People (person_name) VALUES ('%s')"%person_name
        print(sql)
        # This is safer because Python takes care of escaping any illegal/invalid text
        items=(person_name)
        cur.execute(sql)

        print("%s"%(person_name))

        db.commit()

    else:
        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please Specify Full ID </h3>')
        print('</div>')
        print('</div>')

def add_new_test(test_name, required, test_desc_short, test_desc_long, passwd):
    try:
        db = connect_admin(passwd)
    except Exception:
        print("Administrative access denied")
    cur = db.cursor()

    if test_name and required and test_desc_short and test_desc_long:
        sql="INSERT INTO Test_Type (name, required, desc_short, desc_long) VALUES ('%s', '%s', '%s', '%s')"%(test_name, required, test_desc_short, test_desc_long)
        print(sql)
        # This is safer because Python takes care of escaping any illegal/invalid text
        cur.execute(sql)

        db.commit()

    else:
        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please Specify Full ID </h3>')
        print('</div>')
        print('</div>')

def add_init_tests(serial_num, tester, test_results, comments):
    db = connect(1)
    cur = db.cursor()

    if serial_num and tester:
        cur.execute("SELECT board_id FROM Board WHERE full_id = '%s'" %(serial_num))
        row = cur.fetchone()
        card_id = row[0]

        cur.execute("SELECT person_id FROM People WHERE person_name = '%s'" % (tester))
        
        row = cur.fetchone()
        person_id = row[0]
        
        test_ids = []

        for x in test_results.items():
            cur.execute("SELECT test_type FROM Test_Type WHERE name = '%s'" % (x[0]))
            row = cur.fetchone()
            test_type_id = row[0]

            sql="INSERT INTO Test (person_id, test_type_id, board_id, successful, comments, day) VALUES (%s,%s,%s,%s,%s,NOW())"
            items=(person_id,test_type_id,card_id,x[1],comments)
            cur.execute(sql,items)
            test_ids.append(cur.lastrowid)

            db.commit()

        return test_ids       
    else:
        print('<div class ="row">')
        print('<div class = "col-md-3 pt-4 ps-4 mx-2 my-2">')
        print('<h3> Attempt Failed. Please Specify Full ID and Tester </h3>')
        print('</div>')
        print('</div>')

    #add_test_template(serial_num)

def add_test_attachment(test_id, afile, desc, comments):
    print("Adding attachment...")
    if afile.filename:
        db = connect(1)
        cur = db.cursor()
        originalname = os.path.basename(afile.name)

        f = afile.file.read().decode('utf-8')

        cur.execute("INSERT INTO Attachments (test_id,attach,attachmime,attachdesc,comments,originalname) VALUES (%s,%s,%s,%s,%s,%s)",
                    (test_id,f,afile.type,desc,comments,originalname));
        att_id=cur.lastrowid
        db.commit()
        print('<div> The file %s was uploaded successfully. </div>' % (originalname))
    
def add_test_template(serial_number, suggested_test):
    db = connect(0)
    cur = db.cursor()

    print('<form action="add_test2.py" method="post" enctype="multipart/form-data">')
    print('<INPUT TYPE="hidden" name="serial_number" value="%s">' % (serial_number))
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Add Test for Board %s</h2>' %serial_number)
    print('</div>')
    print('</div>')

    #print('<br><br>')
    
    cur.execute("Select person_id, person_name from People;")

    print('<div class="row">')
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Tester')
    print('<select class="form-control" name="person_id">')
    for person_id in cur:
        print("<option value='%s'>%s</option>" % ( person_id[0] , person_id[1] ))
                        
    print('</select>')
    print('</label>')
    print('</div>')
    cur.execute("select test_type, name from Test_Type order by relative_order ASC;")
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Test Type')
    print('<select class="form-control" name="test_type">')
    if suggested_test:
        for test_type in cur:
            if test_type[0] == suggested_test:
                print('<option value="%s">%s</option>' % (test_type[0], test_type[1]))
                break
        for test_type in cur:
            if test_type[0] == suggested_test:
                continue
            print('<option value="%s">%s</option>' % (test_type[0], test_type[1]))
    else:
        for test_type in cur:
            print('<option value="%s">%s</option>' % (test_type[0], test_type[1]))
    print('</select>')
    print('</label>')
    print('</div>')
    print('</div>')
    #print          '<br><br>'

    #print          '<div class = "row">'
    #print              '<div class = "col-md-6">'
    #print                  '<label> Serial Number:'
    #print                      '<input name="serial_number" value="%s">'%serial_number
    #print                  '</label>'
    #print              '</div>'
    #print          '</div>'

    #print('<br><br>')

    print('<div class="row">')
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Successful?')
    print("<input class='form-check-input' type='checkbox' name='success' value='1'>")
    print('</label>')
    print('</div>')
    print('<div class="col-md-9 pt-2 ps-5 mx-2 my-2">')
    print('<label>Comments (Manditory)</label><p>')
    print('<textarea rows="5" cols="50" name="comments"></textarea>')
    print('</div>')
    print('</div>')
                                    
    #print('<br><br>')
    print('<div class="row">')
    print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Add Test">')
    print('</div>')
    print('</div>')
    for iattach in (1,2,3):
        print('<br><hr><br>'    )
        print('<div class="row">')
        print('<div class="col-md-2 pt-2 ps-5 mx-2 my-2">')
        print("<b>Attachment %d:</b>" % (iattach))
        print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
        print("<input type='file' class='form-control' name='attach%d'>"% (iattach)  )
        print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
        print("<label>Description:</label> <INPUT type='text' class='form-control' name='attachdesc%d'>"% (iattach) )
        print('</div>')
        print('</div>')
        print('<div class="row">')
        print('<div class="col-md-10 col-md-offset-2 pt-2 ps-5 mx-2 my-2">')
        print('<label>Comments:</label>')
        print('<textarea rows = "2" cols="50" class="form-control" name="attachcomment%d"></textarea>' % (iattach)  )
        print('</div>')
        print('</div>')

    #print('<br><br><br><br>')

    print('<div class="row">')
    print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Add Test">')
    print('</div>')
    print('</div>')

    #print('<br><br><br><br>')

    print('</form>')

def add_new_test_template():
    print('<form action="add_new_test_template2.py" method="post" enctype="multipart/form-data">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Add New Test Template</h2>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-6 pt-4 ps-5 mx-2 my-2">')
    print('<label>Test Name</label><p>')
    print('<INPUT type="text" class="form-control" name="test_name">')
    print('</div>')

    print('<div class="col-md-3 pt-4 ps-5 mx-2 my-2">')
    print('<label>Required</label>')
    print('<INPUT type="checkbox" class="form-check-input" name="required" value="1">')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-11 pt-2 ps-5 mx-2 my-2">')
    print('<label>Short Test Description</label><p>')
    print('<textarea rows = "2" cols="25" class="form-control" name="test_desc_short"></textarea>')
    print('</div>')
    print('</div>')
    
    print('<div class="row">')
    print('<div class="col-md-11 pt-2 ps-5 mx-2 my-2">')
    print('<label>Long Test Description</label><p>')
    print('<textarea rows = "5" cols="50" class="form-control" name="test_desc_long"></textarea>')
    print('</div>')
    print('</div>')
 
    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print("<label for='password'>Admin Password</label>")
    print("<input type='password' name='password'>")
    print("</div>")
    print("</div>")

    print('<div class="row">')
    print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Submit">')
    print('</div>')
    print('</div>')

    print('</form>')

def add_tester_template():
    print('<form action="add_tester2.py" method="post" enctype="multipart/form-data">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Add New Tester</h2>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-6 pt-4 ps-5 mx-2 my-2">')
    print('<label>Tester Name</label><p>')
    print('<INPUT type="text" class="form-control" name="person_name">')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print("<label for='password'>Admin Password</label>")
    print("<input type='password' name='password'>")
    print("</div>")
    print("</div>")
    
    print("<div class='row'>")
    print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Submit">')
    print('</div>')
    print('</div>')

    print('</form>')
