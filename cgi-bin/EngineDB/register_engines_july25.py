#!/usr/bin/env python3

import json
import csv
import logging
import argparse
from connect import connect
import io
import zipfile
# ---------- Common Hardocdes ------------------
LOCATION         = "UMN"
INSTITUTION      = "UMN"

# ------------- Engine Specific Hardocdes -------------
COMMENT_DESCRIPTION    = "Preproduction"

# -------------- LPGBT Specific Hardcodes --------------
LPGBT_MANUFACTURER     = "TSMC"
LPGBT_PRODUCTION_DATE  = "2024-04-24"
LPGBT_TYPECODE   = "IC-LPG"

# -------- Engine-type -> prefix & LPGBT-count mapping
#### N.B: WILL NEED TO ADD 320EH10F and 320EH10H later
ENGINE_CONFIG = {
    'HDF': {
        'prefix':          '320EH0QF',
        'n_lpgbts':        6,
        'production_date': '2024-08-07',
    },
    'HDH': {
        'prefix':          '320EH0QH',
        'n_lpgbts':        3,
        'production_date': '2024-09-15',
    },
    'LD': {
        'prefix':          '320EL',
        'n_lpgbts':        3,
        'production_date': '2024-07-01',
    },
}

ENGINE_LABELS = {
    'HDF': 'HD Engine',
    'HDH': 'HD Engine',
    'LD' : 'LD Engine',
}

# ------- Helpers -----------------------------------
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
    """
    Generate a name label for the barcode, using the engine type to choose
    the correct prefix (e.g. "HD Engine" vs. "LD Engine").
    """
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
            return None
        cur.execute(
            'SELECT test_id FROM Test '
            'WHERE test_type_id = 22 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (bid[0],)
        )
        tid = cur.fetchone()
        if not tid:
            return None
        cur.execute('SELECT attach FROM Attachments WHERE test_id = %s', (tid[0],))
        blob = cur.fetchone()
        if not blob:
            return None
        data = json.loads(blob[0].decode('utf-8'))['test_data']
        return [(k, f"{v['id']:08X}") for k, v in data.items() if 'id' in v]
    except Exception as e:
        logger.error(f"Error retrieving LPGBT IDs for {barcode}: {e}")
        return None


def get_ldo_id(cur, barcode):
    try:
        cur.execute('SELECT LDO FROM Board WHERE full_id = %s', (barcode,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error getting LDO for {barcode}: {e}")
        return None


def get_bare_code(barcode):
    try:
        i = barcode.find('0', barcode.find('0') + 1)
        if i < 0:
            return None, None
        bc = barcode[:i] + 'B' + barcode[i+1:]
        tc = f"{bc[3:5]}-{bc[5:8]}"
        return tc, bc
    except Exception as e:
        logger.error(f"Error making bare code for {barcode}: {e}")
        return None, None


# --- Engine CSV --------------------------------------------------
def engine_file(prefix, n_lpgbts, production_date, engine_type):
    """Return a StringIO buffer with the engine CSV."""
    db  = connect(1)
    cur = db.cursor(buffered=True)
    boards = filter_boards(cur, prefix)

    header = [
        "LABEL_TYPECODE","SERIAL_NUMBER","BARCODE","LOCATION","INSTITUTION",
        "MANUFACTURER","NAME_LABEL","PRODUCTION_DATE","BATCH_NUMBER",
        "COMMENT_DESCRIPTION"
    ]
    # add MADE-FROM slots?~@?
    for i in range(n_lpgbts):
        header += [f"MADE-FROM-TYPECODE[{i}]", f"MADE-FROM-SN[{i}]"]
    # LDO and bare-code slots
    header += [f"MADE-FROM-TYPECODE[{n_lpgbts}]", f"MADE-FROM-SN[{n_lpgbts}]"]
    header += [f"MADE-FROM-TYPECODE[{n_lpgbts+1}]", f"MADE-FROM-SN[{n_lpgbts+1}]"]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)

    count = 0
    for bc in boards:
        if check_if_registered(cur, bc):
            continue

        tc        = get_typecode(cur, bc)
        mf        = get_manufacturer(cur, bc)
        batch     = get_batch(cur, bc)
        name      = get_name(bc, engine_type)
        lpgbts    = get_lpgbt_ids(cur, bc) or []
        ldo       = get_ldo_id(cur, bc)
        bare_tc, bare_sn = get_bare_code(bc)

        if None in (tc, mf, batch, ldo, bare_tc, bare_sn) or len(lpgbts) < n_lpgbts:
            logging.warning(f"Skipping {bc}: incomplete data")
            continue

        row = [
            tc, bc, bc, LOCATION, INSTITUTION,
               mf, name, production_date, batch,
               COMMENT_DESCRIPTION
        ]
        # first n LPGBTs
        for loc, lid in lpgbts[:n_lpgbts]:
            row += [LPGBT_TYPECODE, lid]
        # LDO
        row += ["IC-LDH", str(ldo)]
        # bare-code
        row += [bare_tc, bare_sn]

        writer.writerow(row)
        count += 1

    logging.info(f"Engine CSV: prepared {count} entries")
    buf.seek(0)
    return buf

# ------ LPGBT CSV ------------------------------------
def lpgbt_file(prefix, start_index, engine_type):
    """
    Return a StringIO buffer containing the LPGBT CSV.
    """
    # open DB connection
    db  = connect(1)
    cur = db.cursor(buffered=True)
    boards = filter_boards(cur, prefix)

    # prepare in-memory CSV
    buf = io.StringIO()
    writer = csv.writer(buf)

    # write header
    header = [
        "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "NAME_LABEL",
        "LOCATION", "INSTITUTION", "MANUFACTURER", "PRODUCTION_DATE",
        "MADE-FROM-TYPECODE[0]", "MADE-FROM-SN[0]",
        "COMMENT_DESCRIPTION", "ATTRIBUTE-NAME[0]", "ATTRIBUTE-VALUE[0]",
    ]
    writer.writerow(header)

    # full remapping for trigger channels
    remap = {
        "DAQ1": "DAQ",
        "TRG1": "TRIG-1",
        "TRG2": "TRIG-2",
        "TRG3": "TRIG-3",
        "TRG4": "TRIG-4"
    }

    eng_label = ENGINE_LABELS.get(engine_type, f"{engine_type} Engine")

    idx = start_index
    count = 0
    for bc in boards:
        if check_if_registered(cur, bc):
            continue

        lpgbts = get_lpgbt_ids(cur, bc) or []
        ldo    = get_ldo_id(cur, bc)
        if ldo is None or not lpgbts:
            continue

        for loc, lid in lpgbts:
            mapped_loc = remap.get(loc, loc)
            row = [
                LPGBT_TYPECODE,                  # LABEL_TYPECODE
                lid,                             # SERIAL_NUMBER
                lid,                             # BARCODE
                f"LPGBT {mapped_loc} 0x{lid}",   # NAME_LABEL
                LOCATION,
                INSTITUTION,
                LPGBT_MANUFACTURER,
                LPGBT_PRODUCTION_DATE,
                "IC-LPS",                        # MADE-FROM-TYPECODE[0]
                idx,                             # MADE-FROM-SN[0]
                f"{mapped_loc} LPGBT for {bc}", # COMMENT_DESCRIPTION
                f"lpGBT Location {eng_label}",  # ATTRIBUTE-NAME[0]
                mapped_loc                       # ATTRIBUTE-VALUE[0]
            ]
            writer.writerow(row)
            idx += 1
            count += 1

    logging.info(f"LPGBT CSV: prepared {count} entries")
    buf.seek(0)
    return buf

# --------- CLI ---------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description="Produce both engine and LPGBT CSVs (in-memory) and zip them."
    )
    p.add_argument('--engine',     required=True, choices=ENGINE_CONFIG.keys())
    p.add_argument('-s','--lpgbt-stock', required=True, type=int)
    p.add_argument('-z','--zip-out',     required=True,
                   help="Output ZIP filename, e.g. all_boards.zip")
    args = p.parse_args()

    cfg         = ENGINE_CONFIG[args.engine]
    prefix      = cfg['prefix']
    n_lpgbts    = cfg['n_lpgbts']
    prod_date   = cfg['production_date']
    engine_type = args.engine

    # get two in-memory CSV buffers
    eng_buf = engine_file(prefix, n_lpgbts, prod_date, engine_type)
    lpg_buf = lpgbt_file(prefix, args.lpgbt_stock, engine_type)

    # pack into one ZIP in-memory
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{engine_type}_engines.csv", eng_buf.getvalue())
        zf.writestr("LPGBT.csv",                lpg_buf.getvalue())

    # write final ZIP to disk
    with open(args.zip_out, 'wb') as f:
        f.write(zip_buf.getvalue())

    logger.info(f"Wrote {args.zip_out}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()

