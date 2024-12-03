#!./cgi_runner.sh

import cgi
import base
import settings
import os.path
import sys
import json
import connect
import base64
import csv

# command line argument 1 is the csv file with the boards to be uploaded
# command line argument 2 is your name as it appears in the database

db=connect.connect(1)
cur=db.cursor()

filename = sys.argv[1]

cur.execute('select person_id from People where person_name="%s"' % sys.argv[2])
person_id = cur.fetchall()[0][0]

with open(filename, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    boards = list(csv_reader)
    boards = boards[1:]

    for b in boards:
        cur.execute('select board_id from Board where full_id="%s"' % b[0])
        board_id = cur.fetchall()[0][0]
        sql = "INSERT INTO Test (person_id, test_type_id, board_id, successful, comments, day) VALUES (%s,%s,%s,%s,%s,NOW())"
        print(sql % (person_id, 24, board_id, 1, ""))
        cur.execute(sql)

db.commit()
