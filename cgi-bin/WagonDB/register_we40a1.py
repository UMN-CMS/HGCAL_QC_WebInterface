#!/usr/bin/python3

"""
Produce a WE-40A1 (4-module wagon) registration CSV.

For each unregistered WE-40A1 board in WagonDB, extracts the lpGBT ID from
the "Mod4 LMezz Id" test, then looks up the matching ZP-LMZ2 board in
EngineDB by lpGBT ID. The CSV links each WE-40A1 to its ZP-LMZ2 daughter
via the MADE-FROM columns.
"""

import argparse
import csv
import importlib.util
import io
import json
import logging
import os
import sys
from pathlib import Path

import cgi

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from connect import connect

# -------- Constants --------
LOCATION = "UMN"
INSTITUTION = "UMN"

WAGON_TYPE_PREFIX = "320WE4"
PRODUCTION_DATE = "2026-02-03"
COMMENT_DESCRIPTION = "Production"

LPGBT_TEST_NAME = "Mod4 LMezz Id"
REGISTERED_TEST_TYPE_ID = 7

ZPLMZ2_TYPE_SN = "ZPLMZ2"
ZPLMZ2_LABEL_TYPECODE = "ZP-LMZ2"
ZPLMZ2_LPGBT_TEST_NAME = "lpGBT Mezz ID"

MANU_RENAMES = {
    "Poly": "PolyElectronics",
    "Piranha": "Piranha EMS",
    "Ninja": "Ninja Circuits",
}


# -------- EngineDB connection --------
def load_enginedb_connect():
    engine_connect_path = Path(__file__).resolve().parents[1] / "EngineDB" / "connect.py"
    spec = importlib.util.spec_from_file_location("enginedb_connect_register_we40a1", engine_connect_path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f"Could not load EngineDB connect module from {engine_connect_path}")
    spec.loader.exec_module(module)
    return module.connect


engine_connect = load_enginedb_connect()


# -------- Helpers --------
def decode_blob(blob):
    if blob is None:
        return None
    if isinstance(blob, bytes):
        return blob.decode("utf-8")
    return blob


def filter_boards(cur):
    cur.execute('SELECT full_id FROM Board')
    return [row[0] for row in cur.fetchall() if row[0].startswith(WAGON_TYPE_PREFIX)]


def check_if_registered(cur, barcode):
    try:
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        board_id = cur.fetchone()[0]
        cur.execute(
            'SELECT test_id FROM Test WHERE test_type_id = %s AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (REGISTERED_TEST_TYPE_ID, board_id),
        )
        return bool(cur.fetchall())
    except Exception as e:
        logger.error(f"Error checking registration for {barcode}: {e}")
        return False


def get_typecode(cur, barcode):
    cur.execute('SELECT type_id FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    if not row or not row[0]:
        return None
    type_id = row[0]
    return f"{type_id[:2]}-{type_id[2:]}" if len(type_id) > 2 else None


def get_manufacturer(cur, barcode):
    cur.execute('SELECT manufacturer_id FROM Board WHERE full_id = %s', (barcode,))
    mid = cur.fetchone()
    if not mid:
        return None
    cur.execute('SELECT name FROM Manufacturers WHERE manufacturer_id = %s', (mid[0],))
    row = cur.fetchone()
    if not row or not row[0]:
        return None
    name_parts = row[0].split('-')
    if len(name_parts) < 2:
        return row[0]
    name_asm = name_parts[1].strip()
    return MANU_RENAMES.get(name_asm, name_asm)


def get_batch(cur, barcode):
    cur.execute('SELECT sn FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    if not row or row[0] is None:
        return None
    sn = str(row[0])
    return sn[0] if len(sn) >= 1 else None


def get_name(barcode):
    return f"4 Module Wagon {barcode}"


# -------- lpGBT ID from WagonDB (WE-40A1 test) --------
def get_lpgbt_test_type_id(cur):
    cur.execute('SELECT test_type FROM Test_Type WHERE name = %s', (LPGBT_TEST_NAME,))
    row = cur.fetchone()
    return row[0] if row else None


def get_wagon_lpgbt_id(cur, barcode, lpgbt_test_type_id):
    cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    if not row:
        return None
    board_id = row[0]

    cur.execute(
        'SELECT test_id FROM Test WHERE test_type_id = %s AND board_id = %s AND successful = 1 '
        'ORDER BY day DESC, test_id DESC',
        (lpgbt_test_type_id, board_id),
    )
    test_row = cur.fetchone()
    if not test_row:
        logger.warning("No successful '%s' test found for %s", LPGBT_TEST_NAME, barcode)
        return None

    cur.execute('SELECT attach FROM Attachments WHERE test_id = %s', (test_row[0],))
    attach_row = cur.fetchone()
    if not attach_row or attach_row[0] is None:
        logger.warning("No attachment found for %s lpGBT test", barcode)
        return None

    try:
        payload = json.loads(decode_blob(attach_row[0]))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        logger.error("Malformed lpGBT attachment JSON for %s: %s", barcode, exc)
        return None

    lpgbt_block = payload.get("LPGBT")
    if isinstance(lpgbt_block, dict) and "id" in lpgbt_block:
        try:
            return f"{int(lpgbt_block['id']):08X}"
        except (TypeError, ValueError):
            logger.error("Invalid lpGBT ID for %s: %r", barcode, lpgbt_block.get("id"))
            return None

    test_data = payload.get("test_data")
    if isinstance(test_data, dict):
        lpgbt_block = test_data.get("LPGBT")
        if isinstance(lpgbt_block, dict) and "id" in lpgbt_block:
            try:
                return f"{int(lpgbt_block['id']):08X}"
            except (TypeError, ValueError):
                logger.error("Invalid nested lpGBT ID for %s: %r", barcode, lpgbt_block.get("id"))
                return None

    logger.error("Could not find LPGBT.id in attachment for %s", barcode)
    return None


# -------- EngineDB: build ZP-LMZ2 lpGBT ID reverse map --------
def get_zplmz2_lpgbt_test_type_id(cur):
    cur.execute('SELECT test_type FROM Test_Type WHERE name = %s', (ZPLMZ2_LPGBT_TEST_NAME,))
    row = cur.fetchone()
    return row[0] if row else None


def get_zplmz2_boards(cur):
    cur.execute('SELECT full_id FROM Board WHERE type_id = %s ORDER BY full_id', (ZPLMZ2_TYPE_SN,))
    return [row[0] for row in cur.fetchall()]


def get_zplmz2_lpgbt_id(cur, barcode, lpgbt_test_type_id):
    """Get lpGBT ID for a ZP-LMZ2 board from EngineDB (same logic as register_zplmz2.py)."""
    cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    if not row:
        return None
    board_id = row[0]

    cur.execute(
        'SELECT test_id FROM Test WHERE test_type_id = %s AND board_id = %s AND successful = 1 '
        'ORDER BY day DESC, test_id DESC',
        (lpgbt_test_type_id, board_id),
    )
    test_row = cur.fetchone()
    if not test_row:
        return None

    cur.execute('SELECT attach FROM Attachments WHERE test_id = %s', (test_row[0],))
    attach_row = cur.fetchone()
    if not attach_row or attach_row[0] is None:
        return None

    try:
        payload = json.loads(decode_blob(attach_row[0]))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

    lpgbt_block = payload.get("LPGBT")
    if isinstance(lpgbt_block, dict) and "id" in lpgbt_block:
        try:
            return f"{int(lpgbt_block['id']):08X}"
        except (TypeError, ValueError):
            return None

    test_data = payload.get("test_data")
    if isinstance(test_data, dict):
        lpgbt_block = test_data.get("LPGBT")
        if isinstance(lpgbt_block, dict) and "id" in lpgbt_block:
            try:
                return f"{int(lpgbt_block['id']):08X}"
            except (TypeError, ValueError):
                return None

    return None


def build_zplmz2_lpgbt_map(engine_cur, lpgbt_test_type_id):
    """Build a map of lpgbt_id -> zplmz2_barcode from EngineDB."""
    boards = get_zplmz2_boards(engine_cur)
    lpgbt_to_zplmz2 = {}

    for barcode in boards:
        lpgbt_id = get_zplmz2_lpgbt_id(engine_cur, barcode, lpgbt_test_type_id)
        if lpgbt_id is None:
            continue
        if lpgbt_id in lpgbt_to_zplmz2:
            logger.warning(
                "Duplicate lpGBT ID %s: found on both %s and %s",
                lpgbt_id, lpgbt_to_zplmz2[lpgbt_id], barcode,
            )
            continue
        lpgbt_to_zplmz2[lpgbt_id] = barcode

    logger.info("Built ZP-LMZ2 lpGBT map with %d entries from EngineDB", len(lpgbt_to_zplmz2))
    return lpgbt_to_zplmz2


# -------- CSV generation --------
def run(csv_file, debug=False):
    wagon_db = connect(0)
    wagon_cur = wagon_db.cursor(buffered=True)

    engine_db = engine_connect(0)
    engine_cur = engine_db.cursor(buffered=True)

    try:
        # WagonDB: get lpGBT test type
        lpgbt_test_type_id = get_lpgbt_test_type_id(wagon_cur)
        if lpgbt_test_type_id is None:
            raise RuntimeError(f"Could not find WagonDB test type '{LPGBT_TEST_NAME}'")

        # EngineDB: build ZP-LMZ2 reverse map
        zplmz2_lpgbt_test_type_id = get_zplmz2_lpgbt_test_type_id(engine_cur)
        if zplmz2_lpgbt_test_type_id is None:
            raise RuntimeError(f"Could not find EngineDB test type '{ZPLMZ2_LPGBT_TEST_NAME}'")
        lpgbt_to_zplmz2 = build_zplmz2_lpgbt_map(engine_cur, zplmz2_lpgbt_test_type_id)

        # WagonDB: get WE-40A1 boards
        all_boards = filter_boards(wagon_cur)
        logger.info("Found %d WE-40A1 boards", len(all_boards))

        ofile = None
        if csv_file is None:
            writer = csv.writer(sys.stdout)
        else:
            ofile = open(csv_file, mode='w', newline='')
            writer = csv.writer(ofile)

        header = [
            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION",
            "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
            "BATCH_NUMBER", "COMMENT_DESCRIPTION",
            "MADE-FROM-TYPECODE[0]", "MADE-FROM-SN[0]",
        ]
        writer.writerow(header)

        success = 0
        for barcode in all_boards:
            if check_if_registered(wagon_cur, barcode):
                logger.info("Skipping %s, already registered", barcode)
                continue

            # Get lpGBT ID from wagon test
            lpgbt_id = get_wagon_lpgbt_id(wagon_cur, barcode, lpgbt_test_type_id)
            if lpgbt_id is None:
                logger.warning("Skipping %s: no lpGBT ID found", barcode)
                continue

            # Match to ZP-LMZ2
            zplmz2_barcode = lpgbt_to_zplmz2.get(lpgbt_id)
            if zplmz2_barcode is None:
                logger.warning("Skipping %s: no ZP-LMZ2 found for lpGBT ID %s", barcode, lpgbt_id)
                continue

            typecode = get_typecode(wagon_cur, barcode)
            manufacturer = get_manufacturer(wagon_cur, barcode)
            batch = get_batch(wagon_cur, barcode)

            if None in (typecode, manufacturer, batch):
                logger.warning("Skipping %s: missing typecode/manufacturer/batch", barcode)
                continue

            if debug:
                logger.info("WOULD REGISTER %s -> ZP-LMZ2 %s (lpGBT %s)", barcode, zplmz2_barcode, lpgbt_id)

            writer.writerow([
                typecode,
                barcode,
                barcode,
                LOCATION,
                INSTITUTION,
                manufacturer,
                get_name(barcode),
                PRODUCTION_DATE,
                batch,
                COMMENT_DESCRIPTION,
                ZPLMZ2_LABEL_TYPECODE,
                zplmz2_barcode,
            ])
            success += 1

        logger.info("CSV: wrote %d WE-40A1 entries", success)
        if ofile is not None:
            ofile.close()

    finally:
        wagon_cur.close()
        wagon_db.close()
        engine_cur.close()
        engine_db.close()


# -------- CLI / CGI --------
def run_cli():
    parser = argparse.ArgumentParser(
        description="Produce WE-40A1 (4-module wagon) registration CSV with ZP-LMZ2 daughters."
    )
    parser.add_argument("-o", "--output", type=str, default=None, help="Output CSV file name")
    parser.add_argument("--debug", "--dry-run", action="store_true", dest="debug",
                        help="Preview matches without side effects")
    args = parser.parse_args()

    if args.output is None and not args.debug:
        print("Content-type: text/csv")
        print('Content-disposition: attachment; filename="we40a1_register.csv"\n')

    run(args.output, debug=args.debug)


if __name__ == "__main__":
    if "REQUEST_METHOD" in os.environ:
        print("Content-type: text/csv")
        print('Content-disposition: attachment; filename="we40a1_register.csv"\n')
        run(None)
    else:
        run_cli()
