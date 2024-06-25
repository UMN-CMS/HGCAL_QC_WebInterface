#!/usr/bin/python3

import cgi
import cgitb
cgitb.enable()
import base
#import module_functions
import connect
import os
import tempfile

print("Content-type: text/html\n")
base_url = connect.get_base_url()

form = cgi.FieldStorage()
full_id = cgi.escape(form.getvalue("full_id"))

base.header(title='Add Board Image')
base.top(False)

# calls the form that uploads the image on submit
print('<form action="add_board_image_upload.py" method="post" enctype="multipart/form-data">')
print('<INPUT TYPE="hidden" name="full_id" value="%s">' % (full_id))
print('<div class="row">')
print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2>Add Image for Board %s</h2>' %full_id)
print('</div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-2 pt-2 ps-5 mx-2 my-2">')
print("<b>Top View:</b>")
print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
print("<input type='file' class='form-control' name='top_view'>")
print('</div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-2 pt-2 ps-5 mx-2 my-2">')
print("<b>Bottom View:</b>")
print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
print("<input type='file' class='form-control' name='bottom_view'>")
print('</div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
print('<input type="submit" class="btn btn-dark" value="Add Images">')
print('</div>')
print('</div>')
print('</form>')
base.bottom(False)

