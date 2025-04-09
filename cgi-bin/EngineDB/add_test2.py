#!./cgi_runner.sh

import cgi, html
import cgitb
cgitb.enable()
import base
import add_test_functions
import os
import connect

base_url = connect.get_base_url()

print("Location: %s/summary.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
person_id = base.cleanCGInumber(form.getvalue("person_id"))
test_type = base.cleanCGInumber(form.getvalue("test_type"))
serial_num = html.escape(form.getvalue("serial_number"))
success = base.cleanCGInumber(form.getvalue("success"))
comments = form.getvalue("comments")

if comments:
    comments = html.escape(comments)

base.header(title='Add Test')
base.top(False)

test_id=add_test_functions.add_test(person_id, test_type, serial_num, success, comments, None)

for itest in [1]:
    afile = form['attach%d'%(itest)]
    if (afile.name):
        adesc= form.getvalue("attachdesc%d"%(itest))
        if adesc:
            adesc = html.escape(adesc)
        acomment= form.getvalue("attachcomment%d"%(itest))
        if acomment:
            acomment = html.escape(acomment)
        add_test_functions.add_test_attachment(test_id,afile,adesc,acomment)
    elif (afile.filename):
        adesc= form.getvalue("attachdesc%d"%(itest))
        if adesc:
            adesc = html.escape(adesc)
        acomment= form.getvalue("attachcomment%d"%(itest))
        if acomment:
            acomment = html.escape(acomment)
        add_test_functions.add_test_attachment_gui(test_id,afile,adesc,acomment)
    
base.bottom(False)
