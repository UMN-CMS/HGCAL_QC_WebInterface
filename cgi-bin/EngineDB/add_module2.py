#!/usr/bin/python3

import cgi, html
import base
import home_page_list
import connect
import os

base_url = connect.get_base_url()

#cgi header
print("Content-type: text/html\n")

base.header(title='Adding a new module...')
base.top(False)

form = cgi.FieldStorage()

if form.getvalue('full_id'):
    full = html.escape(form.getvalue('full_id'))
    manu = html.escape(form.getvalue('manufacturer'))
    loc = html.escape(form.getvalue('location'))

    # calls add_module() to add it to DB
    home_page_list.add_module(full, manu, loc)
    
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

    base.bottom(False) 
    
