#!/usr/bin/python3

import cgi
import base
import home_page_list
import home_page_allboards
import sys

if(len(sys.argv) != 1):
	stdout = sys.stdout
	sys.stdout = open('%(loc)s/index.html' %{ 'loc':sys.argv[1]}, 'w') 
else:
	#cgi header
	print("content-type: text/html\n\n")

base.header(title='Wagon Test Home Page')
base.top()

print()
print('<div class="row">')
print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2>Count by Test</h2>' )
print('</div>')
print('</div>')

home_page_list.render_list_tests()
print('<hr>')

print('<div class="row">')
print('<div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
print('<h2>List of All Boards</h2>' )
print('<b><em>(Sorted by Serial Number)</em></b>&emsp;<badge class="badge bg-primary">Successful Tests</badge>')
print('</div>')
print('<div class="col-md-3"></div>')
if len(sys.argv) == 1:
    print('<div class="col-md-3">')
    print('<br>')
    print('<a href="add_module.py">')
    print('<button type="button" class="btn btn-dark text-light">Add a New Board</button>')
    print('</a>')
    print('</div>')
else:
    print('<div class="col-md-3">')
    print('<br>')
    print('<a href="add_module.html">')
    print('<button type="button" class="btn btn-dark text-light">Add a New Board</button>')
    print('</a>')
    print('</div>')
print('</div>')
print('<br><br>')


#home_page_list.render_list_module()
home_page_allboards.renderlist()

base.bottom()

if len(sys.argv) != 1:
	sys.stdout.close()
	sys.stdout = stdout
