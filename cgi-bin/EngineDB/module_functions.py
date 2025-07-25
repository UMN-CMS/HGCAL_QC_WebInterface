#!./cgi_runner.sh -B
from connect import *
import sys
import mysql.connector
import mysql
import os
from get_attach import save
import home_page_list
import pandas as pd
import numpy as np
import datetime
from datetime import datetime as dt
import uuid
import cgi, html
import json

sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

#SERVER_NAME

db = connect(0)
cur = db.cursor()


def Portage_fetch(test_type_id, board_sn):
    # gets board id from the serial number
    cur.execute('select board_id from Board where full_id="%s"' % board_sn)
    board_id = cur.fetchall()[0][0]
    # gets list of names, keeps duplicates
    cur.execute('select person_id,day from Test where board_id=%(b)s and test_type_id=%(t)s order by day desc, test_id desc' %{'b':board_id, 't':test_type_id})
    person_id = cur.fetchall()
    person_name = []
    for p in person_id:
        # same error with no person id for 0
        if p[0] != 0:
            cur.execute('select person_name from People where person_id="%s"' % p[0])
            person_name.append(cur.fetchall()[0][0])
        else:
            person_name.append('No Name')
    # gets list of datetime strings
    cur.execute('select day from Test where test_type_id=%(t)s and board_id=%(b)s order by day desc, test_id desc' %{'b':board_id, 't':test_type_id})
    date = cur.fetchall()
    # gets list of outcomes
    cur.execute('select successful,day from Test where test_type_id=%(t)s and board_id=%(b)s order by day desc, test_id desc' %{'b':board_id, 't':test_type_id})
    successful = cur.fetchall()
    # gets list of comments
    cur.execute('select comments,day from Test where test_type_id=%(t)s and board_id=%(b)s order by day desc, test_id desc' %{'b':board_id, 't':test_type_id})
    comments = cur.fetchall()
    # gets list of test ids
    cur.execute('select test_id,day from Test where test_type_id=%(t)s and board_id=%(b)s order by day desc, test_id desc' %{'b':board_id, 't':test_type_id})
    test_id = []
    for t in cur.fetchall():
        test_id.append(t[0])
    return person_name, date, successful, comments, test_id

def Portage_fetch_attach(test_id):
    # gets attachment data for the test id
    # orders by attach id in case there's more than 1 attachment
    cur.execute('select attach_id, attachmime, attachdesc, originalname from Attachments where test_id=%s order by attach_id' % test_id)
    return cur.fetchall()

def add_test_tab(barcode, board_id):

    # adds header
    print('<div class="row">')
    print('<div class="col-md-5 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Engine Test Info for %s</h2>' %barcode)
    print('</div>')
    print('</div>')

    decoded = la.decode(barcode)
    major = la.getMajorType(decoded.major_type_code)
    sub = major.getSubtypeByCode(decoded.subtype_code)
    sn = decoded.field_values['SerialNumber'].value
    print('<div class="row">')
    print('<div class="col-md-3 pt-4 ps-5 mx-2 my-2">')
    print('<h4>')
    print('Major Type: %s' % major.name)
    print('</h4>')
    print('</div>')
    print('<div class="col-md-3 pt-4 ps-5 mx-2 my-2">')
    print('<h4>')
    print('Sub Type: %s' % sub.name)
    print('</h4>')
    print('</div>')
    print('<div class="col-md-3 pt-4 ps-5 mx-2 my-2">')
    print('<h4>')
    print('Serial Number: %s' % sn)
    print('</h4>')
    print('</div>')
    print('</div>')
    # adds buttons
    print('<div class="row">')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="add_test.py?board_id=%(id)d&full_id=%(serial)s">' %{'serial':barcode, 'id':board_id})
    print('<button class="btn btn-dark"> Add a New Test </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="add_board_info.py?board_id=%(id)d&full_id=%(serial)s">' %{'serial':barcode, 'id':board_id})
    print('<button class="btn btn-dark"> Add Board Info </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="board_checkout.py?full_id=%(serial)s">' %{'serial':barcode})
    print('<button class="btn btn-dark"> Checkout Board </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="add_board_image.py?board_id=%(id)d&full_id=%(serial)s">' %{'serial':barcode, 'id':board_id})
    print('<button class="btn btn-dark"> Add Board Image </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="change_board_location.py?board_id=%(id)d&full_id=%(serial)s">' %{'serial':barcode, 'id':board_id})
    print('<button class="btn btn-dark"> Update Location </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="board_grade.py?board_id=?board_id=%(id)d&full_id=%(full_id)s">' %{'full_id':barcode, 'id':board_id})
    print('<button class="btn btn-dark"> Grade Board </button>')
    print('</a>')
    print('</div>')
    print('</div>')


def ePortageTest(test_type_id, board_sn, test_name, type_sn):
    # displays test info for each test type, is called for each type individually
    # gets info for test
    person_name, date, successful, comments, test_id = Portage_fetch(test_type_id, board_sn) 
    # separates each test name with a line
    print('<hr>')
    print('<div class="row">')
    print('<div class="col-md-12 px-5 pt-2 mx-2 my-2">')
    print('<h3> %(name)s </h3>' %{ "name":test_name})
    # break before data

    print('<br>')

    # iterates over test ids
    for i in range(len(test_id)):
        n = i+1

        if i == 0:
            print('<table class="table table-bordered table-hover table-active">')
            print('<tbody>')
            print('<tr>')
            print('<th>Name</th>')
            print('<th>Date</th>')
            print('<th colspan=2>Successful?</th>')
            print('</tr>')
            print('<tr>')
            print('<td> %(pname)s </td>' %{ "pname":person_name[i]})
            # the datetime object in the DB is a string, this converts it to a datetime object from string in a nicer format
            print('<td> %(when)s </td>' %{ "when":date[i][0].strftime('%c')})
            # checks if the test was successful
            if successful[i][0] == 1:
                print('<td align=left; class="table-success"> Yes </td>')
                print("<td align=right style='{ background-color: yellow; }' ><a href='revoke_success.py?test_id=%(id)s'>Revoke</a></td>" %{ "id":test_id[i]})

            else:
                print('<td colspan=2; class="table-danger">No</td>')
            print('</tr>')
            print('<tr>')
            print('<td><b>Comments:</b></td>' )
            print('<td colspan=3> %(comm)s </td>' %{ "comm":comments[i][0]})
            print('</tr>')
            # gets attachment(s)
            attachments=Portage_fetch_attach(test_id[i])
            for afile in attachments:
                # links attachment
                print('<tr><td colspan=4>Attachment: <a href="get_attach.py?attach_id=%s">%s</a></tr>' % (afile[0],afile[3]))

            print('</tbody>')
            print('</table>')

            print('</div>')
            print('</div>')

            print('<div class="row">')

            if test_name == 'Eye Opening':
                if type_sn[:2] == 'EH' and type_sn[-2] == 'F':
                    print('<div class="col-md-2 pt-2 my-2">')
                    print('<a href="get_eye_image.py?full_id=%(full_id)s&chip=DAQ1">' %{'full_id':board_sn})
                    print('<button class="btn btn-dark"> Eye Image DAQ1 </button>')
                    print('</a>')
                    print('</div>')
                    
                    print('<div class="col-md-2 pt-2 my-2">')
                    print('<a href="get_eye_image.py?full_id=%(full_id)s&chip=DAQ2">' %{'full_id':board_sn})
                    print('<button class="btn btn-dark"> Eye Image DAQ2 </button>')
                    print('</a>')
                    print('</div>')
                else:
                    print('<div class="col-md-2 px-5 pt-2 mx-2 my-2">')
                    print('<a href="get_eye_image.py?full_id=%(full_id)s&chip=DAQ">' %{'full_id':board_sn})
                    print('<button class="btn btn-dark"> Eye Image </button>')
                    print('</a>')
                    print('</div>')

            if len(test_id) > 1:
                print('<div class="col-md-2 px-5 pt-2 mx-2 my-2">')
                print('<a class="btn btn-dark" role="button" data-bs-toggle="collapse" href="#moretests%s" aria-expanded="false" aria-controls="moretests%s">' % (test_type_id, test_type_id))
                print('Show More Tests')
                print('</a>')
                print('</div>')

                print('<div class="collapse px-5 pt-2 mx-2 my-2" id="moretests%s">' % test_type_id)

        
        if i != 0:
            print('<table class="table table-bordered table-hover table-active">')
            print('<tbody>')
            print('<tr>')
            print('<th>Name</th>')
            print('<th>Date</th>')
            print('<th colspan=2>Successful?</th>')
            print('</tr>')
            print('<tr>')
            print('<td> %(pname)s </td>' %{ "pname":person_name[i]})
            # the datetime object in the DB is a string, this converts it to a datetime object from string in a nicer format
            print('<td> %(when)s </td>' %{ "when":date[i][0].strftime('%c')})
            # checks if the test was successful
            if successful[i][0] == 1:
                print('<td align=left> Yes </td>')
                print("<td align=right style='{ background-color: yellow; }' ><a href='revoke_success.py?test_id=%(id)s'>Revoke</a></td>" %{ "id":test_id[i]})

            else:
                print('<td colspan=2>No</td>')
            print('</tr>')
            print('<tr>')
            print('<td><b>Comments:</b></td>' )
            print('<td colspan=3> %(comm)s </td>' %{ "comm":comments[i][0]})
            print('</tr>')
            # gets attachment(s)
            attachments=Portage_fetch_attach(test_id[i])
            for afile in attachments:
                # links attachment
                print('<tr><td>Attachment: <a href="get_attach.py?attach_id=%s">%s</a><td colspan=2><i>%s</i></tr>' % (afile[0],afile[3],afile[2]))

            print('</tbody>')
            print('</table>')

        if i == len(test_id)-1 and len(test_id) > 1:
            print('</div>')

    print('</div>')
    print('</div>')

def get_sn_from_lpgbt_id(lpgbt_id):

    LD_QUERY = "SELECT full_id FROM Board INNER JOIN Test INNER JOIN Attachments ON Board.board_id=Test.board_id and Test.test_id=Attachments.test_id WHERE JSON_EXTRACT(Attachments.attach, '$.test_data.DAQ.id') = %s"
    HD_QUERY = "SELECT full_id FROM Board INNER JOIN Test INNER JOIN Attachments ON Board.board_id=Test.board_id and Test.test_id=Attachments.test_id WHERE JSON_EXTRACT(Attachments.attach, '$.test_data.DAQ1.id') = %s"

    lpgbt_id_int = str(int(lpgbt_id, 16))

    cur.execute(LD_QUERY % (lpgbt_id_int))
    full_id = cur.fetchall()
    if full_id:
        print(full_id[0][0])
    else:
        cur.execute(HD_QUERY % (lpgbt_id_int))
        full_id = cur.fetchall()
        if full_id:
            print(full_id[0][0])
        else:
            print("Could not find full_id associated with LPGBT ID {}".format(lpgbt_id))

def board_info(sn):
    # gets board id
    cur.execute('select board_id from Board where full_id="%s"' % sn)
    board_id = cur.fetchall()[0][0]
    # gets location info
    cur.execute('select location from Board where board_id=%s' % board_id)
    location = cur.fetchall()[0][0]

    try:
        cur.execute('select LDO from Board where board_id=%s' % board_id)
        ldo = cur.fetchall()[0][0]
    except:
        ldo = 'None'

    # attempts to get the Chip IDs for this Board
    try:
        cur.execute('select test_id,day from Test where test_type_id=22 and board_id=%s order by day desc, test_id desc' % board_id) 
        test_id = cur.fetchall()[0][0]
        cur.execute('select Attach from Attachments where test_id=%s' % test_id)
        attach = cur.fetchall()[0][0]
        try:
            attach = json.loads(attach)['test_data']
        except KeyError:
            attach = json.loads(attach)
        if sn[3:5] == 'EL':
            daq_chip_id = hex(int(attach['DAQ']["id"]))
            east_chip_id = hex(int(attach['E']["id"]))
            west_chip_id = hex(int(attach['W']["id"]))
        if sn[3:5] == 'EH':
            daq1_chip_id = hex(int(attach['DAQ1']["id"]))
            trig1_chip_id = hex(int(attach['TRG1']["id"]))
            trig2_chip_id = hex(int(attach['TRG2']["id"]))
            if sn[7] == 'F':
                daq2_chip_id = hex(int(attach['DAQ2']["id"]))
                trig3_chip_id = hex(int(attach['TRG3']["id"]))
                trig4_chip_id = hex(int(attach['TRG4']["id"]))
    except Exception as e:
        test_id = 'No tests run'
        attach = 'none'
        if sn[3:5] == 'EL':
            daq_chip_id = 'None'
            east_chip_id = 'None'
            west_chip_id = 'None'
        if sn[3:5] == 'EH':
            daq1_chip_id = 'None'
            daq2_chip_id = 'None'
            trig1_chip_id = 'None'
            trig2_chip_id = 'None'
            trig3_chip_id = 'None'
            trig4_chip_id = 'None'
        
    try:
        cur.execute('select comments from Board where board_id=%s' % board_id)
        info_com = cur.fetchall()[0][0]
    except:
        info_com = 'None'

    registered_name = 'Registered'

    #cur.execute('select successful from Test where test_type_id=7 and board_id=%s' % board_id)
    cur.execute('select successful from Test where board_id=%s and test_type_id in (select test_type from Test_Type where name="%s")' % (board_id, registered_name))
    registered = cur.fetchall()
    if registered:
        if registered[0][0] == 1:
            #registered = '<td class="bg-success">&nbsp</td>'
            registered = '<td colspan=1><span class="badge bg-success rounded-pill">Done</span></td>'
        else:
            #registered = '<td class="bg-danger">&nbsp</td>'
            registered = '<td colspan=1><span class="badge bg-danger rounded-pill">Failed</span></td>'
    else:
        registered = '<td>Board has not been registered.</td>'

    # does the same thing as the home page to determine how many tests have passed
    cur.execute('select type_id from Board where board_id=%s' % board_id)
    type_sn = cur.fetchall()[0][0]
    cur.execute('select type_id from Board_type where type_sn="%s"' % type_sn)
    type_id = cur.fetchall()[0][0]
    cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
    names = cur.fetchall()
    names = np.unique(names)
    outcomes = []

    cur.execute('select test_type_id, successful, day from Test where board_id=%s order by day desc, test_id desc' % board_id)
    temp = cur.fetchall()
    ids = []
    run = []
    for t in temp:
        if t[0] not in ids:
            if t[1] == 1:
                outcomes.append(True)
            else:
                outcomes.append(False)
        ids.append(t[0])

    num = outcomes.count(True)
    total = len(names)
 
    # adds info
    print('<div class="col-md-11 pt-2 px-4 mx-2 my-2">')
    print('<table class="table table-bordered table-hover table-active">')
    print('<tbody>')
    print('<tr>')
    print('<th colspan=1>Location</th>')
    if sn[3:5] == 'EL':
        print('<th colspan=1>DAQ Chip ID</th>')
        print('<th colspan=1>East Chip ID</th>')
        print('<th colspan=1>West Chip ID</th>')
    if sn[3:5] == 'EH':
        print('<th colspan=1>DAQ 1 Chip ID</th>')
        if sn[7] == 'F':
            print('<th colspan=1>DAQ 2 Chip ID</th>')

        print('<th colspan=1>Trigger 1 Chip ID</th>')
        print('<th colspan=1>Trigger 2 Chip ID</th>')
    print('<th colspan=2>LDO ID</th>')
    print('<th colspan=1>Testing Status</th>')
    print('</tr>')
    print('<tr>')
    print('<td colspan=1>%s</td>' % location)
    if sn[3:5] == 'EL':
        print('<td colspan=1>%s</td>' % daq_chip_id)
        print('<td colspan=1>%s</td>' % east_chip_id)
        print('<td colspan=1>%s</td>' % west_chip_id)
    if sn[3:5] == 'EH':
        print('<td colspan=1>%s</td>' % daq1_chip_id)
        if sn[7] == 'F':
            print('<td colspan=1>%s</td>' % daq2_chip_id)

        print('<td colspan=1>%s</td>' % trig1_chip_id)
        print('<td colspan=1>%s</td>' % trig2_chip_id)
    print('<td colspan=2>%s</td>' % ldo)
    if num == total:
        print('<td colspan=1><span class="badge bg-success rounded-pill">Done</span></td>')
    else:
        print('<td colspan=1><span class="badge bg-dark rounded-pill">%(success)s/%(total)s</span></td>' %{'success': num, 'total': total})
        
    # gets id of boards that have been checked out
    cur.execute('select board_id from Check_Out')
    temp = cur.fetchall()
    ids = []
    for t in temp:
        ids.append(t[0])
    print('</tr>')
    print('<tr>') 
    if sn[3:5] == 'EL':
        print('<th colspan=2>Comments</th>')
    if sn[3:5] == 'EH':
        if sn[7] == 'F':
            print('<th colspan=1>Comments</th>')
            print('<th colspan=1>Trigger 3 Chip ID</th>')
            print('<th colspan=1>Trigger 4 Chip ID</th>')
        else:
            print('<th colspan=2>Comments</th>')

    print('<th colspan=1>Date Received</th>')
    print('<th colspan=1>Manufacturer</th>')
    print('<th colspan=2>Shipping Status</th>')
    print('<th colspan=1>Registered?</th>')
    print('</tr>')
    print('<tr>')
    if sn[3:5] == 'EL':
        print('<td colspan=2>%s</td>' % info_com)
    if sn[3:5] == 'EH':
        if sn[7] == 'F':
            print('<td colspan=1>%s</td>' % info_com)
            print('<td colspan=1>%s</td>' % trig3_chip_id)
            print('<td colspan=1>%s</td>' % trig4_chip_id)
        else:
            print('<td colspan=2>%s</td>' % info_com)
    # gets check in date
    cur.execute('select checkin_date from Check_In where board_id=%s' % board_id)
    try:
        r_date = cur.fetchall()[0][0]
    except:
        r_date = None
    if r_date:
        print('<td colspan=1>%s</td>' % r_date)
    else:
        print('<td colspan=1>No Receiving Date</td>')  

    cur.execute('select manufacturer_id from Board where board_id=%s' % board_id)
    manuf_id = cur.fetchall()[0][0]
    try:
        cur.execute('select name from Manufacturers where manufacturer_id=%s' % manuf_id)
        manufacturer = cur.fetchall()[0][0]
        print('<td colspan=1>%s</td>' % manufacturer)
    except:
        print('<td colspan=1>No Manufacturer Listed</td>')
        
    # if the board has been checked out, get the check out data
    if board_id in ids:
        cur.execute('select checkout_date,comment from Check_Out where board_id=%s' % board_id)
        checkout = cur.fetchall()[0]
        print('<td>%s</td>' % checkout[1])
        print('<td>%s</td>' % checkout[0])
    else:
        print('<td colspan=2> Board has not been shipped. </td>')

    print(registered)
        
    print('</tr>')
    print('</tbody>')
    print('</table>')

    try:
        print('<h5>Top View:</h5>') 
        print('<img src="get_image.py?board_id=%s&view=%s" width=900 height=auto></a>' % (board_id, 'Top'))
        print('<h5>Bottom View:</h5>')
        print('<img src="get_image.py?board_id=%s&view=%s" width=900 height=auto></a>' % (board_id, 'Bottom'))
    except Exception as e:
        print('<h6>This board has no images.</h6>')

    
    print('</div>')


def add_board_info(board_id, sn, comments, password):
    try:
        db = connect_admin(password)
        cur = db.cursor()

    except mysql.connector.Error as err:
        print("Administrative access denied.")
        return

    cur.execute('update Board set comments="%s" where board_id=%s' % (info, board_id))
    db.commit()

def add_revoke(test_id):
    db = connect(0)
    cur = db.cursor()
    
    # gets the test type and board id for the test being revoked
    cur.execute("SELECT test_type_id, board_id FROM Test WHERE test_id = %s" % test_id)
    test_type_id, board_id = cur.fetchall()[0]
    
    # gets the test type name
    cur.execute("SELECT name FROM Test_Type WHERE test_type = %s" % test_type_id)
    name = cur.fetchall()[0][0]

    # gets the serial number
    cur.execute("Select full_id FROM Board WHERE board_id = %s" % board_id)
    full_id = cur.fetchall()[0][0]

    print('<div class="row">')
    print('<div class="col-md-10 pt-5 ps-5 mx-2 my-2">')
    print('<h2>Revoke %s for Board %s</h2>' % (name, full_id))
    print('</div>')
    print('</div>')

    # form that submits the revoke by running revoke_success2.py on submit
    print('<form action="revoke_success2.py" method="post" enctype="multipart/form-data">')
    print('<input type="hidden" name="test_id" value="%s">' % test_id)
    # gives options for tester
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

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print("<label for='password'>Admin Password</label>")
    print("<input type='password' name='password'>")
    print("</div>")
    print("</div>")

    print('<div class="form-group pt-2 px-5 mx-2 my-2">')
    print('<label for="revokeComments"> Revoke Comments </label>')
    print('<textarea class="form-control" name="revokeComments" rows="3" cols="50"></textarea>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Submit Revoke">')
    print('</form>')

def revoke_success(test_id, comments, person_id):
    # revokes the specified test
    db = connect(1)
    cur = db.cursor()
  
    cur.execute('select board_id, test_type_id from Test where test_id = %s' % test_id)
    x = cur.fetchall()

    cur.execute("insert into Test (person_id, test_type_id, board_id, successful, comments, day) values (%s,%s,%s,%s,%s,NOW())" % (person_id, x[0][1], x[0][0], 0, comments))
    db.commit()

def get_test_types():
    # used in Testing GUI
    db = connect(0)
    cur = db.cursor()

    try:
        cur.execute('SELECT name, test_type FROM Test_Type')

        rows = cur.fetchall()
        tests = [[r[0],r[1]] for r in rows]

        return tests

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)

def add_board_image(sn, img_file, view):
    # writes the image file
    db = connect(1)
    cur = db.cursor() 

    print("Adding board image")

    try: 
        # gets board id
        cur.execute("SELECT board_id FROM Board WHERE full_id = '%s';" % sn)
        rows = cur.fetchall()

        # check if board id exists
        # it will be on Visual Inspection GUI side, new boards are automatically entered when scanned
        if not rows:
            print("Board sn does not exist! Make sure this board has been entered into the database.")

        else:
            board_id = rows[0][0]

        img_path = get_image_location()
        # generates random string for the image name
        img_name = str(uuid.uuid4())

        path = img_path + img_name

        # puts the file name and other info into DB
        cur.execute('INSERT INTO Board_images (board_id, image_name, view, date) VALUES (%s, "%s", "%s", NOW())' % (board_id, img_name, view))

        db.commit()
        db.close()

        print("Attempting to write file...")

        # saves the image file
        with open(path, "wb") as f:
            print("File opened!")
            f.write(img_file)
            print("File wrote:)")

        print("File received successfully!")

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)

def change_board_location(sn, location):

    db = connect(1)
    cur = db.cursor() 

    try: 
        # gets board id
        cur.execute("SELECT board_id FROM Board WHERE full_id = '%s';" % sn)
        rows = cur.fetchall()

        # check if board exists
        if not rows:
            print("Board sn does not exist! Make sure this board has been entered into the database.")

        else:
            board_id = rows[0][0]

        # updates location
        cur.execute('UPDATE Board SET location="%s" WHERE board_id=%i' % (location, board_id))

        db.commit()
        db.close()

        print("Location Updated Successfully!")

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)


