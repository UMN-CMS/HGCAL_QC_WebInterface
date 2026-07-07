#!/usr/bin/python3

import sys
import os
import json 
import csv
import argparse
from connect import connect

def run(csv_file):
    db = connect(0)
    cur = db.cursor()
    ofile = None

    if csv_file is None:
        writer = csv.writer(sys.stdout)
    else:
        ofile = open(csv_file, mode='w', newline='')
        writer = csv.writer(ofile)

    # Write the header row
    writer.writerow([
        "BARCODE", "GRADE", "GRADE COMMENT",
    ])

    cur.execute('''
    SELECT B.full_id, G.grade, G.comments
    FROM Board B JOIN Grades G
    ON B.board_id=G.board_id
            ''')

    writer.writerows(cur.fetchall())

    if ofile is not None:
        ofile.close()


if __name__ == '__main__':
    if "REQUEST_METHOD" in os.environ:
        import cgi, html
        print("Content-type: text/csv")
        print('Content-disposition: attachment; filename="wagon_grades.csv"\n')
        run(None)

    else: # Commandline
        parser = argparse.ArgumentParser(description="Get boards and their corresponding grades by exporting data to a CSV file.")
        parser.add_argument("-o", "--output", type=str, default=None, help="Output CSV file name (e.g., output.csv)")
        args = parser.parse_args()

        run(args.output)

