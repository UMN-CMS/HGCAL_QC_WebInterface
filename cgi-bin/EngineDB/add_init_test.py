#!/usr/bin/python3

import cgi, html
import base
import add_test_functions
import os

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
label_applied = base.cleanCGInumber(form.getvalue("label_applied"))
database_entry = base.cleanCGInumber(form.getvalue("database_entry"))
label_legibility = base.cleanCGInumber(form.getvalue("label_legibility"))
power_cycle = base.cleanCGInumber(form.getvalue("power_cycle"))
tester = html.escape(form.getvalue("tester"))
serial_num = base.cleanCGInumber(form.getvalue("serial_num"))
comments = form.getvalue("comments")

test_results = {"Label Applied": label_applied, "Database Entry": database_entry, "Label Legibility": label_legibility, "Power Cycle": power_cycle}

if comments:
    comments = html.escape(comments)

base.header(title='Add Test')
base.top(False)

test_id=add_test_functions.add_init_tests(serial_num, tester, test_results, comments)

base.bottom(False)
