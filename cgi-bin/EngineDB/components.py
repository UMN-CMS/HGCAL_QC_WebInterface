#!/usr/bin/env python3

import os
import sys
import cgi
import html
import base
from connect import connect
import settings
import json
import cgitb
import mariadb

cgitb.enable()

# ---------- Helpers -----------------------------------
def add_component(cnx, cur, barcode, typecode):
    try:
        cur.execute(
            'INSERT INTO COMPONENT_STOCK (barcode, typecode) VALUES (?, ?)',
            (barcode, typecode)
        )
        cnx.commit()
        return (200, "Ok")
    except mariadb.Error as e:
        return (400, f"Error on add_component: {e}")


def get_used_for(cur, barcode):
    retval = {}
    try:
        cur.execute(
            "SELECT barcode, typecode FROM COMPONENT_STOCK \
             JOIN COMPONENT_USAGE ON COMPONENT_STOCK.component_id = COMPONENT_USAGE.component_id \
             WHERE COMPONENT_USAGE.used_in_barcode LIKE ?", (barcode,)
        )
        for bc, tc in cur:
            retval.setdefault(tc, []).append(bc)
        return (200, retval)
    except mariadb.Error as e:
        return (400, f"Error on get_used_for: {e}")


def get_unused_stock(cur, typecode=None, quantity=1):
    try:
        retval = []
        if typecode is None:
            query = (
                "SELECT typecode, barcode FROM COMPONENT_STOCK \
                 WHERE component_id NOT IN (SELECT component_id FROM COMPONENT_USAGE) \
                 ORDER BY entered LIMIT ?"
            )
            cur.execute(query, (quantity,))
            for tc, bc in cur:
                retval.append((tc, bc))
        else:
            query = (
                "SELECT barcode FROM COMPONENT_STOCK \
                 WHERE typecode = ? AND component_id NOT IN (SELECT component_id FROM COMPONENT_USAGE) \
                 ORDER BY entered LIMIT ?"
            )
            cur.execute(query, (typecode, quantity))
            for (bc,) in cur:
                retval.append(bc)
        return (200, retval)
    except mariadb.Error as e:
        return (400, f"Error on get_unused_stock: {e}")


def mark_used(ctx, cur, barcode, tomake=None):
    try:
        cur.execute(
            "SELECT component_id FROM COMPONENT_STOCK WHERE barcode = ?", (barcode,)
        )
        row = cur.fetchone()
        if not row:
            return (404, f"Barcode '{barcode}' not found in stock")
        cid = int(row[0])

        if tomake and len(tomake) > 10:
            cur.execute(
                "INSERT INTO COMPONENT_USAGE (component_id, used_in_barcode) VALUES (?, ?) ",
                (cid, tomake)
            )
        else:
            cur.execute(
                "INSERT INTO COMPONENT_USAGE (component_id) VALUES (?)", (cid,)
            )
        ctx.commit()
        return (200, "Ok")
    except mariadb.Error as e:
        if e.errno == 1062:
            return (409, f"Barcode {barcode} already used to make something else")
        return (400, f"Error on mark_used: {e}")


def argas(args, name, default=None):
    return args.get(name, default)


# ---------- Main entrypoint -----------------------------
def main():
    args = {}
    if 'REQUEST_METHOD' in os.environ:
        form = cgi.FieldStorage()
        for key in form:
            args[key] = form.getvalue(key)
    else:
        parser = argparse.ArgumentParser(description="Components API")
        parser.add_argument(
            '-r', '--req', choices=['get_unused_stock','get_used_for','add_component','mark_used'],
            required=False, default='get_unused_stock',
            help="Request type"
        )
        parser.add_argument('-b', '--barcode', type=str, help="Barcode")
        parser.add_argument('-m', '--tomake', type=str, help="To make barcode")
        parser.add_argument('-t', '--typecode', type=str, help="Typecode")
        parser.add_argument('-q', '--quantity', type=int, default=20, help="Quantity requested")
        parsed = parser.parse_args()
        args = vars(parsed)

    req = args.get('req')
    result = (404, 'Unknown')

    if req == 'get_unused_stock':
        db = connect(0)
        cur = db.cursor(prepared=True)
        result = get_unused_stock(cur, argas(args, 'typecode'), int(argas(args, 'quantity', 1)))
        print(result)
    elif req == 'get_used_for':
        db = connect(0)
        cur = db.cursor(prepared=True)
        result = get_used_for(cur, argas(args, 'barcode'))
    elif req == 'add_component':
        db = connect(1)
        cur = db.cursor(prepared=True)
        result = add_component(db, cur, argas(args, 'barcode'), argas(args, 'typecode'))
    elif req == 'mark_used':
        db = connect(1)
        cur = db.cursor(prepared=True)
        result = mark_used(db, cur, argas(args, 'barcode'), argas(args, 'tomake'))

    status, payload = result

    if status > 299:
        print("Content-Type: text/plain")
        print(f"Status: {status}\n")
        print(payload)
    else:
        print("Content-Type: application/json")
        print("Status: 200 OK\n")
        print(json.dumps(payload))


if __name__ == '__main__':
    import argparse
    main()

