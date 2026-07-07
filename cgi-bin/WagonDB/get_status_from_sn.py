#!./cgi_runner.sh
import cgi, html
import cgitb
import base
import home_page_list
import sys
from add_test_functions import get_status

cgitb.enable()
#cgi header
print("content-type: text/html\n\n")

base.header(title='')
base.top()

form = cgi.FieldStorage()

full_id = form.getvalue('full_id')

status = get_status(full_id)

print(status)

base.bottom()
