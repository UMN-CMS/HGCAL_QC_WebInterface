#!/usr/bin/python3

import cgi, html
import cgitb; cgitb.enable()
import base
#import home_page_list
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

    db = connect(1)
    cur = db.cursor()

    cur.execute('select full_id from Board')
    boards = cur.fetchall()
    ld_engines = filter_boards(boards)

    csv_file = "lpgbt_ld_eng_241220.csv"
 
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow([
            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "NAME_LABEL", "LOCATION",
            "INSTITUTION", "MANUFACTURER", "PRODUCTION_DATE", "MADE-FROM-TYPECODE[0]", 
            "MADE-FROM-SN[0]", "COMMENT_DESCRIPTION", "ATTRIBUTE-NAME[0]", "ATTRIBUTE-VALUE[0]",
        ])

        initial_count = 4000381
        for barcode in ld_engines:

            # GET LPGBT IDs
            cur.execute('select board_id from Board where full_id="%s"' % barcode)
            board_id_result = cur.fetchall()
            board_id = board_id_result[0][0]

            cur.execute('select test_id from Test where test_type_id=22 and board_id="%s"' % board_id) #lpgbt 
            test_id_result = cur.fetchall()
            if test_id_result: 
                test_id = test_id_result[0][0]
                cur.execute('Select attach from Attachments where test_id="%s"' % test_id)
                lpgbt_ids_result = cur.fetchall()
                if lpgbt_ids_result:
                    lpgbt_ids = lpgbt_ids_result[0][0]
                    lpgbt_ids = extract_ids(lpgbt_ids)
                    if lpgbt_ids is not None:
                        for loc, lpgbt in lpgbt_ids:
                            label_typecode = "IC-LPG"
                            serial_number = f"{lpgbt}"
                            bc = serial_number
                            name_label = f"LPGBT {loc} 0x{serial_number}"
                            location = "UMN"
                            institution = "UMN"
                            manufacturer = "TSMC"
                            production_date = "2024-04-24"
                            made_from_typecode0 = "IC-LPS"
                            made_from_sn0 = initial_count
                            comment_description = f"{loc} LPGBT for {barcode}"
                            attribute_name0 = "lpGBT Location LD Engine"
                            if loc == "E" or loc == "W":
                                loc = f"TRIG-{loc}"
                            attribute_value0 = loc
                            # Write the row to the CSV
                            writer.writerow([
                                label_typecode, serial_number, bc, name_label, location,
                                institution, manufacturer, production_date, made_from_typecode0,
                                made_from_sn0, comment_description, attribute_name0, attribute_value0
                            ])
                   

                            initial_count += 1
                    else:
                        continue
                else:
                    continue
            else:
                continue
#                            print(label_typecode, serial_number, name_label, made_from_typecode0, made_from_sn0, comment_description, attribute_value0)

        print(f"CSV file '{csv_file}' created successfully.")
#    base.bottom(True)

def filter_boards(board_list):
    # Define boards to exclude
    exclude_boards = {
    "320EL10W1010002", "320EL10W1010005", "320EL10W1010004",
    "320EL10W1010006", "320EL10E1010004", "320EL10E1010005",
    "320EL10E1010008", "320EL10E1010001", "320EL10E1010003",
    "320EL10E1010006",
    "320EL10W1010073", "320EL10W1010055", "320EL10W1010045",
    "320EL10W1010040", "320EL10W1010038", "320EL10W1010036",
    "320EL10W1010013", "320EL10W1010011",
    "320EL10E1010069", "320EL10E1010065", "320EL10E1010064",
    "320EL10E1010056", "320EL10E1010048", "320EL10E1010045",
    "320EL10E1010038",
    }

    # Filter the list for boards starting with '320EL10' and not in the exclusion list
    filtered_boards = [
        board[0] for board in board_list 
        if board[0].startswith('320EL10') and board[0] not in exclude_boards
    ]
    return filtered_boards

def extract_ids(byte_data):
    json_str = byte_data.decode('utf-8')
    data_dict = json.loads(json_str)

    test_data = data_dict['test_data']

    if not test_data or all('id' not in value for value in test_data.values()):
        return None

    # Extracting tuples with the name and id
    id_list = [(key, f"{value['id']:08x}".upper()) for key, value in test_data.items() if 'id' in value]
    return id_list

#def extract_ids(byte_data):
#    json_str = byte_data.decode('utf-8')
#    data_dict = json.loads(json_str)
    
#    test_data = data_dict['test_data']
#
#    print(test_data)
#    if not test_data or all('id' not in value for value in test_data.values()):
#        return None

#    id_list = [f"{value['id']:08x}".upper() for key, value in test_data.items() if 'id' in value]
#
#    return id_list

if __name__ == '__main__':
    print("Content-type: text/html\n")
    run()
