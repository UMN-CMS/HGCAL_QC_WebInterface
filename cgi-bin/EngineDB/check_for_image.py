#!./cgi_runner.sh

import cgi
import base
import settings
import os.path
import sys
import json
import connect
import base64

print("Content-type: text/json\n")

db=connect.connect(0)
cur=db.cursor()

form = cgi.FieldStorage()

full_id = form.getvalue('full_id')

cur.execute('''select image_name, date from Board_images 
        join Board on Board.board_id=Board_images.board_id 
        where Board.full_id="%s" and view="Top"''' % full_id)
top = cur.fetchall()
cur.execute('''select image_name, date from Board_images 
        join Board on Board.board_id=Board_images.board_id 
        where Board.full_id="%s" and view="Bottom"''' % full_id)
bottom = cur.fetchall()
ret = True

if not top:
    ret = False

if not bottom:
    ret = False

print(ret)
