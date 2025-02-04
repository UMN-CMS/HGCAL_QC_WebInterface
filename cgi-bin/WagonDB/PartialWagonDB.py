#!/usr/bin/python3

import cgi, html
import cgitb; cgitb.enable()
import base
import home_page_list
#import module_functions
from connect import connect
import pandas as pd
import numpy as np
import json
import csv
import argparse

def run():
#    base.header(title='Engine DB')
#    base.top(True)

    db = connect(0)
    cur = db.cursor()

    cur.execute('select full_id from Board')
    boards = cur.fetchall()
    hd_engines = filter_boards(boards)

    csv_file = "lpgbt_ids_2.csv"

#    with open(csv_file, mode='w', newline='') as file:
#        writer = csv.writer(file)

        # Write the header row
#        writer.writerow([
#            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION",
#            "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
#            "MADE-FROM-TYPECODE[0]", "MADE-FROM-SN[0]", "COMMENT_DESCRIPTION"
#        ])
#
#        lpgbt_sn = 2001
#        for eng_barcode in hd_engines:
#            cur.execute('select board_id from Board where full_id="%s"' % eng_barcode)
#            board_id_result = cur.fetchall()
###            board_id = board_id_result[0][0]
#
#            cur.execute('select test_id from Test where test_type_id=22 and board_id="%s"' % board_id)
#            test_id_result = cur.fetchall()
#            if test_id_result:
#                test_id = test_id_result[0][0]
#                cur.execute('Select attach from Attachments where test_id="%s"' % test_id)
#                lpgbt_ids_result = cur.fetchall()
#                lpgbt_ids = lpgbt_ids_result[0][0]
#
#                lpgbt_ids_dict = extract_ids(lpgbt_ids)
#
#                for lpgbt_type, sn in lpgbt_ids_dict.items():
#                    label_typecode = "IC-LPG"
#                    serial_number = sn
#                    barcode = sn
#                    location = "Minnesota"
#                    institution = "Minnesota"
#                    manufacturer = 'TSMC'
#                    name_label = f"LPGBT {lpgbt_type} {sn}"
#                    production_date = '2024-04-24'
#                    made_from_typecode = "IC-LPS"
#                    made_from_sn = lpgbt_sn
#                    comment_description = f"{lpgbt_type} LPGBT for {eng_barcode}"

                # Write the row to the CSV
#                    writer.writerow([
#                        label_typecode, serial_number, barcode, location,
#                        institution, manufacturer, name_label, production_date,
#                        made_from_typecode, made_from_sn, comment_description
#                    ])
#
#                    lpgbt_sn += 1
#
#    print(f"CSV file '{csv_file}' created successfully.")
#    base.bottom(True)

def filter_boards(board_list):
    # Filter the list for boards starting with '320EH0Q'
    filtered_boards = [board[0] for board in board_list if board[0].startswith('320')]
    return filtered_boards

#def extract_ids(byte_data):
#    json_str = byte_data.decode('utf-8')

#    data_dict = json.loads(json_str)

#    test_data = data_dict['test_data']
#    id_dict = {f"{key}": f"{value['id']:08x}" for key, value in test_data.items()}
#    id_dict = {f"{key}": f"0x{value['id']:08x}" for key, value in test_data.items()}

#    return id_dict

if __name__ == '__main__':
    print("Content-type: text/html\n")
    run()
