#!/usr/bin/env python3
"""
Produce engine- and LPGBT- registration CSVs and bundle them into a ZIP.

Usage:
    # basic invocation (outputs LD_engine_reg.zip)
    python3 register_engines.py --engine LD

    # specify a custom ZIP filename
    python3 register_engines.py --engine HDH --zip-out my_hdh_bundle.zip

Arguments:
    --engine       Required. One of: HDF, HDH, LD
    -z, --zip-out  Optional. Output ZIP filename (default: '<engine>_engine_reg.zip')

Examples:
    # Generate CSVs for HD full engines:
    python3 register_engines.py --engine HDF

    # Generate CSVs for LD engines, output to 'ld_components.zip':
    python3 register_engines.py --engine LD -z ld_components.zip
"""

import json
import csv
import logging
import argparse
from connect import connect
from components import get_unused_stock, get_used_for, mark_used
import io
import zipfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Production dates & comments by engine type & batch ----------
BATCH_INFO = {
    'HDF': {
        '1': ('2024-06-21', 'Preseries'),
        '2': ('2025-06-04', 'Production'),
    },
    'HDH': {
        '1': ('2024-06-21', 'Preseries'),
        '2': ('2025-06-06', 'Production'),
    },
    'LD': {
        '1': ('2024-11-22', 'Preproduction'),
        '2': ('2025-07-02', 'Production'),
    },
}

# ---------- Common Hardcodes ------------------
LOCATION    = "UMN"
INSTITUTION = "UMN"

# -------------- LPGBT Specific Hardcodes --------------
LPGBT_VERSIONS = {
    '0': {'manufacturer': 'TSMC', 'production_date': '2024-04-24'},
    '1': {'manufacturer': 'TSMC', 'production_date': '2024-04-24'},
    '2': {'manufacturer': 'TSMC', 'production_date': '2025-05-13'},
}

# -------- Engine-type -> prefix & LPGBT-count mapping ----------
ENGINE_CONFIG = {
    'HDF': {'prefix': '320EH0QF', 'n_lpgbts': 6},
    'HDH': {'prefix': '320EH0QH', 'n_lpgbts': 3},
    'LD' : {'prefix': '320EL',    'n_lpgbts': 3},
}

ENGINE_LABELS = {
    'HDF': 'HD Engine',
    'HDH': 'HD Engine',
    'LD' : 'LD Engine',
}

# -------------------- Helpers ------------------------------
def filter_boards(cur, prefix) -> list:
    try:
        cur.execute('SELECT full_id FROM Board')
        return [row[0] for row in cur.fetchall() if row[0].startswith(prefix)]
    except Exception as e:
        logger.error(f"Error fetching boards: {e}")
        return []

def check_if_registered(cur, barcode):
    try:
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        bid = cur.fetchone()[0]
        cur.execute(
            'SELECT test_id FROM Test '
            'WHERE test_type_id = 26 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (bid,)
        )
        return bool(cur.fetchall())
    except Exception as e:
        logger.error(f"Error checking registration for {barcode}: {e}")
        return False

def get_typecode(cur, barcode):
    try:
        cur.execute('SELECT type_id FROM Board WHERE full_id = %s', (barcode,))
        row = cur.fetchone()
        if not row:
            return None
        tid = row[0]
        return f"{tid[:2]}-{tid[2:5]}" if len(tid) > 2 else None
    except Exception as e:
        logger.error(f"Error getting typecode for {barcode}: {e}")
        return None

def get_manufacturer(cur, barcode):
    try:
        cur.execute('SELECT manufacturer_id FROM Board WHERE full_id = %s', (barcode,))
        mid = cur.fetchone()
        if not mid:
            return None
        cur.execute('SELECT name FROM Manufacturers WHERE manufacturer_id = %s', (mid[0],))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error getting manufacturer for {barcode}: {e}")
        return None

def get_batch(cur, barcode):
    try:
        cur.execute('SELECT sn FROM Board WHERE full_id = %s', (barcode,))
        row = cur.fetchone()
        if not row:
            return None
        sn = str(row[0])
        return sn[0] if len(sn) > 1 else None
    except Exception as e:
        logger.error(f"Error getting batch for {barcode}: {e}")
        return None

def get_name(barcode, engine_type):
    prefix = {
        'HDF': 'HD Full Engine',
        'HDH': 'HD Half Engine',
        'LD' : 'LD Engine',
    }.get(engine_type, 'Engine')

    if "HD" in prefix:
        return f"{prefix} {barcode}"
    elif "LD" in prefix:
        return f"{prefix} {barcode[7]} {barcode}"

def get_lpgbt_ids(cur, barcode):
    try:
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        bid = cur.fetchone()
        if not bid:
            return []
        cur.execute(
            'SELECT test_id FROM Test '
            'WHERE test_type_id = 22 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (bid[0],)
        )
        tid = cur.fetchone()
        if not tid:
            return []
        cur.execute('SELECT attach FROM Attachments WHERE test_id = %s', (tid[0],))
        blob = cur.fetchone()
        if not blob:
            return []
        data = json.loads(blob[0].decode('utf-8'))['test_data']
        return [(loc, f"{vals['id']:08X}") for loc, vals in data.items() if 'id' in vals]
    except Exception as e:
        logger.error(f"Error retrieving LPGBT IDs for {barcode}: {e}")
        return []

def get_ldo_id(cur, barcode):
    try:
        cur.execute('SELECT LDO FROM Board WHERE full_id = %s', (barcode,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error getting LDO for {barcode}: {e}")
        return None

def get_bare_code(barcode, typecode):
    """
    barcode:   e.g. "320EL10E2020001"
    typecode:  e.g. "EL-10E"
    Returns:
      (200, (final_typecode, component_barcode))
    or
      (error_code, error_message)
    """
    # 1) open a read-only stock cursor
    stock_db  = connect(0)
    stock_cur = stock_db.cursor(prepared=True)

    # 2) check if barcode is already in use
    st, used_map = get_used_for(stock_cur, barcode)
    if st != 200:
        logger.error(f"Error checking existing stock for {barcode}: {used_map}")
        return st, f"Error checking existing usage: {used_map}"
   
    # 3) normalize "-10X" -> "-1BX"
    if len(typecode) > 4 and typecode[4] == '0':
        typecode = typecode[:4] + 'B' + typecode[5:]

    # 4) if already used, re-use
    existing = used_map.get(typecode)
    if existing:
        return 200, (typecode, existing[0])

    # 5) fetch all unused stock for this typecode
    st, stock_list = get_unused_stock(stock_cur, typecode, quantity=9999)
    if st != 200:
        return st, f"Error fetching unused stock: {stock_list}"
    # filter for matching trailing digits
    suffix = barcode[-6:]
    matches = [s for s in stock_list if s.endswith(suffix)]
    if not matches:
        return 404, f"No unused stock matching suffix {suffix} for typecode {typecode}"
    bc = matches[0]

    # 6) mark it used for this barcode
    mark_db  = connect(1)
    mark_cur = mark_db.cursor(prepared=True)
    mstatus, msg = mark_used(mark_db, mark_cur, bc, barcode)
    if mstatus != 200:
        mark_db.rollback()
        return mstatus, f"Failed to mark {bc} used→{barcode}: {msg}"

    # mark_used commits on success
    return 200, (typecode, bc)

# --- Engine CSV --------------------------------------------------
def engine_file(prefix, n_lpgbts, engine_type):
    db  = connect(0)
    cur = db.cursor(buffered=True)
    boards = filter_boards(cur, prefix)

    header = [
        "LABEL_TYPECODE","SERIAL_NUMBER","BARCODE","LOCATION","INSTITUTION",
        "MANUFACTURER","NAME_LABEL","PRODUCTION_DATE","BATCH_NUMBER",
        "COMMENT_DESCRIPTION"
    ]
    for i in range(n_lpgbts):
        header += [f"MADE-FROM-TYPECODE[{i}]", f"MADE-FROM-SN[{i}]"]
    header += [f"MADE-FROM-TYPECODE[{n_lpgbts}]", f"MADE-FROM-SN[{n_lpgbts}]"]
    header += [f"MADE-FROM-TYPECODE[{n_lpgbts+1}]", f"MADE-FROM-SN[{n_lpgbts+1}]"]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)

    written_boards = []
    count = 0
    for bc in boards:
        if check_if_registered(cur, bc):
            continue

        tc, mf, batch = get_typecode(cur, bc), get_manufacturer(cur, bc), get_batch(cur, bc)

        info = BATCH_INFO.get(engine_type, {}).get(batch)
        if info is None:
            logger.warning(f"Unknown batch '{batch}' for {engine_type} engine {bc}, skipping…")
            continue
        prod_date, comment = info

        name = get_name(bc, engine_type)
        lpgbts = get_lpgbt_ids(cur, bc)
        ldo = get_ldo_id(cur, bc)

        status, payload = get_bare_code(bc, tc)
        if status != 200:
            continue #This skips anything not 10E or 10W
        else:
            bare_tc, bare_sn = payload

        missing = []
        if tc is None:           missing.append("typecode")
        if mf is None:           missing.append("manufacturer")
        if batch is None:        missing.append("batch")
        if ldo is None:          missing.append("LDO")
        if bare_tc is None or bare_sn is None:
            missing.append("bare code")
        if len(lpgbts) < n_lpgbts:
            missing.append(f"{n_lpgbts} LPGBT IDs (got {len(lpgbts)})")
        if missing:
            logger.warning(f"Skipping {bc}: missing {', '.join(missing)}")
            continue

        row = [tc, bc, bc, LOCATION, INSTITUTION,
               mf, name, prod_date, batch,
               comment]
        for loc, lid in lpgbts[:n_lpgbts]:
            row += ["IC-LPG", lid]
        row += ["IC-LDH", str(ldo)]
        row += [bare_tc, bare_sn]

        writer.writerow(row)
        written_boards.append(bc)
        count += 1

    logger.info(f"Engine CSV: prepared {count} entries")
    buf.seek(0)
    return buf, written_boards

# ------ LPGBT CSV using unused stock --------------------------
def lpgbt_file(prefix, engine_type, boards):
    db  = connect(0)
    cur = db.cursor(buffered=True)

    logger.info("Fetching LPGBT stock..")
    total_needed = sum(len(get_lpgbt_ids(cur, bc)) for bc in boards)
    stock_db  = connect(0)
    stock_cur = stock_db.cursor(prepared=True)
    status, stock_list = get_unused_stock(stock_cur, "IC-LPS", quantity=total_needed)

    if status != 200:
        logger.error(f"Failed to fetch LPGBT stock: {stock_list}")
        return io.StringIO()
    stock_iter = iter(stock_list)

    buf = io.StringIO()
    writer = csv.writer(buf)
    header = [
        "LABEL_TYPECODE","SERIAL_NUMBER","BARCODE","NAME_LABEL",
        "LOCATION","INSTITUTION","MANUFACTURER","PRODUCTION_DATE",
        "MADE-FROM-TYPECODE[0]","MADE-FROM-SN[0]",
        "COMMENT_DESCRIPTION","ATTRIBUTE-NAME[0]","ATTRIBUTE-VALUE[0]",
    ]
    writer.writerow(header)

    remap = {"DAQ1":"DAQ","TRG1":"TRIG-1","TRG2":"TRIG-2","TRG3":"TRIG-3","TRG4":"TRIG-4"}
    eng_label = ENGINE_LABELS.get(engine_type, f"{engine_type} Engine")

    count = 0
    for bc in boards:
        version_char = bc[8]
        lp_info = LPGBT_VERSIONS.get(version_char)
        if lp_info is None:
            logger.warning(f"Unknown LPGBT version '{version_char}' in {bc}, skipping")
            continue

        manufacturer    = lp_info['manufacturer']
        production_date = lp_info['production_date']

        for loc, lid in get_lpgbt_ids(cur, bc):
            st_status, used_map = get_used_for(stock_cur, lid)
            if st_status != 200:
                logger.error(f"Error checking existing stock for {lid}: {used_map}")
                continue

            existing = None
            if "IC-LPS" in used_map and used_map["IC-LPS"]:
                existing = used_map["IC-LPS"][0]

            if existing:
                serial = existing
            else:
                try:
                    serial = next(stock_iter)
                except StopIteration:
                    logger.error("Insufficient LPGBT stock for all boards")
                    break

                mark_db  = connect(1)
                mark_cur = mark_db.cursor(prepared=True)
                mk_status, mk_msg = mark_used(mark_db, mark_cur, serial, lid)
                if mk_status != 200:
                    logger.error(f"Failed to mark {serial} used→{lid}: {mk_msg}")
                    continue
                logger.info(f"Assigned new stock {serial} → LPGBT {lid}")

            mapped_loc = remap.get(loc, loc)
            row = [
                "IC-LPG", lid, lid,
                f"LPGBT {mapped_loc} 0x{lid}",
                LOCATION, INSTITUTION, manufacturer,
                production_date, "IC-LPS", serial,
                f"{mapped_loc} LPGBT for {bc}",
                f"lpGBT Location {eng_label}", mapped_loc
            ]
            writer.writerow(row)
            count += 1

    logger.info(f"LPGBT CSV: prepared {count} entries")
    buf.seek(0)
    return buf

# --------- CLI ---------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Produce both engine and LPGBT CSVs and zip them."
    )
    parser.add_argument(
        '--engine',
        required=True,
        choices=ENGINE_CONFIG.keys(),
    )
    parser.add_argument(
        '-z', '--zip-out',
        required=False,
        default=None,
        help="Output ZIP filename. If omitted, defaults to '<engine>_components.zip'"
    )
    args = parser.parse_args()

    zip_name = args.zip_out or f"{args.engine}_engine_reg.zip"

    cfg     = ENGINE_CONFIG[args.engine]
    eng_buf, written_engines = engine_file(cfg['prefix'], cfg['n_lpgbts'], args.engine)
    lpg_buf = lpgbt_file(cfg['prefix'], args.engine, written_engines)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{args.engine}_engines.csv", eng_buf.getvalue())
        zf.writestr(f"{args.engine}_lpgbts.csv",                lpg_buf.getvalue())

    with open(zip_name, 'wb') as f:
        f.write(zip_buf.getvalue())

    logger.info(f"Wrote {zip_name}")


if __name__ == '__main__':
    main()
