#!/usr/bin/python3

import cgi
import cgitb
cgitb.enable()
import base
import module_functions
import connect
import os
import tempfile
import base64

print("Content-type: text/html\n")
base_url = connect.get_base_url()

form = cgi.FieldStorage()
full = cgi.escape(form.getvalue("full_id"))
fileitem = cgi.escape(form.getvalue("image"))
view = cgi.escape(form.getvalue("view"))

fileitems = base64.b64decode(fileitem)

try:
    module_functions.add_board_image(str(full), fileitems, view)
except Exception as e:
    print("Issue uploading")
    print(e)
