#!/usr/bin/python3

import cgi
import base
import os
from connect import connect

#cgi header
print("Content-type: text/html\n")

base.header(title='Get Manufacturers')
base.top(False)

db = connect(0)
cur = db.cursor()

cur.execute('select name from Manufacturers')
manus = cur.fetchall()

print('Begin')

for m in manus:
    print(m[0])

print('End')

base.bottom(False)
