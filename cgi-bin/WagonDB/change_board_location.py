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
sn = cgi.escape(form.getvalue("serial_num"))
#fileitem = form['file']

base.header(title='Change Board Location')
base.top()

print('<form action="change_board_location2.py" method="post" enctype="multipart/form-data">')
print('<INPUT TYPE="hidden" name="serial_number" value="%s">' % (sn))
print('<div class="row">')
print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
print('<h2>Change Board Location %s</h2>' %sn)
print('</div>')
print('</div>')
print('<div class="row">')
print('<div class = "col-md-5 ps-5 pt-2 mx-2 my-2">')
print('<input type="text" name="location" placeholder="Location">')
print('</div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
print('<input type="submit" class="btn btn-dark" value="Update Location">')
print('</div>')
print('</div>')
print('</form>')

base.bottom()
