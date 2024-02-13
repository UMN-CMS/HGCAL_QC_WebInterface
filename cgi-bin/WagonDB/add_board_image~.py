#!/usr/bin/python3

import cgi
import cgitb
cgitb.enable()
import base
import module_functions
import connect
import os
import tempfile
import base64

print("Content-type: text/html\n")
#try:
    #os.environ["TEMP"] = '/tmp/HGCAL_ApacheServer/board_images' 
    #os.mkdtemp(prefix="BoardImage_", dir=os.environ["TEMP"])
    #sysTemp = tempfile.gettempdir()
    #print(sysTemp)
#except Exception as e:
#    print(e)
base_url = connect.get_base_url()

#print("Location: %s/summary.py\n\n"%(base_url))
#cgi header
form = cgi.FieldStorage()
sn = cgi.escape(form.getvalue("serial_num"))
fileitem = cgi.escape(form.getvalue("image"))
view = cgi.escape(form.getvalue("view"))

fileitems = base64.b64decode(fileitem)

#base.header(title='Add Board Image')
#base.top()

#print('<form action="add_test2.py" method="post" enctype="multipart/form-data">')
#print('<INPUT TYPE="hidden" name="serial_number" value="%s">' % (sn))
#print('<div class="row">')
#print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
#print('<h2>Add Image for Board %s</h2>' %sn)
#print('</div>')
#print('</div>')
#print('<div class="row">')
#print('<div class="col-md-2 pt-2 ps-5 mx-2 my-2">')
#print("<b>Attachment:</b>")
#print('</div><div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
#print("<input type='file' class='form-control' name='attached_image'>")
#print('</div>')
#print('</div>')
#print('<div class="row">')
#print('<div class="col-md-6 pt-2 ps-5 mx-2 my-2">')
#print('<input type="submit" class="btn btn-dark" value="Add Image">')
#print('</div>')
#print('</div>')
#print('</form>')
try:
    module_functions.add_board_image(str(sn), fileitems, view)
except Exception as e:
    print("Issue uploading")
    print(e)
#base.bottom()
