#!/usr/bin/python3

import json 
import csv
import logging
import argparse
from connect import connect

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Common Hardcodes
LOCATION = "UMN"
INSTITUTION = "UMN"
LPGBT_TYPECODE = "IC-LPG"

# Engine Specific Hardcodes
ENGINE_PRODUCTION_DATE = "2024-08-07"
COMMENT_DESCRIPTION = "Preproduction"

# LPGBT Specific Hardcodes
LPGBT_MANUFACTURER = "TSMC"
LPGBT_PRODUCTION_DATE = "2024-04-24"

# Helper Functions
def filter_boards(cur) -> list:
    """Fetch and filter board IDs that start with '320EH0QF' (HD Full Engines)."""
    try:
        cur.execute('SELECT full_id FROM Board')
        return [board[0] for board in cur.fetchall() if board[0].startswith('320EH0QF')]
    except Exception as e:
        logger.error(f"Error fetching board IDs: {e}")
        return []

def check_if_registered(cur, barcode):
    """Check if board is already registered."""
    try:
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        board_id_result = cur.fetchall()
        board_id = board_id_result[0][0]

        cur.execute(
            'SELECT test_id FROM Test WHERE test_type_id = 26 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (board_id,)
        )
        test_id_result = cur.fetchall()
        return test_id_result
    except Exception as e:
        logger.error(f"Error checking if board is registered for barcode {barcode}: {e}")
        return None

def get_typecode(cur, barcode):
    """Function to make a typcode (e.g EL-10E)."""
    try:
        cur.execute('SELECT type_id FROM Board WHERE full_id = %s', (barcode,))
        type_id_result = cur.fetchone()
        if not type_id_result:
            logger.warning(f"No type ID found for barcode {barcode}")
            return None
        type_id = type_id_result[0]

        # Insert a hyphen after the first two characters
        if len(type_id) > 2:
            formatted_type_id = type_id[:2] + '-' + type_id[2:5] #ENGINEDB_PRO gives EL-10E1 as the type_id, DB uses EL-10E
        else:
            logger.warning(f"Type ID '{type_id}' is too short to format")
            return None
        return formatted_type_id
    except Exception as e:
        logger.error(f"Error getting formatted type ID for barcode {barcode}: {e}")
        return None

def get_manufacturer(cur, barcode):
    try:
        # Fetch the manufacturer_id associated with the barcode
        cur.execute('SELECT manufacturer_id FROM Board WHERE full_id = %s', (barcode,))
        manufacturer_id_result = cur.fetchone()
        if not manufacturer_id_result:
            logger.warning(f"No manufacturer ID found for barcode {barcode}")
            return None
        manufacturer_id = manufacturer_id_result[0]

        # Fetch the name from the Manufacturers table
        cur.execute('SELECT name FROM Manufacturers WHERE manufacturer_id = %s', (manufacturer_id,))
        name_result = cur.fetchone()
        if not name_result:
            logger.warning(f"No manufacturer name found for manufacturer ID {manufacturer_id}")
            return None
        else:
            return name_result[0]

        # Split the name by hyphen and return the second word (e.g. TTM-Caltronics)
        name_parts = name.split('-')
        if len(name_parts) < 2:
            logger.warning(f"Manufacturer name '{name}' does not contain a hyphen")
            return None
        return name_parts[1].strip()
    except Exception as e:
        logger.error(f"Error getting manufacturer for barcode {barcode}: {e}")
        return None

def get_batch(cur, barcode):
    """Get the full SN of the barcode, parse it to determine the board batch."""
    try:
        cur.execute('SELECT sn FROM Board WHERE full_id = %s', (barcode,))
        sn_result = cur.fetchone()
        if not sn_result:
            logger.warning(f"No serial number (sn) found for barcode {barcode}")
            return None
        sn = str(sn_result[0])

        # Return the second character of the sn, which is the batch character.
        if len(sn) > 0:
            return sn[0]
        else:
            logger.warning(f"Serial number '{sn}' is too short to extract the second character")
            return None
    except Exception as e:
        logger.error(f"Error getting second character from serial number for barcode {barcode}: {e}")
        return None

def get_name(barcode):
    """Generate a name label for the barcode."""
    return f"HD Engine {barcode[7]} {barcode}"

def get_lpgbt_ids(cur, barcode):
    """
    Retrieve LPGBT IDs for a given barcode.
    """
    try:
        # Fetch the board ID associated with the barcode
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        board_id_result = cur.fetchall()
        if not board_id_result:
            return None
        
        board_id = board_id_result[0][0]

        # Fetch the most recent test ID for LPGBT
        cur.execute(
            'SELECT test_id FROM Test WHERE test_type_id = 22 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (board_id,)
        )
        test_id_result = cur.fetchall()
        if not test_id_result:
            return None
        
        test_id = test_id_result[0][0]

        # Fetch the attached LPGBT IDs
        cur.execute('SELECT attach FROM Attachments WHERE test_id = %s', (test_id,))
        lpgbt_ids_result = cur.fetchall()
        if not lpgbt_ids_result:
            return None
        
        lpgbt_ids = lpgbt_ids_result[0][0]
        return extract_ids(lpgbt_ids)
    except Exception as e:
        logger.error(f"Error retrieving LPGBT IDs for barcode {barcode}: {e}")
        return None

def extract_ids(byte_data):
    json_str = byte_data.decode('utf-8')
    data_dict = json.loads(json_str)

    test_data = data_dict['test_data']

    if not test_data or all('id' not in value for value in test_data.values()):
        return None

    id_list = [(key, f"{value['id']:08x}".upper()) for key, value in test_data.items() if 'id' in value]
    return id_list

def get_ldo_id(cur, barcode):
    """
    Retrieve the LDO ID for a given barcode.
    """
    try:
        cur.execute('SELECT LDO FROM Board WHERE full_id = %s', (barcode,))
        ldo_result = cur.fetchone()
        return ldo_result[0] if ldo_result else None
    except Exception as e:
        logger.error(f"Error retrieving LDO ID for barcode {barcode}: {e}")
        return None

def get_bare_code(barcode):
    """
    Generate the Bare Code from the given barcode.
    """
    try:
        zero_index = barcode.find('0', barcode.find('0') + 1)
        if zero_index == -1:
            logger.warning(f"Invalid barcode format: {barcode}")
            return None, None

        bare_code = barcode[:zero_index] + 'B' + barcode[zero_index + 1:]
        made_from_typecode = f"{bare_code[3:5]}-{bare_code[5:8]}"
        return made_from_typecode, bare_code
    except Exception as e:
        logger.error(f"Error generating Bare Code for barcode {barcode}: {e}")
        return None, None

def engine_file(csv_file):
    """Main execution function to make the engine CSV file."""
    try:
        db = connect(1)
        cur = db.cursor()

        all_ld_engines = filter_boards(cur)

        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow([
                "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION",
                "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
	        "BATCH_NUMBER", "COMMENT_DESCRIPTION", "MADE-FROM-TYPECODE[0]", 
                "MADE-FROM-SN[0]", "MADE-FROM-TYPECODE[1]", "MADE-FROM-SN[1]",
                "MADE-FROM-TYPECODE[2]", "MADE-FROM-SN[2]", "MADE-FROM-TYPECODE[3]",
	        "MADE-FROM-SN[3]", "MADE-FROM-TYPECODE[4]", "MADE-FROM-SN[4]", 
                "MADE-FROM-TYPECODE[5]", "MADE-FROM-SN[5]", "MADE-FROM-TYPECODE[6]", 
                "MADE-FROM-SN[6]", "MADE-FROM-TYPECODE[7]", "MADE-FROM-SN[7]",
            ])

            success = 0

            for barcode in all_ld_engines:
#                logger.info(f"Processing barcode: {barcode}")
                if check_if_registered(cur, barcode):
#                    logger.info(f"Skipping {barcode}, already registered")
                    continue

                label_typecode = get_typecode(cur, barcode)
                manufacturer = get_manufacturer(cur, barcode)
                batch_number = get_batch(cur, barcode)
                name_label = get_name(barcode)
                 
                # Retrieve LPGBT IDs
                lpgbt_ids = get_lpgbt_ids(cur, barcode)
                if not lpgbt_ids:
                    continue

                made_from_components = [
                    (LPGBT_TYPECODE, lpgbt_ids[0][1]),
                    (LPGBT_TYPECODE, lpgbt_ids[1][1]),
                    (LPGBT_TYPECODE, lpgbt_ids[2][1]),
                    (LPGBT_TYPECODE, lpgbt_ids[3][1]),
                    (LPGBT_TYPECODE, lpgbt_ids[4][1]),
                    (LPGBT_TYPECODE, lpgbt_ids[5][1]),
                ]

                # Retrieve LDO ID
                ldo = get_ldo_id(cur, barcode)
                if not ldo: 
                    logger.info(f"Skipping {barcode}, no LDO found.")
                    continue  # Skip if no LDO found

                made_from_components.append(("IC-LDH", ldo))

               # Retrieve Bare Code
                made_from_typecode4, made_from_sn4 = get_bare_code(barcode)
                if not made_from_typecode4 or not made_from_sn4:
                    continue  # Skip if Bare Code cannot be generated

                made_from_components.append((made_from_typecode4, made_from_sn4))
                   
                writer.writerow([
                    label_typecode, barcode, barcode, LOCATION, INSTITUTION, 
                    manufacturer, name_label, ENGINE_PRODUCTION_DATE, batch_number, 
                    COMMENT_DESCRIPTION,
                    *(item for sublist in made_from_components for item in sublist)
                ])

                success += 1

            logger.info(f"Created CSV file '{csv_file}' for {success} engines.")

    except Exception as e:
        logger.error(f"Error in engine file: {e}")

def lpgbt_file(csv_file, LPGBT_INDEX):
    """Main execution function to make the lpgbt CSV file."""
    lpgbt_csv_file = f"LPGBT_{csv_file}"
    try:
        db = connect(1)
        cur = db.cursor()

        all_ld_engines = filter_boards(cur)

        with open(lpgbt_csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header row
            writer.writerow([
                "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "NAME_LABEL", "LOCATION",
                "INSTITUTION", "MANUFACTURER", "PRODUCTION_DATE", "MADE-FROM-TYPECODE[0]",
                "MADE-FROM-SN[0]", "COMMENT_DESCRIPTION", "ATTRIBUTE-NAME[0]", "ATTRIBUTE-VALUE[0]",
            ])

            success = 0

            for barcode in all_ld_engines:
#                logger.info(f"Processing barcode: {barcode}")
                if check_if_registered(cur, barcode):
#                    logger.info(f"Skipping {barcode}, already registered")
                    continue


                # Retrieve LPGBT IDs
                lpgbt_ids = get_lpgbt_ids(cur, barcode)
                if not lpgbt_ids:
                    continue

		# Retrieve LDO ID
                ldo = get_ldo_id(cur, barcode)
                if not ldo:
                    logger.info(f"Skipping {barcode}, no LDO found.")
                    continue  # Skip if no LDO found

                for loc, lpgbt in lpgbt_ids:
                    serial_number = f"{lpgbt}"
                    bc = serial_number
                    name_label = f"LPGBT {loc} 0x{serial_number}"
                    made_from_typecode0 = "IC-LPS"
                    made_from_sn0 = LPGBT_INDEX 
                    comment_description = f"{loc} LPGBT for {barcode}"
                    attribute_name0 = "lpGBT Location HD Engine"
                    if loc == "E" or loc == "W":
                        loc = f"TRIG-{loc}"
                    attribute_value0 = loc

                    # Write the row to the CSV
                    writer.writerow([
                        LPGBT_TYPECODE, serial_number, bc, name_label, LOCATION,
                        INSTITUTION, LPGBT_MANUFACTURER, LPGBT_PRODUCTION_DATE, made_from_typecode0,
                        made_from_sn0, comment_description, attribute_name0, attribute_value0
                    ])
                    success += 1
                    LPGBT_INDEX += 1
            logger.info(f"Created LpGBT CSV file '{lpgbt_csv_file}' for {success} LpGBTs.")
    except Exception as e:
        logger.error(f"Error in LpGBT file: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Register LD engines and LpGBTs by exporting data to CSV files.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output CSV file name (e.g., output.csv)")
    parser.add_argument("-l", "--lpgbt", type=int, required=True, help="Starting LpGBT index (find from the last upload)")
    args = parser.parse_args()

    engine_file(args.output)
    lpgbt_file(args.output, args.lpgbt)
