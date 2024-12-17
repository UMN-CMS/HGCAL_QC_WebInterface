#!./cgi_runner.sh

import cgi, html
import base
import home_page_list
import add_test_functions_engine


#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
serial_num = html.escape(form.getvalue('full_id'))
suggested_test = base.cleanCGInumber(form.getvalue('suggested'))

base.header(title='Add Test')
base.top(False)

add_test_functions_engine.add_test_template(serial_num, suggested_test)

base.bottom(False)
