#!/usr/bin/python3

import cgi
import base
from add_label_functions import update_metatables

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
majortypes = form.getvalue('majortypes')

update_metatables(majortypes)
