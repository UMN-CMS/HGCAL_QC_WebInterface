#!/usr/bin/python3

from connect import connect
import sys
#import mysql.connector

base_url = connect.get_base_url()

print("Location: %s/summary.py\n\n"%(base_url))

import os

print(os.environ.get("QUERY_STRING", "No Query String in url"))

#cgi header
print("Content-type: text/html\n")

base.header(title='Adding a new module...')
base.top(False)

form = cgi.FieldStorage()

if form.getvalue('full_id'):
    sn = cgi.escape(form.getvalue('full_id'))

    home_page_list.add_module(sn)
    
    print('<div class="row">')
    print('<div class="col-md-3 ps-4 pt-2 mx-2 my-2">')
    print('<h2>List of All Boards</h2>' )
    print('<b><em>(Sorted by Full ID)</em></b>')
    print('</div>')
    print('<div class="col-md-3 ps-5 pt-2 mx-2 my-2">')
    print('<a href="add_module.py">')
    print('<button type="button">Add a New Board</button>')
    print('</a>')
    print('</div>')
    print('</div>')

    print('<br><br>')


    home_page_list.render_list_module()

    base.bottom(False)


else:
    print('<div class="row">')
    print('<div class="col-md-12 ps-4 pt-2 mx-2 my-2">')
    print('<h4><b> FAILED. Enter Full ID </b></h4>')
    print('</div>')
    print('</div>')

    home_page_list.add_module_form()


    print('<div class="row">')
    print('<div class="col-md-3 ps-4 pt-2 mx-2 my-2">')
    print('<h2>List of All Boards</h2>' )
    print('<b><em>(Sorted by Full ID)</em></b>')
    print('</div>')
    print('</div>')

    print('<br><br>')

    home_page_list.render_list_module()

    base.bottom(False)

    
    
    
