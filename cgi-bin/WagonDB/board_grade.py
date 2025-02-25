#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
import home_page_list
import add_test_functions_wagon


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()

# this page can be accessed from a link that autofills the barcode
# or it can be accessed normally, this checks which one it is
try:
    bc = html.escape(form.getvalue("full_id"))
    board_id = base.cleanCGInumber(form.getvalue("board_id"))
except:
    bc = None
    board_id = None

base.header(title='Board Grade')
base.top(False)

if bc:
    add_test_functions_wagon.add_board_grade_form(bc)
else:
    add_test_functions_wagon.add_board_grade_form()

base.bottom(False)
