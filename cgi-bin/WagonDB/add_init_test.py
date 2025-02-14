#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions_wagon
import os

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
label_applied = base.cleanCGInumber(form.getvalue("label_applied"))
database_entry = base.cleanCGInumber(form.getvalue("database_entry"))
label_legibility = base.cleanCGInumber(form.getvalue("label_legibility"))
power_cycle = base.cleanCGInumber(form.getvalue("power_cycle"))
tester = html.escape(form.getvalue("tester"))
bc = html.escape(form.getvalue("full_id"))
comments = form.getvalue("comments")

test_results = {"Label Applied": label_applied, "Database Entry": database_entry, "Label Legibility": label_legibility, "Power Cycle": power_cycle}

if comments:
    comments = html.escape(comments)

base.header(title='Add Test')
base.top(False)

test_id=add_test_functions_wagon.add_init_tests(bc, tester, test_results, comments)

base.bottom(False)

