#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
import home_page_list
import add_test_functions
from connect import connect


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
action = form.getvalue("action", "")

base.header(title='Override Board')
base.top()

db = connect(1)
cur = db.cursor()

if form.getvalue('action') == 'submit':

    full_id = form.getvalue('full_id')
    cur.execute('select board_id from Board where full_id="%s"' % full_id)
    board_id = cur.fetchall()[0][0]
    person_id = base.cleanCGInumber(form.getvalue('person_id'))
    grade = form.getvalue("grade")
    comments = html.escape(form.getvalue("comment"))

    passwd = html.escape(form.getvalue("password"))

    base.header(title='Board Grade')
    base.top()

    add_test_functions.add_board_grade(passwd, board_id, person_id, grade, comments)

    test = form.getvalue('test_type')
    success = base.cleanCGInumber(form.getvalue("success"))

    test_id = add_test_functions.add_test(person_id, test, full_id, success, "Overriden when grading", None)

    if test_id:
        if form.getvalue('attach'):
            afile = form['attach']
            if (afile.filename):
                add_test_functions.add_test_attachment(test_id, afile, None, None)
else:

    print('<form action="override_board.py" method="post" enctype="multipart/form-data">')
    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Override Board</h2>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-6 pt-4 ps-5 mx-2 my-2">')
    print('<label>Board Serial Number</label><p>')
    print('<INPUT type="text" class="form-control" name="full_id" value="">')
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
    print('<div class="col-md-6 pt-4 ps-5 mx-2 my-2">')
    print('<label>Board Grade</label><p>')
    print('<select name="grade" id="grade">')
    print('<option value="A">A</option>')
    print('<option value="B">B</option>')
    print('<option value="C">C</option>')
    print('<option value="D">D</option>')
    print('<option value="E">E</option>')
    print('<option value="F">F</option>')
    print('</select>')
    print('</div>')
    print('</div>')

    # gives options of for test type
    cur.execute("select test_type, name from Test_Type order by relative_order ASC;")
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Test Type')
    print('<select class="form-control" name="test_type">')
    for test_type in cur:
        print('<option value="%s">%s</option>' % (test_type[1], test_type[1]))
    print('</select>')
    print('</label>')
    print('</div>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
    print('<label>Successful?')
    print("<input class='form-check-input' type='checkbox' name='success' value='1'>")
    print('</label>')
    print('</div>')

    print('<div class="row">')
    print('<div class="col-md-6 pt-4 ps-5 mx-2 my-2">')
    print('<label>Comments</label><p>')
    print('<textarea class="form-control" name="comment" id="comment" rows="4" cols="50"></textarea>')
    print('</div>')

    print('<br><hr><br>'    )
    print('<div class="row">')
    print('<div class="col-md-2 pt-2 ps-5 mx-2 my-2">')
    print("<b>Attachment:</b>")
    print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
    print("<input type='file' class='form-control' name='attach'>")
    print('</div>')
    print('</div>')

    print("<div class='row'>")
    print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
    print("<label for='password'>Admin Password</label>")
    print("<input type='password' name='password'>")
    print("</div>")
    print("</div>")

    print("<div class='row'>")
    print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
    print('<button class="btn btn-dark" type="submit" name="action" value="submit">Submit</button>')
    print('</div>')
    print('</div>')

    print('</form>')

base.bottom()
