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
    db = connect(1)
    cur = db.cursor()

    # Input CSV file containing barcodes
    input_csv_file = "ld_eng_250113.csv"
    
    # Get barcodes from the input CSV
    barcodes_df = pd.read_csv(input_csv_file)
    barcodes = barcodes_df['BARCODE'].tolist()
    print(len(barcodes))
    csv_file = "lpgbt_ld_eng_250113.csv"

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow([
            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "NAME_LABEL", "LOCATION",
            "INSTITUTION", "MANUFACTURER", "PRODUCTION_DATE", "MADE-FROM-TYPECODE[0]",
            "MADE-FROM-SN[0]", "COMMENT_DESCRIPTION", "ATTRIBUTE-NAME[0]", "ATTRIBUTE-VALUE[0]",
        ])

        initial_count = 4000615
        for barcode in barcodes:
            print(barcode)
            # GET LPGBT IDs
            cur.execute('select board_id from Board where full_id="%s"' % barcode)
            board_id_result = cur.fetchall()
            if not board_id_result:
                print("test1")
                continue
            
            board_id = board_id_result[0][0]

            # Fetch the most recent test ID for LPGBT
            cur.execute(
                'SELECT test_id FROM Test WHERE test_type_id = 22 AND board_id = %s '
                'ORDER BY day DESC, test_id DESC',
                (board_id,)
            )
            test_id_result = cur.fetchall()
            if not test_id_result:
                print("test2")
                continue

            test_id = test_id_result[0][0]
            cur.execute('Select attach from Attachments where test_id="%s"' % test_id)
            lpgbt_ids_result = cur.fetchall()
            print("lpgbt_ids_result", lpgbt_ids_result)
            if not lpgbt_ids_result:
                print("test3")
                continue

            lpgbt_ids = extract_ids(lpgbt_ids_result[0][0])
            print("lpgbt_ids", lpgbt_ids)
            if lpgbt_ids is None:
                print("test4")
                continue

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

        print(f"CSV file '{csv_file}' created successfully.")

def extract_ids(byte_data):
    json_str = byte_data.decode('utf-8')
    data_dict = json.loads(json_str)

    test_data = data_dict['test_data']

    if not test_data or all('id' not in value for value in test_data.values()):
        return None

    # Extracting tuples with the name and id
    id_list = [(key, f"{value['id']:08x}".upper()) for key, value in test_data.items() if 'id' in value]
    return id_list

if __name__ == '__main__':
    print("Content-type: text/html\n")
    run()
