#!/usr/bin/python3 -B
from connect import connect
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
import cgi
import json

#SERVER_NAME

db = connect(0)
cur = db.cursor()


def Portage_fetch(test_type_id, board_sn):
    cur.execute('select board_id from Board where full_id="%s"' % board_sn)
    board_id = cur.fetchall()[0][0]
    cur.execute('select person_id from Test where board_id=%(b)s and test_type_id=%(t)s' %{'b':board_id, 't':test_type_id})
    person_id = cur.fetchall()
    person_name = []
    for p in person_id:
        cur.execute('select person_name from People where person_id="%s"' % p[0])
        person_name.append(cur.fetchall()[0][0])
    cur.execute('select day from Test where test_type_id=%(t)s and board_id=%(b)s' %{'b':board_id, 't':test_type_id})
    date = cur.fetchall()
    cur.execute('select successful from Test where test_type_id=%(t)s and board_id=%(b)s' %{'b':board_id, 't':test_type_id})
    successful = cur.fetchall()
    cur.execute('select comments from Test where test_type_id=%(t)s and board_id=%(b)s' %{'b':board_id, 't':test_type_id})
    comments = cur.fetchall()
    cur.execute('select test_id from Test where test_type_id=%(t)s and board_id=%(b)s' %{'b':board_id, 't':test_type_id})
    test_id = []
    for t in cur.fetchall():
        test_id.append(t[0])
    return person_name, date, successful, comments, test_id

def Portage_fetch_revokes(sn):
    cur.execute('select board_id from Board where full_id="%s"' % sn)
    board_id = cur.fetchall()[0][0]
    cur.execute('select test_id from Test where board_id=%s' % board_id)
    test_ids = cur.fetchall()
    cur.execute('select test_id from TestRevoke')
    revoked_ids = cur.fetchall()
    revoked={}
    for t in test_ids:
        if t[0] in revoked_ids:
            cur.execute('select comment from TestRevoke where test_id=%s' % t[0])
            revoked[t[0]] =  cur.fetchall()[0][0]
    return revoked


def Portage_fetch_attach(test_id):
    cur.execute('select attach_id, attachmime, attachdesc, originalname from Attachments where test_id=%s order by attach_id' % test_id)
    return cur.fetchall()

def add_test_tab(sn, board_id):

    print('<div class="row">')
    print('<div class="col-md-5 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Wagon Test Info for %s</h2>' %sn)
    print('</div>')
    print('</div>')
    
    print('<div class="row">')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="add_test.py?board_id=%(id)d&serial_num=%(serial)s">' %{'serial':sn, 'id':board_id})
    print('<button class="btn btn-dark"> Add a New Test </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="add_board_info.py?board_id=%(id)d&serial_num=%(serial)s">' %{'serial':sn, 'id':board_id})
    print('<button class="btn btn-dark"> Add Board Info </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="board_checkout.py?serial_num=%(serial)s">' %{'serial':sn})
    print('<button class="btn btn-dark"> Checkout Board </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="board_checkin.py?serial_num=%(serial)s">' %{'serial':sn})
    print('<button class="btn btn-dark"> Checkin Board </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="add_board_image.py?board_id=%(id)d&serial_num=%(serial)s">' %{'serial':sn, 'id':board_id})
    print('<button class="btn btn-dark"> Add Board Image </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 my-2">')
    print('<a href="change_board_location.py?board_id=?board_id=%(id)d&serial_num=%(serial)s">' %{'serial':sn, 'id':board_id})
    print('<button class="btn btn-dark"> Update Location </button>')
    print('</a>')
    print('</div>')
    print('</div>')



def ePortageTest(test_type_id, board_sn, test_name, revokes):
    person_name, date, successful, comments, test_id = Portage_fetch(test_type_id, board_sn) 
    print('<hr>')
    print('<div class="row">')
    print('<div class="col-md-12 px-5 pt-2 mx-2 my-2">')
    print('<h3> %(name)s </h3>' %{ "name":test_name})
    print('<br>')

    for i in range(len(test_id)):
        n = i+1

        print('<h4>Attempt: %d</h4>'%n)
        print('<table class="table table-bordered table-hover table-active">')
        print('<tbody>')
        print('<tr>')
        print('<th>Name</th>')
        print('<th>Date</th>')
        print('<th colspan=2>Successful?</th>')
#        print                          '<th>Comments</th>'
        print('</tr>')
        print('<tr>')
        print('<td> %(pname)s </td>' %{ "pname":person_name[i]})
        print('<td> %(when)s </td>' %{ "when":date[i][0].strftime('%c')})
        if successful[i][0] == 1:
            if test_id[i] in revokes:
                print('<td><b>Revoked</b>: %(comment)s </td>' %{ "comment":revokes[test_id[i]] })
            else:
                print('<td align=left> Yes </td>')
                if len(sys.argv) == 1:
                    print("<td align=right style='{ background-color: yellow; }' ><a href='revoke_success.py?test_id=%(id)s'>Revoke</a></td>" %{ "id":test_id[i]})

        else:
            print('<td colspan=2>No</td>')
        print('</tr>')
        print('<tr>')
        print('<td><b>Comments:</b></td>' )
        print('<td colspan=3> %(comm)s </td>' %{ "comm":comments[i][0]})
        print('</tr>')
        attachments=Portage_fetch_attach(test_id[i])
        for afile in attachments:
            if len(sys.argv) == 1:
                print('<tr><td>Attachment: <a href="get_attach.py?attach_id=%s">%s</a><td colspan=2><i>%s</i></tr>' % (afile[0],afile[3],afile[2]))
            else:
                print('<tr><td>Attachment: <a href="%s.html">%s</a><td colspan=2><i>%s</i></tr>' % (afile[0], afile[3], afile[2]))
                stdout = sys.stdout
                sys.stdout = open("%(loc)s/%(f)s.html" %{'loc':sys.argv[1], 'f':afile[0]},'w')
                save(afile[0])
                sys.stdout.close()
                sys.stdout = stdout

        print('</tbody>')
        print('</table>')
                    
    print('</div>')
    print('</div>')

def board_info(sn):
    cur.execute('select board_id from Board where full_id="%s"' % sn)
    board_id = cur.fetchall()[0][0]
    cur.execute('select location from Board where board_id=%s' % board_id)
    location = cur.fetchall()[0][0]
    try:
        cur.execute('select test_id,day from Test where test_type_id=22 and board_id=%s order by day desc' % board_id) 
        test_id = cur.fetchall()[0][0]
        cur.execute('select Attach from Attachments where test_id=%s' % test_id)
        attach = cur.fetchall()[0][0]
        attach = json.loads(attach)
        daq_chip_id = attach['DAQ'][-1]
        trig1_chip_id = attach['E'][-1]
        trig2_chip_id = attach['W'][-1]
    except:
        daq_chip_id = 'none'
        trig1_chip_id = 'none'
        trig2_chip_id = 'none'
        

    info_com = 'None'

    cur.execute('select name from Test_Type')
    names = cur.fetchall()
    outcomes = []
    for i in range(len(names)):
        outcomes.append(False)

    cur.execute('select test_type_id, successful from Test where board_id=%s' % board_id)
    temp = cur.fetchall()
    for t in temp:
        if t[1] == 1:
            outcomes[t[0]] = True
    num = outcomes.count(True)
    total = len(outcomes)
 
    print('<div class="col-md-11 pt-2 px-4 mx-2 my-2">')
    print('<table class="table table-bordered table-hover table-active">')
    print('<tbody>')
    print('<tr>')
    print('<th colspan=1>Location</th>')
    print('<th colspan=1>DAQ Chip ID</th>')
    print('<th colspan=1>Trigger 1 Chip ID</th>')
    print('<th colspan=1>Trigger 2 Chip ID</th>')
    print('<th colspan=1>Testing Status</th>')
    print('</tr>')
    print('<tr>')
    print('<td colspan=1>%s</td>' % location)
    print('<td colspan=1>%s</td>' % daq_chip_id)
    print('<td colspan=1>%s</td>' % trig1_chip_id)
    print('<td colspan=1>%s</td>' % trig2_chip_id)
    if num == total:
        print('<td colspan=1><span class="badge bg-success rounded-pill">Done</span></td>')
    else:
        print('<td colspan=1><span class="badge bg-primary rounded-pill">%(success)s/%(total)s</span></td>' %{'success': num, 'total': total})
        
    cur.execute('select board_id from Check_Out')
    temp = cur.fetchall()
    ids = []
    for t in temp:
        ids.append(t[0])
    print('</tr>')
    print('<tr>')
    print('<th colspan=2>Comments</th>')
    print('<th colspan=1>Date Received</th>')
    print('<th colspan=2>Status</th>')
    print('</tr>')
    print('<tr>')
    print('<td colspan=2>%s</td>' % info_com)
    cur.execute('select checkin_date from Check_In where board_id=%s' % board_id)
    try:
        r_date = cur.fetchall()[0][0]
    except:
        r_date = None
    if r_date:
        print('<td colspan=1>%s</td>' % r_date)
    else:
        print('<td colspan=1>No Receiving Date</td>')  
        
    if board_id in ids:
        cur.execute('select checkout_date,comment from Check_Out where board_id=%s' % board_id)
        checkout = cur.fetchall()[0]
        print('<td>%s</td>' % checkout[1])
        print('<td>%s</td>' % checkout[0])
    else:
        print('<td colspan=2> Board has not been shipped. </td>')
        
    print('</tr>')
    print('</tbody>')
    print('</table>')

    server_name = os.environ["SERVER_NAME"]

    try:
        cur.execute('select image_name,date from Board_images where board_id=%s and view="Top" order by date desc' % board_id)
        img_name_top = cur.fetchall()[0][0]
        cur.execute('select image_name,date from Board_images where board_id=%s and view="Bottom" order by date desc' % board_id)
        img_name_bottom = cur.fetchall()[0][0]

        print('<h5>Top View:</h5>') 
        print('<a href="http://%(server_name)s/ePortage/wagondb/%(img)s"><img src="http://%(server_name)s/ePortage/wagondb/%(img)s" width=900 height=auto></a>' % {'server_name': server_name, 'img':img_name_top})
        #print('<a href="/home/ePortage/wagondb/image_top"><img src="/home/ePortage/wagondb/image_top" width=900 height=auto></a>')
        print('<h5>Bottom View:</h5>')
        print('<a href="http://%(server_name)s/ePortage/wagondb/%(img)s"><img src="http://%(server_name)s/ePortage/wagondb/%(img)s" width=900 height=auto></a>' % {'server_name': server_name, 'img':img_name_bottom})
        #print('<a href="./static/image_bottom"><img src="./static/image_bottom" width=900 height=auto></a>')
    except Exception as e:
        print('<h6>This board has no image.</h6>')
    
    print('</div>')


def add_board_info(board_id, sn, location, daqid, trig1id, trig2id, info):
    db = connect(1)
    cur = db.cursor()

    if not board_id:
        try:
            cur.execute("SELECT board_id FROM Board WHERE full_id = '%s';" % sn)
            rows = cur.fetchall()

            if not rows:
                home_page_list.add_module(sn)
                cur.execute("SELECT board_id FROM Board WHERE full_id = '%s';" % sn)
                board_id = cur.fetchall()[0][0]
            else:
                board_id = rows[0][0]

        except mysql.connector.Error as err:
            print("CONNECTION ERROR")
            print(err)

    try:
        cur.execute('INSERT INTO Board_Info (board_id, info_type, info, daq_chip_id, trigger_chip_1_id, trigger_chip_2_id, location) VALUES (%i, %i, "%s", "%s", "%s", "%s", "%s");' % (board_id, 0, info, daqid, trig1id, trig2id, location))

        db.commit()
        db.close()

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)

def add_revoke(test_id):
    db = connect(0)
    cur = db.cursor()
    
    cur.execute("SELECT test_type_id, board_id FROM Test WHERE test_id = %s" % test_id)
    test_type_id, board_id = cur.fetchall()[0]
    
    cur.execute("SELECT name FROM Test_Type WHERE test_type = %s" % test_type_id)
    name = cur.fetchall()[0][0]

    cur.execute("Select full_id FROM Board WHERE board_id = %s" % board_id)
    full_id = cur.fetchall()[0][0]

    print('<div class="row">')
    print('<div class="col-md-10 pt-5 ps-5 mx-2 my-2">')
    print('<h2>Revoke %s for Board %s</h2>' % (name, full_id))
    print('</div>')
    print('</div>')

    print('<form action="revoke_success2.py" method="post" enctype="multipart/form-data">')
    print('<input type="hidden" name="test_id" value="%s">' % test_id)
    print('<div class="form-group pt-2 px-5 mx-2 my-2">')
    print('<label for="revokeComments"> Revoke Comments </label>')
    print('<textarea class="form-control" name="revokeComments" rows="3" cols="50"></textarea>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<input type="submit" class="btn btn-dark" value="Submit Revoke">')
    print('</form>')

def revoke_success(test_id, comments):
    db = connect(1)
    cur = db.cursor()
  
    try:
        cur.execute('INSERT INTO TestRevoke (test_id, comment) VALUES (%s, "%s")' % (test_id, comments))

        db.commit()
        db.close()

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)

def get_test_types():
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

    db = connect(1)
    cur = db.cursor() 

    print("Adding board image")

    try: 
        cur.execute("SELECT board_id FROM Board WHERE full_id = '%s';" % sn)
        rows = cur.fetchall()

        if not rows:
            print("Board sn does not exist! Make sure this board has been entered into the database.")

        else:
            board_id = rows[0][0]

        img_path = "/home/ePortage/wagondb"
        img_name = str(uuid.uuid4())

        path = "{}/{}".format(img_path, img_name)

        cur.execute('INSERT INTO Board_images (board_id, image_name, view, date) VALUES (%s, "%s", "%s", NOW())' % (board_id, img_name, view))

        db.commit()
        db.close()

        print("Attempting to write file...")

        with open(path, "wb") as f:
            print("File opened!")
            f.write(img_file)
            print("File wrote:)")

        print("File recieved successfully!")

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)

def change_board_location(sn, location):

    db = connect(1)
    cur = db.cursor() 

    try: 
        cur.execute("SELECT board_id FROM Board WHERE full_id = '%s';" % sn)
        rows = cur.fetchall()

        if not rows:
            print("Board sn does not exist! Make sure this board has been entered into the database.")

        else:
            board_id = rows[0][0]

        cur.execute('UPDATE Board SET location="%s" WHERE board_id=%i' % (location, board_id))

        db.commit()
        db.close()

        print("Location Updated Successfully!")

    except mysql.connector.Error as err:
        print("CONNECTION ERROR")
        print(err)





