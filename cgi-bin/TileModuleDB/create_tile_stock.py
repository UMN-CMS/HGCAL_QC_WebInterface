#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
from connect import connect
import sys
sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()

db = connect(0)
cur = db.cursor()

base.header(title='Board Check In')
base.top()

print('<form action="tile_stock2.py" method="post" enctype="multipart/form-data">')
print("<div class='row'>")
print('<div class = "col-md-6 pt-4 ps-4 mx-2 my-2">')
print('<h2>Add new Tile stock</h2>')
print("</div>")
print("</div>")

print("<div class='row'>")
print('<div class="col-md-3 pt-2 ps-5 mx-2 my-2">')
print('<label>Tile Material')
print('<select class="form-control" name="mat">')

print("<option value='I'>Injection Molded</option>")
print("<option value='C'>Cast Machined</option>")
                    
print('</select>')
print('</label>')
print('</div>')
print('<div class = "col-md-3 pt-2 ps-5 mx-2 my-2">')
print('<label>Size')
print('<select class="form-control" name="size">')

tile = la.getMajorType("TC")
for s in tile.getAllSubtypes():
    name = tile.getSubtypeByCode(s).name
    print('<option value="%s">%s</option>' % (s, name))

                    
print('</select>')
print('</label>')
print("</div>")
print("</div>")

print("<div class='row'>")
print('<div class = "col-md-11 pt-2 ps-5 mx-2 my-2">')
print('<label>Batch Number</label>')
print('<input type="text" name="batch_num">')
print("</div>")
print('<div class = "col-md-11 pt-2 ps-5 mx-2 my-2">')
print('<label>Wrapping ID</label>')
print('<input type="text" name="reel">')
print("</div>")
print('<div class = "col-md-11 pt-2 ps-5 mx-2 my-2">')
print('<label>Number of Tiles</label>')
print('<input type="text" name="num_tiles">')
print("</div>")
print("</div>")

print("<div class='row'>")
print('<div class = "col-md-6 pt-2 ps-5 mx-2 my-2">')
# submits the form on click
print('<input type="submit" class="btn btn-dark" value="Create Tile Stock">')
print("</div>")
print("</div>")
print("<div class='row pt-4'>")
print("</div>")
print("</form>")


base.bottom()
