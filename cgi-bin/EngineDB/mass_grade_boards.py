#!./cgi_runner.sh

import cgi, html
import base
import os
from connect import connect
import csv
import io

#cgi header
print("Content-type: text/html\n")

base.header('Grade Many Boards')
base.top()

db = connect(1)
cur = db.cursor()

form = cgi.FieldStorage()

action = form.getvalue('action')

if action == 'submit':

    person_id = base.cleanCGInumber(form.getvalue('person_id'))
    csv_file = form['boards']

    csv_text = csv_file.file.read().decode('utf-8')
    f = io.StringIO(csv_text)

    reader = csv.reader(f)
    boards = list(reader)

    for b in boards:
        cur.execute('select board_id from Board where full_id="%s"' % b[0])
        x = cur.fetchall()[0][0]
        cur.execute('insert into Grades (board_id, person_id, grading_time, grade, comments) values (%s, %s, NOW(), "%s", "%s")' % (x, person_id, b[1], b[2]))

    db.commit()

else:
    print('<form action="mass_grade_boards.py" method="post" enctype="multipart/form-data">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Grade Many Boards</h2>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h4>Attach a three column csv, no headers</h4>')
    print('<h5>First column is the barcodes, second is the corresponding grade, third is the comment</h5>')
    print('</div>')
    print('</div>')

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
    print('<div class="row">')
    print('<div class="col-md-2 pt-2 ps-5 mx-2 my-2">')
    print("<b>Boards CSV:</b>")
    print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
    print("<input type='file' class='form-control' name='boards'>")
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<button class="btn btn-dark" type="submit" name="action" value="submit">Submit</button>')
    print('</div>')
    print('</div>')

    print('</form>')

base.bottom()
