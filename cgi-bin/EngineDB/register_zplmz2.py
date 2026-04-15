#!/usr/bin/python3

"""
Produce ZP-LMZ2 and lpGBT registration CSVs and bundle them into a ZIP.

Normal mode writes EngineDB lpGBT stock usage when a new IC-LPS stock item
must be assigned. Debug/dry-run mode is fully read-only and only previews
the stock items that would be used.
"""

import argparse
import csv
import io
import json
import logging
import os
import sys
import zipfile

import cgi
import mysql.connector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from connect import connect


LOCATION = "UMN"
INSTITUTION = "UMN"
WAGON_TYPE_SN = "ZPLMZ2"
WAGON_LABEL_TYPECODE = "ZP-LMZ2"
WAGON_NAME_PREFIX = "lpGBT Mezzanine"
WAGON_COMMENT = "Production"
WAGON_PRODUCTION_DATES = {
    "2": "2026-03-23",
}

LPGBT_TYPECODE = "IC-LPG"
LPGBT_STOCK_TYPECODE = "IC-LPS"
LPGBT_ATTRIBUTE_NAME = "lpGBT Location ZP-LMZ2"
LPGBT_ATTRIBUTE_VALUE = "MEZZ"
LPGBT_TEST_NAME = "lpGBT Mezz ID"
REGISTERED_TEST_NAME = "Registered"

LPGBT_VERSIONS = {
    "0": {"manufacturer": "TSMC", "production_date": "2024-04-24"},
    "1": {"manufacturer": "TSMC", "production_date": "2024-04-24"},
    "2": {"manufacturer": "TSMC", "production_date": "2025-05-13"},
}

MANU_RENAMES = {
    "Poly": "PolyElectronics",
    "Piranha": "Piranha EMS",
    "Ninja": "Ninja Circuits",
}


def decode_blob(blob):
    if blob is None:
        return None
    if isinstance(blob, bytes):
        return blob.decode("utf-8")
    return blob


def get_registered_test_type_id(cur):
    cur.execute('SELECT test_type FROM Test_Type WHERE name = %s', (REGISTERED_TEST_NAME,))
    row = cur.fetchone()
    return row[0] if row else None


def get_lpgbt_test_type_id(cur):
    cur.execute('SELECT test_type FROM Test_Type WHERE name = %s', (LPGBT_TEST_NAME,))
    row = cur.fetchone()
    return row[0] if row else None


def get_zplmz2_boards(cur):
    cur.execute('SELECT full_id FROM Board WHERE type_id = %s ORDER BY full_id', (WAGON_TYPE_SN,))
    return [row[0] for row in cur.fetchall()]


def get_board_id(cur, barcode):
    cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    return row[0] if row else None


def is_registered(cur, barcode, registered_test_type_id):
    board_id = get_board_id(cur, barcode)
    if board_id is None or registered_test_type_id is None:
        return False
    cur.execute(
        'SELECT test_id FROM Test WHERE test_type_id = %s AND board_id = %s ORDER BY day DESC, test_id DESC',
        (registered_test_type_id, board_id),
    )
    return cur.fetchone() is not None


def get_typecode(cur, barcode):
    cur.execute('SELECT type_id FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    if not row or not row[0]:
        return None
    type_id = row[0]
    if len(type_id) <= 2:
        return None
    return f"{type_id[:2]}-{type_id[2:]}"


def get_manufacturer(cur, barcode):
    cur.execute('SELECT manufacturer_id FROM Board WHERE full_id = %s', (barcode,))
    manufacturer_row = cur.fetchone()
    if not manufacturer_row:
        return None
    cur.execute('SELECT name FROM Manufacturers WHERE manufacturer_id = %s', (manufacturer_row[0],))
    name_row = cur.fetchone()
    if not name_row or not name_row[0]:
        return None
    name_parts = name_row[0].split("-")
    if len(name_parts) < 2:
        return name_row[0]
    asm_name = name_parts[1].strip()
    return MANU_RENAMES.get(asm_name, asm_name)


def get_batch(cur, barcode):
    cur.execute('SELECT sn FROM Board WHERE full_id = %s', (barcode,))
    row = cur.fetchone()
    if not row or row[0] is None:
        return None
    sn = str(row[0])
    if len(sn) < 1:
        return None
    # EngineDB-backed ZPLMZ2 boards follow the same batch convention as
    # register_engines.py: the first SN character is the batch.
    return sn[0]


def get_production_date(batch):
    return WAGON_PRODUCTION_DATES.get(batch, "UNKNOWN")


def get_wagon_name(barcode):
    return f"{WAGON_NAME_PREFIX} {barcode}"


def get_engine_used_for(cur, barcode):
    retval = {}
    try:
        cur.execute(
            "SELECT COMPONENT_STOCK.barcode, COMPONENT_STOCK.typecode "
            "FROM COMPONENT_STOCK "
            "JOIN COMPONENT_USAGE ON COMPONENT_STOCK.component_id = COMPONENT_USAGE.component_id "
            "WHERE COMPONENT_USAGE.used_in_barcode = %s",
            (barcode,),
        )
        for stock_barcode, typecode in cur.fetchall():
            retval.setdefault(typecode, []).append(stock_barcode)
        return 200, retval
    except mysql.connector.Error as exc:
        return 400, f"Error on get_used_for: {exc}"


def get_engine_unused_stock(cur, typecode, quantity=1):
    try:
        quantity = int(quantity)
        if typecode is None:
            cur.execute(
                "SELECT typecode, barcode FROM COMPONENT_STOCK "
                "WHERE component_id NOT IN (SELECT component_id FROM COMPONENT_USAGE) "
                f"ORDER BY barcode LIMIT {quantity}"
            )
            return 200, cur.fetchall()

        cur.execute(
            "SELECT barcode FROM COMPONENT_STOCK "
            "WHERE typecode = %s AND component_id NOT IN (SELECT component_id FROM COMPONENT_USAGE) "
            f"ORDER BY barcode LIMIT {quantity}",
            (typecode,),
        )
        return 200, cur.fetchall()
    except mysql.connector.Error as exc:
        return 400, f"Error on get_unused_stock: {exc}"


def mark_engine_stock_used(ctx, cur, stock_barcode, used_in_barcode):
    try:
        cur.execute("SELECT component_id FROM COMPONENT_STOCK WHERE barcode = %s", (stock_barcode,))
        row = cur.fetchone()
        if row is None:
            return 404, f"Barcode '{stock_barcode}' not found in stock"

        component_id = int(row[0])
        if used_in_barcode is not None:
            cur.execute(
                "INSERT INTO COMPONENT_USAGE (component_id, used_in_barcode) VALUES (%s, %s)",
                (component_id, used_in_barcode),
            )
        else:
            cur.execute("INSERT INTO COMPONENT_USAGE (component_id) VALUES (%s)", (component_id,))
        ctx.commit()
        return 200, "Ok"
    except mysql.connector.Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return 409, f"Barcode {stock_barcode} already used to make something else"
        return 400, f"Error on mark_used: {exc}"


def get_latest_lpgbt_id(cur, barcode, lpgbt_test_type_id):
    board_id = get_board_id(cur, barcode)
    if board_id is None:
        logger.warning("No EngineDB board found for %s", barcode)
        return None

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
            logger.error("Invalid lpGBT ID payload for %s: %r", barcode, lpgbt_block.get("id"))
            return None

    test_data = payload.get("test_data")
    if isinstance(test_data, dict):
        lpgbt_block = test_data.get("LPGBT")
        if isinstance(lpgbt_block, dict) and "id" in lpgbt_block:
            try:
                return f"{int(lpgbt_block['id']):08X}"
            except (TypeError, ValueError):
                logger.error("Invalid nested lpGBT ID payload for %s: %r", barcode, lpgbt_block.get("id"))
                return None

    logger.error("Could not find LPGBT.id in attachment payload for %s", barcode)
    return None


def build_board_lpgbt_map(engine_cur, boards, lpgbt_test_type_id):
    candidate_ids = {}
    duplicates = set()

    for barcode in boards:
        lpgbt_id = get_latest_lpgbt_id(engine_cur, barcode, lpgbt_test_type_id)
        if lpgbt_id is None:
            continue
        if lpgbt_id in candidate_ids.values():
            duplicates.add(lpgbt_id)
        candidate_ids[barcode] = lpgbt_id

    valid = {}
    reverse = {}
    for barcode, lpgbt_id in candidate_ids.items():
        if lpgbt_id in duplicates:
            logger.error("Skipping %s because lpGBT ID %s is duplicated across ZPLMZ2 boards", barcode, lpgbt_id)
            continue
        valid[barcode] = lpgbt_id
        reverse[lpgbt_id] = barcode

    logger.info(
        "Selected %d ZPLMZ2 boards with a successful '%s' test",
        len(valid),
        LPGBT_TEST_NAME,
    )
    return valid, reverse


def filter_exportable_boards(source_cur, board_to_lpgbt):
    filtered = {}

    for barcode, lpgbt_id in sorted(board_to_lpgbt.items()):
        missing = []
        if get_typecode(source_cur, barcode) is None:
            missing.append("typecode")
        if get_manufacturer(source_cur, barcode) is None:
            missing.append("manufacturer")
        if get_batch(source_cur, barcode) is None:
            missing.append("batch")
        if len(barcode) <= 8 or barcode[8] not in LPGBT_VERSIONS:
            missing.append("supported lpGBT version")

        if missing:
            logger.warning("Skipping %s because it is missing %s", barcode, ", ".join(missing))
            continue

        filtered[barcode] = lpgbt_id

    return filtered


def build_board_csv(source_cur, board_to_lpgbt):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION", "INSTITUTION",
        "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE", "BATCH_NUMBER",
        "COMMENT_DESCRIPTION", "MADE-FROM-TYPECODE[0]", "MADE-FROM-SN[0]",
    ])

    count = 0
    for barcode in sorted(board_to_lpgbt):
        typecode = get_typecode(source_cur, barcode)
        manufacturer = get_manufacturer(source_cur, barcode)
        batch = get_batch(source_cur, barcode)
        lpgbt_id = board_to_lpgbt[barcode]

        missing = []
        if typecode is None:
            missing.append("typecode")
        if manufacturer is None:
            missing.append("manufacturer")
        if batch is None:
            missing.append("batch")
        if missing:
            logger.warning("Skipping %s from board CSV: missing %s", barcode, ", ".join(missing))
            continue

        writer.writerow([
            WAGON_LABEL_TYPECODE,
            barcode,
            barcode,
            LOCATION,
            INSTITUTION,
            manufacturer,
            get_wagon_name(barcode),
            get_production_date(batch),
            batch,
            WAGON_COMMENT,
            LPGBT_TYPECODE,
            lpgbt_id,
        ])
        count += 1

    logger.info("ZPLMZ2 board CSV: prepared %d entries", count)
    buf.seek(0)
    return buf


def assign_stock_serial(engine_read_cur, engine_write_connect, board_to_lpgbt, debug):
    needed = len(board_to_lpgbt)
    status, stock_list = get_engine_unused_stock(engine_read_cur, LPGBT_STOCK_TYPECODE, quantity=needed)
    if status != 200:
        raise RuntimeError(f"Failed to fetch unused {LPGBT_STOCK_TYPECODE} stock: {stock_list}")

    stock_iter = iter(stock_list)
    assignments = {}

    for barcode in sorted(board_to_lpgbt):
        lpgbt_id = board_to_lpgbt[barcode]
        status, used_map = get_engine_used_for(engine_read_cur, lpgbt_id)
        if status != 200:
            raise RuntimeError(f"Failed to inspect existing stock for {lpgbt_id}: {used_map}")

        existing = None
        if LPGBT_STOCK_TYPECODE in used_map and used_map[LPGBT_STOCK_TYPECODE]:
            existing = used_map[LPGBT_STOCK_TYPECODE][0]

        if existing:
            assignments[lpgbt_id] = existing
            logger.info("Reusing existing stock %s -> %s", existing, lpgbt_id)
            continue

        try:
            next_row = next(stock_iter)
        except StopIteration as exc:
            raise RuntimeError("Insufficient IC-LPS stock for all ZPLMZ2 lpGBTs") from exc

        full_serial = next_row[0] if isinstance(next_row, tuple) else next_row
        assignments[lpgbt_id] = full_serial

        if debug:
            logger.info("WOULD ASSIGN stock %s -> %s", full_serial, lpgbt_id)
            continue

        if engine_write_connect is None:
            raise RuntimeError("Write connection was not opened in commit mode")

        write_cur = engine_write_connect.cursor(buffered=True)
        mk_status, mk_msg = mark_engine_stock_used(engine_write_connect, write_cur, full_serial, lpgbt_id)
        write_cur.close()
        if mk_status != 200:
            raise RuntimeError(f"Failed to mark {full_serial} used→{lpgbt_id}: {mk_msg}")
        logger.info("Assigned new stock %s -> %s", full_serial, lpgbt_id)

    return assignments


def build_lpgbt_csv(board_to_lpgbt, lpgbt_to_board, stock_assignments):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "NAME_LABEL",
        "LOCATION", "INSTITUTION", "MANUFACTURER", "PRODUCTION_DATE",
        "VERSION", "MADE-FROM-TYPECODE[0]", "MADE-FROM-SN[0]",
        "COMMENT_DESCRIPTION", "ATTRIBUTE-NAME[0]", "ATTRIBUTE-VALUE[0]",
    ])

    count = 0
    for lpgbt_id in sorted(lpgbt_to_board):
        barcode = lpgbt_to_board[lpgbt_id]
        version_char = barcode[8]
        version_info = LPGBT_VERSIONS.get(version_char)
        if version_info is None:
            logger.warning("Skipping lpGBT %s for %s: unknown lpGBT version '%s'", lpgbt_id, barcode, version_char)
            continue

        full_serial = stock_assignments.get(lpgbt_id)
        if not full_serial:
            logger.warning("Skipping lpGBT %s for %s: no IC-LPS stock assignment available", lpgbt_id, barcode)
            continue

        writer.writerow([
            LPGBT_TYPECODE,
            lpgbt_id,
            lpgbt_id,
            f"LPGBT MEZZ 0x{lpgbt_id}",
            LOCATION,
            INSTITUTION,
            version_info["manufacturer"],
            version_info["production_date"],
            version_char,
            LPGBT_STOCK_TYPECODE,
            full_serial[-7:],
            f"MEZZ LPGBT for {barcode}",
            LPGBT_ATTRIBUTE_NAME,
            LPGBT_ATTRIBUTE_VALUE,
        ])
        count += 1

    logger.info("ZPLMZ2 lpGBT CSV: prepared %d entries", count)
    buf.seek(0)
    return buf


def make_zip(debug=False):
    engine_read_db = connect(0)
    engine_read_cur = engine_read_db.cursor(buffered=True)
    engine_write_db = None

    try:
        registered_test_type_id = get_registered_test_type_id(engine_read_cur)
        if registered_test_type_id is None:
            raise RuntimeError(f"Could not find EngineDB test type '{REGISTERED_TEST_NAME}'")

        lpgbt_test_type_id = get_lpgbt_test_type_id(engine_read_cur)
        if lpgbt_test_type_id is None:
            raise RuntimeError(f"Could not find EngineDB test type '{LPGBT_TEST_NAME}'")

        boards = get_zplmz2_boards(engine_read_cur)
        unregistered_boards = []
        for barcode in boards:
            if is_registered(engine_read_cur, barcode, registered_test_type_id):
                logger.info("Skipping %s, already registered in EngineDB", barcode)
                continue
            unregistered_boards.append(barcode)

        board_to_lpgbt, _ = build_board_lpgbt_map(engine_read_cur, unregistered_boards, lpgbt_test_type_id)
        board_to_lpgbt = filter_exportable_boards(engine_read_cur, board_to_lpgbt)
        lpgbt_to_board = {lpgbt_id: barcode for barcode, lpgbt_id in board_to_lpgbt.items()}

        board_buf = build_board_csv(engine_read_cur, board_to_lpgbt)
        if not debug and board_to_lpgbt:
            engine_write_db = connect(1)

        stock_assignments = assign_stock_serial(engine_read_cur, engine_write_db, board_to_lpgbt, debug)
        lpgbt_buf = build_lpgbt_csv(board_to_lpgbt, lpgbt_to_board, stock_assignments)

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("zplmz2_boards.csv", board_buf.getvalue())
            zf.writestr("zplmz2_lpgbts.csv", lpgbt_buf.getvalue())

        return zip_buf.getvalue()
    finally:
        engine_read_cur.close()
        engine_read_db.close()
        if engine_write_db is not None:
            engine_write_db.close()


def parse_debug_flag(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def run_cli():
    parser = argparse.ArgumentParser(
        description="Produce ZPLMZ2 and lpGBT registration CSVs and bundle them into a ZIP."
    )
    parser.add_argument(
        "--debug",
        "--dry-run",
        action="store_true",
        dest="debug",
        help="Preview lpGBT stock assignments without writing to EngineDB",
    )
    parser.add_argument(
        "-z",
        "--zip-out",
        default=None,
        help='Output ZIP filename. Defaults to "zplmz2_register.zip".',
    )
    args = parser.parse_args()

    zip_name = args.zip_out or "zplmz2_register.zip"
    zip_data = make_zip(debug=args.debug)
    with open(zip_name, "wb") as handle:
        handle.write(zip_data)
    logger.info("Wrote %s%s", zip_name, " (debug mode)" if args.debug else "")


def run_cgi():
    form = cgi.FieldStorage()
    debug = parse_debug_flag(form.getfirst("debug", "0"))
    zip_data = make_zip(debug=debug)

    print("Content-type: application/zip")
    print('Content-disposition: attachment; filename="zplmz2_register.zip"\n')
    sys.stdout.flush()
    sys.stdout.buffer.write(zip_data)


if __name__ == "__main__":
    if "REQUEST_METHOD" in os.environ:
        run_cgi()
    else:
        run_cli()
