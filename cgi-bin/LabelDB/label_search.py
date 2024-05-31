#!/usr/bin/python3

import cgi
import cgitb
cgitb.enable()
import base
import connect
import os

print("Content-type: text/html\n")

base.header(title='Search for Label')
base.top()

# creates form to change board location
# runs change_board_location2.py with the form info on submit 
print('<form action="label_search2.py" method="post" enctype="multipart/form-data">')
print('<div class="row">')
print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2>Search for Label</h2>')
print('</div>')
print('</div>')

print('<div class="col">')
print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
print('<label> Query')
print('<select class="form-control" name="query">')
print('<option value="Contains">Contains</option>')
print('<option value="Starts with">Starts with</option>')
print('<option value="Ends with">Ends with</option>')
print('</select>')
print('</label>')
print('</div>')
print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
print('<input type="text" name="serial_num" placeholder="Serial Number">')
print('</div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
print('<input type="submit" class="btn btn-dark" value="Search">')
print('</div>')
print('</div>')
print('</form>')

base.bottom()
