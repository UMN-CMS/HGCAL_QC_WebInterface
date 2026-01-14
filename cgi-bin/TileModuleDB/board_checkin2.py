#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
import board_check_functions
import os
from connect import connect, get_base_url
from home_page_list import add_module

base_url = get_base_url()
db = connect(1)
cur = db.cursor()

def get_tiles(barcode):
    return {"06": 16, "S1": 4}

#cgi header
print("Content-type: text/html\n")

base.header(title='Board Check In')
base.top()

# grabs the information from the form and calls board_checkin() to enter info into the DB
form = cgi.FieldStorage()

person_id = form.getvalue("person_id")
comments = form.getvalue("comments")
pcb_barcode = form.getvalue("pcb_barcode")
action = form.getvalue("action")

mat = form.getvalue("mat")

if mat == "M":
    mm = "TI"
elif mat == "C":
    mm = "TC"

tq = "320TQ" + pcb_barcode[5:8] + mat + pcb_barcode[8] + pcb_barcode[10:]

tiles = get_tiles(tq)

if action == "submit2":
    add_module(tq, "Fermilab", "Fermilab")

    cur.execute('select board_id from Board where full_id="%s"' % tq)
    board_id = cur.fetchall()[0][0]

    board_check_functions.board_checkin(board_id, person_id, comments)

    cur.execute('select component_id from COMPONENT_STOCK where barcode="%s"' % pcb_barcode)
    comp_id = cur.fetchall()[0][0]
    cur.execute("insert into COMPONENT_USAGE (component_id, used_in, used_when) values (%s, %s, NOW())" % (comp_id, board_id))

    cur.execute("insert into Check_Out (board_id, person_id, comment, checkout_date) values (%s, %s, '%s', NOW())" % (board_id, person_id, f"Used in {tq}"))

    for tt, num in tiles.items():
        typecode = mm + "-" + tt
        bnum = base.cleanCGInumber(form.getvalue("num_batches_%s" % tt))
        for i in range(bnum):
            name = form.getvalue("batch_%s" % (tt + "_" + str(i)))
            num_tiles = base.cleanCGInumber(form.getvalue("num_%s" % (tt + "_" + str(i))))
            cur.execute('select C.component_id from COMPONENT_STOCK C where typecode="%s" and batch="%s" and NOT EXISTS (select 1 from COMPONENT_USAGE U where U.component_id = C.component_id) order by C.component_id ASC' % (typecode, name))

            tiles_to_use = cur.fetchall()[0:num_tiles]

            for t in tiles_to_use:
                cur.execute("insert into COMPONENT_USAGE (component_id, used_in, used_when) values (%s, %s, NOW())" % (t[0], board_id))

    db.commit()

else:

    print('<form action="board_checkin2.py" method="post" enctype="multipart/form-data">')
    print("<div class='row'>")
    print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
    print('<h2>Add Tiles to be used</h2>')
    print("</div>")
    print("</div>")

    print(f"<input type='hidden' name='person_id' value='{person_id}'>")
    print(f"<input type='hidden' name='comments' value='{comments}'>")
    print(f"<input type='hidden' name='pcb_barcode' value='{pcb_barcode}'>")
    print(f"<input type='hidden' name='mat' value='{mat}'>")

    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<tr>')
    print('<th> Typecode </th>')
    print('<th> # needed </th>')
    print('<th> Batch </th>')
    print('<th> # used </th>')
    print('<th> </th>')
    print('</tr>')

    for tt, num in tiles.items():
        typecode = mm + "-" + tt
        cur.execute('select DISTINCT batch from COMPONENT_STOCK where typecode="%s"' % (typecode))
        batches = cur.fetchall()

        bnum = base.cleanCGInumber(form.getvalue("num_batches_%s" % tt))

        if not bnum:
            bnum = 1

        if action == "add_%s" % tt:
            bnum += 1

        print(f"<input type='hidden' name='num_batches_{tt}' value='{bnum}'>")

        for i in range(bnum):
            print('<tr>')
            print('<td>%s</td>' % typecode)
            print('<td>%s</td>' % num)
            print('<td>')
            print('<select class="form-control" name="batch_%s">' % (tt + "_" + str(i)))
            for b in batches:
                print("<option value='%s'>%s</option>" % (b[0], b[0]))

            print('</select>')
            print('</td>')
            print('<td>')
            print('<input type="text" name="num_%s">' % (tt + "_" + str(i)))
            print('</td>')
            print('<td>')
            print('<button class="btn btn-dark" type="submit" name="action" value="add_%s">Add Batch</button>' % tt)
            print('</td>')
            print('</tr>')
                        

    print('</table>')
    print('</div>')
    print('</div>')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
    # submits the form on click
    print('<button class="btn btn-dark" type="submit" name="action" value="submit2">Use Tiles</button>')
    print("</div>")
    print("</div>")
    print("<div class='row pt-4'>")
    print("</div>")
    print("</form>")

base.bottom()
