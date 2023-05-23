#!/usr/bin/python3
from connect import connect
import sys
#import mysql.connector
from get_attach import save
import home_page_list

def Portage_fetch(test_type_id, board_sn):
    db = connect(0)
    cur = db.cursor()
    cur.execute("SELECT People.person_name, Test.day, Test.successful, Test.comments, Test_Type.name, Test.test_id FROM Test, Test_Type, People, Board  WHERE Test_Type.test_type = %(test_id)s AND Board.full_id = %(sn)s AND People.person_id = Test.person_id AND Test_Type.test_type=Test.test_type_id AND Test.board_id = Board.board_id ORDER BY Test.day ASC" %{'test_id':test_type_id, 'sn':board_sn})
    return cur.fetchall()

def Portage_fetch_revokes(board_sn):
    db=connect(0)
    cur = db.cursor()
    cur.execute("SELECT TestRevoke.test_id, TestRevoke.comment FROM TestRevoke,Test,Board WHERE Board.sn = %(sn)s AND Board.board_id = Test.board_id AND Test.test_id = TestRevoke.test_id" %{'sn':board_sn})
    # build a dictionary
    revoked={}
    for fromdb in cur.fetchall():
        revoked[fromdb[0]]=fromdb[1]
    return revoked

def Portage_fetch_attach(test_id):
    db = connect(0)
    cur = db.cursor()
    cur.execute('SELECT attach_id, attachmime, attachdesc, originalname FROM Attachments WHERE test_id=%(tid)s ORDER BY attach_id' % {'tid':test_id})
    return cur.fetchall()

def add_test_tab(sn, board_id):

    print('<div class="row">')
    print('<div class="col-md-5 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Wagon Test Info for %d</h2>' %sn)
    print('</div>')
    print('</div>')
    
    print('<div class="row">')
    print('<div class="col-md-2 ps-5 pt-2 mx-2 my-2">')
    print('<a href="add_test.py?board_id=%(id)d&serial_num=%(serial)d">' %{'serial':sn, 'id':board_id})
    print('<button class="btn btn-dark"> Add a New Test </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 mx-2 my-2">')
    print('<a href="add_board_info.py?board_id=%(id)d&serial_num=%(serial)d">' %{'serial':sn, 'id':board_id})
    print('<button class="btn btn-dark"> Add Board Info </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 mx-2 my-2">')
    print('<a href="board_checkout.py?serial_num=%(serial)d">' %{'serial':sn})
    print('<button class="btn btn-dark"> Checkout Board </button>')
    print('</a>')
    print('</div>')
    print('<div class="col-md-2 ps-5 pt-2 mx-2 my-2">')
    print('<a href="board_checkin.py?board_id=%(board_id)d">' %{'board_id':board_id})
    print('<button class="btn btn-dark"> Checkin Board </button>')
    print('</a>')
    print('</div>')
    print('</div>')



def ePortageTest(test_type_id, board_sn, test_name, revokes):
    attempts =  Portage_fetch(test_type_id, board_sn) 
    print('<hr>')
    print('<div class="row">')
    print('<div class="col-md-12 px-5 pt-2 mx-2 my-2">')
    print('<h3> %(name)s </h3>' %{ "name":test_name})
    print('<br>')

    n = 0
    for attempt in attempts:
        n += 1

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
        print('<td> %(pname)s </td>' %{ "pname":attempt[0]})
        print('<td> %(when)s </td>' %{ "when":attempt[1]})
        if attempt[2] == 1:
            if attempt[5] in revokes:
                print('<td><b>Revoked</b>: %(comment)s </td>' %{ "comment":revokes[attempt[5]] })
            else:
                print('<td align=left> Yes </td>')
                if len(sys.argv) == 1:
                    print("<td align=right style='{ background-color: yellow; }' ><a href='revoke_success.py?test_id=%(id)s'>Revoke</a></td>" %{ "id":attempt[5]})

        else:
            print('<td colspan=2>No</td>')
        print('</tr>')
        print('<tr>')
        print('<td><b>Comments:</b></td>' )
        print('<td colspan=3> %(comm)s </td>' %{ "comm":attempt[3]})
        print('</tr>')
        attachments=Portage_fetch_attach(attempt[5])
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

def board_info(info):
    if info and len(info[0]) == 5:
        location = info[0][0]
        daq_chip_id = info[0][1]
        trigger_chip_1_id = info[0][2]
        trigger_chip_2_id = info[0][3]
        info_com = info[0][4]
    
    else:
       location, daq_chip_id, trigger_chip_1_id, trigger_chip_2_id, info_com = "None", "None", "None", "None", "None"
 
    print('<div class="col-md-11 pt-2 px-4 mx-2 my-2">')
    print('<table class="table table-bordered table-hover table-active">')
    print('<tbody>')
    print('<tr>')
    print('<th colspan=3>Location</th>')
    print('<th>DAQ Chip ID</th>')
    print('<th>Trigger Chip 1 ID</th>')
    print('<th>Trigger Chip 2 ID</th>')
    print('</tr>')
    print('<tr>')
    print('<td colspan=3>%s</td>' % location)
    if daq_chip_id != "0" and trigger_chip_1_id != "0" and trigger_chip_2_id != "0":
        print('<td>%s</td>' % daq_chip_id)
        print('<td>%s</td>' % trigger_chip_1_id)
        print('<td>%s</td>' % trigger_chip_2_id)
    else:
        print('<td>None</td>')
        print('<td>None</td>') 
        print('<td>None</td>')
        
    print('</tr>')
    print('<tr>')
    print('<th colspan=10>Comments</th>')
    print('</tr>')
    print('<td colspan=10>%s</td>' % info_com)
    print('</tr>')
    print('</tbody>')
    print('</table>')
    print('</div>')

def add_board_info(board_id, sn, location, daqid, trig1id, trig2id, info):
    db = connect(1)
    cur = db.cursor()

    if not board_id:
        try:
            cur.execute('SELECT board_id FROM Board WHERE full_id = %s;' % sn)
            rows = cur.fetchall()

            if not rows:
                home_page_list.add_module(sn)
                cur.execute('SELECT board_id FROM Board WHERE full_id = %s;' % sn)
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

