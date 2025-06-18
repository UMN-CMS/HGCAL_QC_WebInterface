#!/usr/bin/env python3

import json
import csv
import logging
import argparse
from connect import connect

# -------- Logging ---------------------------- 
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
    'HDF': 'HD Full Engine',
    'HDH': 'HD Half Engine',
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
def engine_file(csv_file, prefix, n_lpgbts, production_date, engine_type):
    db = connect(1)
    cur = db.cursor(buffered=True)
    boards = filter_boards(cur, prefix)

    # Build header
    header = [
        "LABEL_TYPECODE","SERIAL_NUMBER","BARCODE","LOCATION","INSTITUTION",
        "MANUFACTURER","NAME_LABEL","PRODUCTION_DATE","BATCH_NUMBER",
        "COMMENT_DESCRIPTION"
    ]
    # n_lpgbts slots, then LDO, then bare-code
    for i in range(n_lpgbts):
        header += [f"MADE-FROM-TYPECODE[{i}]", f"MADE-FROM-SN[{i}]"]
    header += [f"MADE-FROM-TYPECODE[{n_lpgbts}]", f"MADE-FROM-SN[{n_lpgbts}]"]  # LDO
    header += [f"MADE-FROM-TYPECODE[{n_lpgbts+1}]", f"MADE-FROM-SN[{n_lpgbts+1}]"]  # bare code

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        count = 0

        for bc in boards:
            print("BARCODE:", bc)

            if check_if_registered(cur, bc):
                continue

            tc        = get_typecode(cur, bc)
            mf        = get_manufacturer(cur, bc)
            batch     = get_batch(cur, bc)
            name      = get_name(bc, engine_type)
            lpgbts    = get_lpgbt_ids(cur, bc) or []
            ldo       = get_ldo_id(cur, bc)
            bare_tc, bare_sn = get_bare_code(bc)

            # require exactly n_lpgbts LPGBTs plus LDO and bare-code
            if None in (tc, mf, batch, ldo, bare_tc, bare_sn) or len(lpgbts) < n_lpgbts:
                logger.warning(f"Skipping {bc}: missing data or only {len(lpgbts)} LPGBTs")
                continue

            row = [
                tc, bc, bc, LOCATION, INSTITUTION,
                   mf, name, production_date, batch,
                   COMMENT_DESCRIPTION
            ]

            # add the first n_lpgbts LPGBTs
            for loc, lid in lpgbts[:n_lpgbts]:
                row += [LPGBT_TYPECODE, lid]

            # LDO slot
            row += ["IC-LDH", str(ldo)]
            # bare-code slot
            row += [bare_tc, bare_sn]

            writer.writerow(row)
            count += 1

    logger.info(f"Engine CSV: wrote {count} entries to {csv_file}")


# ------ LPGBT CSV ------------------------------------
def lpgbt_file(csv_file, start_index, prefix, engine_type):
    db = connect(1)
    cur = db.cursor(buffered=True)
    boards = filter_boards(cur, prefix)

    out_name = f"LPGBT_{csv_file}"
    header = [
        "LABEL_TYPECODE","SERIAL_NUMBER","BARCODE","NAME_LABEL",
        "LOCATION","INSTITUTION","MANUFACTURER","PRODUCTION_DATE",
        "MADE-FROM-TYPECODE[0]","MADE-FROM-SN[0]",
        "COMMENT_DESCRIPTION","ATTRIBUTE-NAME[0]","ATTRIBUTE-VALUE[0]",
    ]

    remap = {
        "DAQ1": "DAQ",
        "TRG1": "TRIG-1",
        "TRG2": "TRIG-2",
        "TRG3": "TRIG-3",
        "TRG4": "TRIG-4"
    }

    eng_label = ENGINE_LABELS.get(engine_type, f"{engine_type} Engine")

    with open(out_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

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
                attr_value = mapped_loc  

                row = [
                    LPGBT_TYPECODE,  # "IC-LPG"
                    lid,             # SERIAL_NUMBER
                    lid,             # BARCODE
                    f"LPGBT {mapped_loc} 0x{lid}",      # NAME_LABEL
                    LOCATION,
                    INSTITUTION,
                    LPGBT_MANUFACTURER,
                    LPGBT_PRODUCTION_DATE,
                    "IC-LPS",        # MADE-FROM-TYPECODE[0]
                    idx,             # MADE-FROM-SN[0]
                    f"{mapped_loc} LPGBT for {bc}",         # COMMENT_DESCRIPTION
                    f"lpGBT Location {eng_label}",  # ATTRIBUTE-NAME[0]
                    attr_value       # ATTRIBUTE-VALUE[0]
                ]
                writer.writerow(row)

                idx   += 1
                count += 1

    logger.info(f"LPGBT CSV: wrote {count} entries to {out_name}")


# --------- CLI ---------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description="Produce both engine and LPGBT CSVs based on engine type."
    )
    p.add_argument('--engine', required=True, choices=ENGINE_CONFIG.keys(),
                   help="Which engine type to process: HDF, HDH, or LD.")
    p.add_argument('-o','--output', required=True,
                   help="Base output filename for engine CSV.")
    p.add_argument('-s','--lpgbt-stock', required=True, type=int,
                   help="Starting LPGBT-stock index")
    args = p.parse_args()

    cfg          = ENGINE_CONFIG[args.engine]
    board_prefix = cfg['prefix']
    n_lpgbts     = cfg['n_lpgbts']
    prod_date    = cfg['production_date']
    engine_type  = args.engine

    # engine_file signature now also takes production_date and engine_type
    engine_file(
        args.output,
        board_prefix,
        n_lpgbts,
        prod_date,
        engine_type
    )

    # pass engine_type into lpgbt_file as well
    lpgbt_file(
        args.output,
        args.lpgbt_stock,
        board_prefix,
        engine_type
    )

if __name__ == '__main__':
    main()
