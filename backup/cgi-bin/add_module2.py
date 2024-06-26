#!/usr/bin/python3

import cgi
import base
import home_page_list

print("Location: http://cmslab3.umncmslab/~cros0400/cgi-bin/summary.py\n\n")

import os

print(os.environ.get("QUERY_STRING", "No Query String in url"))

#cgi header
print("Content-type: text/html\n")

base.header(title='Adding a new module...')
base.top()

form = cgi.FieldStorage()

if form.getvalue('serial_number'):
    sn = cgi.escape(form.getvalue('serial_number'))

    #print '<div> Serial Number = %(s)s , )s </div>' %{'s': sn} 
    home_page_list.add_module(sn)
    
    print('<div class="row">')
    print('<div class="col-md-3 ps-4 pt-2 mx-2 my-2">')
    print('<h2>List of All Boards</h2>' )
    print('<b><em>(Sorted by Serial Number)</em></b>')
    print('</div>')
    print('<div class="col-md-3 ps-5 pt-2 mx-2 my-2">')
    print('<a href="add_module.py">')
    print('<button type="button">Add a New Board</button>')
    print('</a>')
    print('</div>')
    print('</div>')

    print('<br><br>')


    home_page_list.render_list_module()

    base.bottom()


else:
    print('<div class="row">')
    print('<div class="col-md-12 ps-4 pt-2 mx-2 my-2">')
    print('<h4><b> FAILED. Enter SERIAL NUMBER </b></h4>')
    print('</div>')
    print('</div>')

    home_page_list.add_module_form()


    print('<div class="row">')
    print('<div class="col-md-3 ps-4 pt-2 mx-2 my-2">')
    print('<h2>List of All Boards</h2>' )
    print('<b><em>(Sorted by Serial Number)</em></b>')
    print('</div>')
    print('</div>')

    print('<br><br>')

    home_page_list.render_list_module()

    base.bottom()

    
    
    
