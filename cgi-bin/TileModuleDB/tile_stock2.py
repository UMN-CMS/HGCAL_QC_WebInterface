#!./cgi_runner.sh

import cgi, html
import cgitb; cgitb.enable()
import base
import board_check_functions
import os
from connect import connect, get_base_url
from home_page_list import add_module

base_url = get_base_url()
db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

base.header(title='Board Check In')
base.top()

# grabs the information from the form and calls board_checkin() to enter info into the DB
form = cgi.FieldStorage()

mat = form.getvalue("mat")
size = form.getvalue("size")
batch_num = form.getvalue("batch_num")
reel = form.getvalue("reel")
num_tiles = form.getvalue("num_tiles")

base_barcode = "320T" + mat + size + batch_num + reel
typecode = "T" + mat + "-" + size 
batch = batch_num + "-" + reel

for n in range(int(num_tiles)):
    if len(str(n)) == 1:
        barcode = base_barcode + "00" + str(n)
    elif len(str(n)) == 2:
        barcode = base_barcode + "0" + str(n)
    elif len(str(n)) == 3:
        barcode = base_barcode + str(n)
    else:
        raise

    cur.execute('insert into COMPONENT_STOCK (barcode, typecode, entered, batch) values ("%s", "%s", NOW(), "%s")' % (barcode, typecode, batch))

db.commit()

print("Created stock successfully")

base.bottom()
