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
#try:
#    os.environ["TEMP"] = '/tmp/HGCAL_ApacheServer/board_images' 
#    tos.mkdtemp(prefix="BoardImage_", dir=os.environ["TEMP"])
#    sysTemp = tempfile.gettempdir()
#    print(sysTemp)
#except Exception as e:
#    print(e)
base_url = connect.get_base_url()

#print("Location: %s/summary.py\n\n"%(base_url))
#cgi header
form = cgi.FieldStorage()
sn = cgi.escape(form.getvalue("full_id"))
#fileitem = form['file']

base.header(title='Add Board Image')
base.top(False)

print('<form action="add_board_image_upload.py" method="post" enctype="multipart/form-data">')
print('<INPUT TYPE="hidden" name="serial_number" value="%s">' % (sn))
print('<div class="row">')
print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2>Add Image for Board %s</h2>' %sn)
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
