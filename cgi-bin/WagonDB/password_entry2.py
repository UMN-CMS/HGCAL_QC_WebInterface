#!/usr/bin/python3

import cgi
import base
import home_page_list
import add_test_functions
import hashlib
import connect

try: 
    base_url = connect.get_base_url()

    form = cgi.FieldStorage()
    url = form.getvalue("url")
    password = form.getvalue("password")

    correct_password = "8ae3ce28c2aecce334e4c2395b86066b"

    # decodes password and checks if it's correct
    if hashlib.md5(password.encode('utf-8')).hexdigest() == correct_password:
        print("Location: %s/%s\n\n" % (base_url,url))

        print("Content-type: text/html\n")

        base.header(title='Access Granted')
        base.top(False)

        print("<div class='row'>")
        print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
        print('<h2>Access Granted</h2>')
        print("</div>")
        print("</div>")

        base.bottom(False)

    else:
        print("Content-type: text/html\n")
        
        base.header(title='Access Denied')
        base.top(False)

        print("<div class='row'>")
        print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
        print('<h2>Access Denied</h2>')
        print("</div>")
        print("</div>")

        base.bottom(False)

except Exception as e:
    print("content-type: text/html\n")
    print(e)
