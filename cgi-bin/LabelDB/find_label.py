#!/usr/bin/python3

from connect import connect
import mysql
import cgi
import base
import json
from add_label_functions import upload_label

#cgi header
print("Content-type: text/html\n")

# gets label from Labeling GUI and uploads it to the database

form = cgi.FieldStorage()
label = form.getvalue('labels')

label_dict = json.loads(label)

is_good = {}

cnx = connect(0)
cur = cnx.cursor()

for i, l in enumerate(label_dict.keys()):

    sql = 'SELECT * FROM Label WHERE full_label="%s"'
    cur.execute(sql, (l))

    try:
        cur.fetchall()[0][0]
        is_good[l] = False
    except Exception as e:
        is_good[l] = True

print(is_good)


