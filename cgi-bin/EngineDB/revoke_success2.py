#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import connect

cgitb.enable()

base_url = connect.get_base_url()

print("Location: %s/summary.py\n\n"%(base_url))
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
test_id = base.cleanCGInumber(form.getvalue("test_id"))
comments = form.getvalue("revokeComments")

if comments:
    comments = cgi.escape(comments)

base.header(title='Revoke Success')
base.top(False)

module_functions.revoke_success(test_id, comments)

base.bottom(False)


