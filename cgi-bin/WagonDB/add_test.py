#!./cgi_runner.sh

import cgi, html
import base
import home_page_list
import add_test_functions_wagon


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
bc = html.escape(form.getvalue('full_id'))
suggested_test = base.cleanCGInumber(form.getvalue('suggested'))

base.header(title='Add Test')
base.top(False)

add_test_functions_wagon.add_test_template(bc, suggested_test)

base.bottom(False)
