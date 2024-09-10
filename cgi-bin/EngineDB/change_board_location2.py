#!./cgi_runner.sh

import module_functions
import cgi
import base

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
bc = cgi.escape(form.getvalue("full_id"))
location = cgi.escape(form.getvalue("location"))

base.header(title='Change Board Location')
base.top(False)
try:
    module_functions.change_board_location(str(bc), location)
except Exception as e:
    print("Issue updating board location")
    print(e)

base.bottom(False)
