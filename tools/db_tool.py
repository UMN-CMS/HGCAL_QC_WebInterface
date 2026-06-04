#!/usr/bin/env python3
"""
A simple script for interacting with the UMN HGCAL QC database.
"""

import argparse
import itertools as it
import socket
import sys
import mysql.connector
from getpass import getpass

DB_USERNAME = "FactoryInserter"


def makeConfirm(passthrough):
    def confirm(prompt):
        if passthrough:
            return True
        answer = ""
        while answer not in ["y", "n"]:
            answer = input(prompt + " [Y/N] ").lower()
        return answer == "y"

    return confirm

def handleAddManufacturer(args):
    if args.yes:
        print(f'Running in "always yes" mode.')

    confirm = makeConfirm(args.yes)
    name = args.name
    letter_code = args.letter_code
    db = args.db
    print(
        f'You are about to add the manufacturer "{name}" database.'
    )
    if not confirm(f"This is what I want to do"):
        print("Aborting")
        return

    db_password = getpass("SQL Inserter Password:")
    conn = mysql.connector.connect(
        user=DB_USERNAME, password=db_password, database=db, host="cmslab0"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Manufacturers")
    manufacturers = [x["name"] for x in  cursor.fetchall()]
    codes = [x["letter_code"] for x in  cursor.fetchall()]

    if name in manufactuers:
        print(f"There is already a manufacturer with this name in the database.")
        print("Aborting")
        return

    if letter_code is not None and letter_code in codes:
        print(f"There is already a manufacturer with this code in the database.")
        print("Aborting")
        return

    if letter_code is not None:
        cursor.execute(
            "INSERT INTO Manufacturers (name,letter_code) VALUES (%s,%s)",
            (name,letter_code)
        )
    else:
        cursor.execute(
            "INSERT INTO Manufacturers (name) VALUES (%s)",
            (name,letter_code)
        )
    conn.commit()
    conn.close()

    print(f"Done adding manufacturer to database.")


def handleAddBoard(args):
    if args.yes:
        print(f'Running in "always yes" mode.')

    confirm = makeConfirm(args.yes)
    name = args.name
    typecode = args.typecode
    db = args.db
    print(
        f'You are about to add the board "{typecode}" ("{name}") to the {db} database.'
    )
    if not confirm(f"This is what I want to do"):
        print("Aborting")
        return

    db_password = getpass("SQL Inserter Password:")
    conn = mysql.connector.connect(
        user=DB_USERNAME, password=db_password, database=db, host="cmslab0"
    )
    cursor = conn.cursor(dictionary=True)

    test_ids = cursor.execute("SELECT * FROM Test_Type")
    test_ids = cursor.fetchall()
    vi_test_id = next(x for x in test_ids if x["name"] == "Visual Inspection")[
        "test_type"
    ]
    register_test_id = next(x for x in test_ids if x["name"] == "Registered")[
        "test_type"
    ]

    cursor.execute(
        "SELECT * FROM Board_type WHERE type_id=%s OR name=%s", (typecode, name)
    )
    matches = cursor.fetchall()
    if matches:
        print(f"There are already a boards in the database with these parameters:")
        for t, n in matches:
            print(f"{t}: {n}")
        print("Aborting")
        return

    cursor.execute(
        "INSERT INTO Board_type (type_sn, name) VALUES (%s,%s)", (typecode, name)
    )
    conn.commit()

    cursor.execute(
        "SELECT * FROM Board_type WHERE type_id=%s OR name=%s", (typecode, name)
    )
    type_id = cursor.fetchone()["type_id"]

    cursor.execute(
        "INSERT INTO Type_test_stitch (type_id, test_type_id) VALUES (%s,%s)",
        (type_id, vi_test_id),
    )
    cursor.execute(
        "INSERT INTO Type_test_stitch (type_id, test_type_id) VALUES (%s,%s)",
        (type_id, register_test_id),
    )
    conn.commit()
    conn.close()

    print(f"Done adding board to database.")


def handleAddTest(args):
    if args.yes:
        print(f'Running in "always yes" mode.')

    confirm = makeConfirm(args.yes)

    db = args.db
    name = args.name
    long_desc = args.long_desc
    short_desc = args.long_desc
    after = args.after
    before = args.before

    db_password = getpass("SQL Inserter Password:")
    conn = mysql.connector.connect(
        user=DB_USERNAME, password=db_password, database=db, host="cmslab0"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Test_Type")
    tests = cursor.fetchall()

    test_names = [t["name"] for t in tests]
    test_orders = [t["relative_order"] for t in tests]
    if name in (x["name"] for x in tests):
        print(f'Test "{n}" already exists in database.\nAborting.')
        return

    for n in [*before, *after]:
        if n not in test_names:
            print(f'Test "{n}" not found in database.\nAborting.')
            return

    max_less = max(x["relative_order"] for x in tests if x["name"] in before)
    min_more = min(x["relative_order"] for x in tests if x["name"] in after)
    if max_less >= min_more:
        print(
            f"Could not resolve ordering. Please check your list of before and after tests.\nAborting."
        )
        return

    order_to_use = None
    for i in range(max_less, min_more):
        if i not in test_orders:
            order_to_use = i
            break
    if order_to_use is None:
        print(
            f"Could not resolve ordering. Please check your list of before and after tests.\nAborting."
        )
        return

    print(
        f"I am about insert a test with the following properties:\nName: {name}\nShort Desc: {short_desc}\nLong Desc: {long_desc}\nRelative Order: {order_to_use}"
    )
    if not confirm(f"This is what I want to do"):
        print("Aborting")
        return

    cursor.execute(
        "INSERT INTO Test_type (name,desc_short,desc_long,required,relative_order) VALUES (%s,%s,%s,%s,%s)",
        (name, short_desc, long_desc, True, order_to_use),
    )
    conn.commit()
    print("Test inserted into database.")


def handleStitch(args):
    if args.yes:
        print(f'Running in "always yes" mode.')

    confirm = makeConfirm(args.yes)

    test_names = args.test_names
    board_types = args.board_types
    db = args.db

    db_password = getpass("SQL Inserter Password:")
    conn = mysql.connector.connect(
        user=DB_USERNAME, password=db_password, database=db, host="cmslab0"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Test_Type")
    tests = cursor.fetchall()
    cursor.execute("SELECT * FROM Board_type")
    boards = cursor.fetchall()

    board_ids = [x["type_id"] for x in boards if x["type_sn"] in board_types]
    test_ids = [x["test_type"] for x in tests if x["name"] in test_names]

    db_test_names = [t["name"] for t in tests]
    for n in test_names:
        if n not in db_test_names:
            print(f'Test "{n}" not found in database.\nAborting.')
            return

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Type_test_stitch")
    stitched = cursor.fetchall()
    to_stitch = set(it.product(board_ids, test_ids)) - set(stitched)
    print(f"Preparing to add {len(to_stitch)} stitches to the table")
    if not confirm(f"This is what I want to do"):
        print("Aborting")
        return

    for type_id, test_type_id in to_stitch:
        cursor.execute(
            f"INSERT INTO Type_test_stitch (type_id, test_type_id) VALUES (%s,%s)",
            (type_id, test_type_id),
        )

    conn.commit()

    print(f"Stiches added")


def parseArguments():
    parser = argparse.ArgumentParser(
        description="Tool to add new boards to the UMN CMS QC Databases"
    )
    parser.add_argument(
        "-y",
        "--yes",
        help="Always respond yes to safety prompts",
        action="store_true",
    )

    parser.add_argument(
        "-d",
        "--db",
        help="Name of the database to add the board to.",
        type=str,
        choices=["EngineDB_PRO", "WagonDB_PRO"],
        required=True,
    )
    subparsers = parser.add_subparsers()

    parser_add_board = subparsers.add_parser(
        name="add-board", help="Add a new board to the database."
    )
    parser_add_board.add_argument(
        "-t",
        "--typecode",
        help='Typecode (major and subtype) of the board. eg "WH30A2"',
        type=str,
        required=True,
    )
    parser_add_board.add_argument(
        "-n",
        "--name",
        help='Name of the board. Eg "Pineapple" for WH30AD',
        type=str,
        required=True,
    )
    parser_add_board.set_defaults(func=handleAddBoard)

    parser_add_test = subparsers.add_parser(
        name="add-test", help="Add a new test to the database"
    )
    parser_add_test.add_argument(
        "-n",
        "--name",
        help="Short name of the test",
        type=str,
        required=True,
    )
    parser_add_test.add_argument(
        "-l",
        "--long-desc",
        help="Long description of the test",
        type=str,
        required=True,
    )

    parser_add_test.add_argument(
        "-s",
        "--short-desc",
        help="Short description of the test",
        type=str,
        required=True,
    )

    parser_add_test.add_argument(
        "--before",
        help="List of tests that must precede this test",
        nargs="+",
        required=True,
    )

    parser_add_test.add_argument(
        "--after",
        help="List of tests that must follow this test",
        nargs="+",
        required=True,
    )
    parser_add_test.set_defaults(func=handleAddTest)

    parser_add_stitch = subparsers.add_parser(
        name="add-stitch", help="Add new stitches to the database"
    )

    parser_add_stitch.add_argument(
        "--test-names",
        help="List of tests to stitch",
        nargs="+",
        type=str,
        required=True,
    )

    parser_add_stitch.add_argument(
        "--board-types",
        help="List of board typecodes to stitch",
        nargs="+",
        type=str,
        required=True,
    )
    parser_add_stitch.set_defaults(func=handleStitch)

    parser_add_manu = subparsers.add_parser(
        name="add-manufacturer", help="Add new manufacturers to the database"
    )

    parser_add_manu.add_argument(
        "--name",
        type=str,
        required=True,
    )

    parser_add_manu.add_argument(
        "--letter-code",
        type=str,
        default=None,
    )
    parser_add_manu.set_defaults(func=handleAddManufacturer)

    args =  parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help(sys.stderr)
        return None
    else:
        return args


def main():
    hostname = socket.gethostname()
    if "cmslab" not in hostname:
        print(f"This script must be run on the cmslab network. Aborting.")
        return

    args = parseArguments()
    if args is None:
        return
    args.func(args)


if __name__ == "__main__":
    main()
