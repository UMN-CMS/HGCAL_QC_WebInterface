#!/usr/bin/python3

import json 
import csv
import logging
import argparse
from connect import connect

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
LOCATION = "UMN"
INSTITUTION = "UMN"

# Helper Functions
def filter_boards(cur) -> list:
    """Fetch and filter board IDs that start with '320WW' or '320WE'."""
    try:
        cur.execute('SELECT full_id FROM Board')
        return [board[0] for board in cur.fetchall() if board[0].startswith('320WW') or board[0].startswith('320WE')]
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
            'SELECT test_id FROM Test WHERE test_type_id = 7 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (board_id,)
        )
        test_id_result = cur.fetchall()
        return test_id_result
    except Exception as e:
        logger.error(f"Error checking if board is registered for barcode {barcode}: {e}")
        return None

def get_typecode(cur, barcode):
    """Function to make a typcode (e.g WE-10A1)."""
    try:
        cur.execute('SELECT type_id FROM Board WHERE full_id = %s', (barcode,))
        type_id_result = cur.fetchone()
        if not type_id_result:
            logger.warning(f"No type ID found for barcode {barcode}")
            return None
        type_id = type_id_result[0]

        # Insert a hyphen after the first two characters
        if len(type_id) > 2:
            formatted_type_id = type_id[:2] + '-' + type_id[2:]
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
        name = name_result[0]

        # Split the name by hyphen and return the second word
        name_parts = name.split('-')
        if len(name_parts) < 2:
            logger.warning(f"Manufacturer name '{name}' does not contain a hyphen")
            return None
        return name_parts[1].strip()
    except Exception as e:
        logger.error(f"Error getting manufacturer for barcode {barcode}: {e}")
        return None


def get_name(barcode):
    """Generate a name label for the barcode."""
    return f"LD Wagon {barcode[4]} {barcode}"

def get_date(typecode):
    """Determine the production date based on typcode."""
    first_group = {"WE-10A1", "WE-20A1", "WW-10A1", "WW-20A1", "WE-20B1"}
    second_group = {"WE-11A1", "WE-12A1", "WW-11A1", "WW-12A1"}
    return "2024-06-01" if typecode in first_group else "2024-09-01" if typecode in second_group else "UNKNOWN"

def get_batch(cur, barcode):
    """Get the full SN of the barcode, parse it to determine the board batch."""
    try:
        cur.execute('SELECT sn FROM Board WHERE full_id = %s', (barcode,))
        sn_result = cur.fetchone()
        if not sn_result:
            logger.warning(f"No serial number (sn) found for barcode {barcode}")
            return None
        sn = sn_result[0]

        # Return the second character of the sn, which is the batch character.
        if len(sn) >= 2:
            return sn[1]
        else:
            logger.warning(f"Serial number '{sn}' is too short to extract the second character")
            return None
    except Exception as e:
        logger.error(f"Error getting second character from serial number for barcode {barcode}: {e}")
        return None

def get_description(batch):
    """Check if the batch character is a number or a letter to assign a comment field."""
    return "Pre-series" if batch.isdigit() else "Pre-production" if batch.isalpha() else "None"
 
def run(csv_file):
    """Main execution function."""
    try:
        db = connect(0)
        cur = db.cursor()

        all_ld_wagons = filter_boards(cur)

        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header row
            writer.writerow([
                "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION",
                "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
	        "BATCH_NUMBER", "COMMENT_DESCRIPTION", 
            ])

            success = 0

            for barcode in all_ld_wagons:
                logger.info(f"Processing barcode: {barcode}")
                
                if check_if_registered(cur, barcode):
                    logger.info(f"Skipping {barcode}, already registered")
                    continue

                label_typecode = get_typecode(cur, barcode)
                manufacturer = get_manufacturer(cur, barcode)
                batch = get_batch(cur, barcode)
                name_label = get_name(barcode)
                production_date = get_date(label_typecode)
                comment = get_description(batch)

                writer.writerow([
                    label_typecode, barcode, barcode, LOCATION,
                    INSTITUTION, manufacturer, name_label, production_date,
                    batch, comment,
                ])

                success += 1

            logger.info(f"CSV file '{csv_file}' for {success} LD wagons created successfully.")

    except Exception as e:
        logger.error(f"Critical error in run function: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Register LD wagons by exporting data to a CSV file.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output CSV file name (e.g., output.csv)")
    args = parser.parse_args()

    print("Content-type: text/html\n")
    run(args.output)
