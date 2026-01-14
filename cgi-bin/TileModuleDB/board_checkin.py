#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
from connect import connect
import sys
sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la
import board_check_functions
import os
from home_page_list import add_module

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()

db = connect(1)
cur = db.cursor()

major_type = form.getvalue("major_type")
action = form.getvalue("action", "")

base.header(title='Board Check In')
base.top()

if action == "submit":

    person_id = form.getvalue("person_id")
    comments = form.getvalue("comments")
    pcb_barcode = form.getvalue("pcb_barcode")

    if major_type == "TM":
        module = form.getvalue("mod_barcode")

        mat = module[8]

        tq = "320TQ" + pcb_barcode[5:8] + mat + pcb_barcode[8] + pcb_barcode[10:]

        sn = module[9:15]

        type_id = module[3:9]

        cur.execute('update Board set sn="%s", full_id="%s", type_id="%s" where full_id="%s"' % (sn, module, type_id, tq))
        cur.execute('update Check_Out set comment="%s"' % f"Used in {module}")
        db.commit()

        print("New module created successfully")

    else:
        add_module(pcb_barcode, "Maryland", "Fermilab")

        cur.execute('select board_id from Board where full_id="%s"' % pcb_barcode)
        board_id = cur.fetchall()[0][0]

        board_check_functions.board_checkin(board_id, person_id, comments)

else:

    if major_type == "TQ":
        print('<form action="board_checkin2.py" method="post" enctype="multipart/form-data">')
    else:
        print('<form action="board_checkin.py" method="post" enctype="multipart/form-data">')
    print("<div class='row'>")
    print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
    print('<h2>Add a New Tile Board</h2>')
    print("</div>")
    print("</div>")

    print(f"<input type='hidden' name='major_type' value='{major_type}'>")

    # creates a form to select the person checking the board in
    cur.execute("Select person_id, person_name from People;")
    print("<div class='row'>")
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Tester')
    print('<select class="form-control" name="person_id">')
    for person_id in cur:
        print("<option value='%s'>%s</option>" % ( person_id[0] , person_id[1] ))
                        
    print('</select>')
    print('</label>')
    print('</div>')
    print("</div>")

    print("<div class='row'>")
    print('<div class = "col-md-11 pt-2 ps-5 mx-2 my-2">')
    print('<label>PCB Barcode</label>')
    print('<input type="text" name="pcb_barcode">')
    print("</div>")

    if major_type == "TM":
        print('<div class = "col-md-11 pt-2 ps-5 mx-2 my-2">')
        print('<label>Module Barcode</label>')
        print('<input type="text" name="mod_barcode">')
        print("</div>")

    print("</div>")

    if major_type == "TQ":
        print("<div class='row'>")
        print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
        print('<label>Tile Material')
        print('<select class="form-control" name="mat">')

        print("<option value='M'>Injection Molded</option>")
        print("<option value='C'>Cast Machined</option>")
                            
        print('</select>')
        print('</label>')
        print('</div>')
        print('</div>')


    print('<div class="row">')
    print('<div class="col-md-11 pt-2 ps-5 mx-2 my-2">')
    print('<label>Comments</label><p>')
    print('<textarea rows = "2" cols="25" class="form-control" name="comments"></textarea>')
    print('</div>')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    # submits the form on click
    print('<button class="btn btn-dark" type="submit" name="action" value="submit">Add Board</button>')
    print("</div>")
    print("</div>")
    print("<div class='row pt-4'>")
    print("</div>")
    print("</form>")


base.bottom()
