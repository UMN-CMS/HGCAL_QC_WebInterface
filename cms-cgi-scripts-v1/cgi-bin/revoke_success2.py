#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions

cgitb.enable()

print("Location: http://cmslab1.spa.umn.edu/~cros0400/cgi-bin/summary.py\n\n")
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
test_id = base.cleanCGInumber(form.getvalue("test_id"))
comments = form.getvalue("revokeComments")

if comments:
    comments = cgi.escape(comments)

base.header(title='Revoke Success')
base.top()

module_functions.revoke_success(test_id, comments)

base.bottom()


