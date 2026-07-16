import argparse
import itertools as it
from collections import namedtuple
import socket
import sys
import mysql.connector
from getpass import getpass

DB_INSERT_USERNAME = "FactoryInserter"
DB_READ_USERNAME = "FactoryReadUser"


GET_ID_TEMPLATE = """
with T1 as
(select board_id, MAX(test_id) as test_id, test_type_id from Test where test_type_id={test_id} group by board_id, test_type_id)
select Board.board_id, full_id, CONVERT(JSON_EXTRACT(Attachments.attach, "$.LPGBT.id"), INTEGER) as LPGBT_ID,
     Board.comments as board_comment, Check_In.checkin_id as checkin_id,
    Check_Out.comment as checkout_comment,
     checkout_date, People.person_name as checkout_person_name
from Board
left join T1 on T1.board_id=Board.board_id
left join Attachments on T1.test_id=Attachments.test_id
left join Check_Out on Board.board_id=Check_Out.board_id
left join Check_In on Board.board_id=Check_In.board_id
left join People on Check_Out.person_id = People.person_id
"""

MEZZ_TEST_ID = 29
WAGON_TEST_ID = 26


def makeConfirm(passthrough):
    def confirm(prompt):
        if passthrough:
            return True
        answer = ""
        while answer not in ["y", "n"]:
            answer = input(prompt + " [Y/N] ").lower()
        return answer == "y"

    return confirm


def getConnection(username, password, db):
    conn = mysql.connector.connect(
        user=username, password=password, database=db, host="cmslab0"
    )
    conn.autocommit = False
    cursor = conn.cursor(dictionary=True)
    return conn, cursor


def getWagonIds(cur):
    wagon_q = (
        GET_ID_TEMPLATE.format(test_id=WAGON_TEST_ID)
        + 'where Board.type_id in ("WE40A1", "WE40A2", "WE31A3", "WE31A1")'
    )
    cur.execute(wagon_q)
    all_wagons = cur.fetchall()
    return {x["full_id"]: x for x in all_wagons}


def getMezzIds(cur):
    mezz_q = (
        GET_ID_TEMPLATE.format(test_id=MEZZ_TEST_ID)
        + 'where Board.type_id like "ZPLM%"'
    )
    cur.execute(mezz_q)
    all_mezzs = cur.fetchall()
    return {x["full_id"]: x for x in all_mezzs}


def neededUpdates(wagon_ids, mezz_ids):
    lookup = {x["LPGBT_ID"]: x for x in wagon_ids.values() if x["LPGBT_ID"] is not None}
    mezz_creates, mezz_comment_updates = {}, {}
    for mezz in mezz_ids.values():
        found = lookup.get(mezz["LPGBT_ID"])
        if not found:
            continue
        mid, m_c_comment, mdate = (
            mezz["full_id"],
            mezz["checkout_comment"],
            mezz["checkout_date"],
        )
        wid, w_c_comment, wdate = (
            found["full_id"],
            found["checkout_comment"],
            found["checkout_date"],
        )
        if wdate is None:
            continue
        if mezz["checkout_date"] is None:
            mezz_creates[mid] = {
                "comment": w_c_comment,
                "date": wdate,
                "person_name": found["checkout_person_name"],
            }
        elif m_c_comment != w_c_comment:
            mezz_comment_updates[mid] = {
                "comment": w_c_comment,
                "date": wdate,
                "person_name": found["checkout_person_name"],
            }

    return mezz_creates, mezz_comment_updates


def parseArguments():
    parser = argparse.ArgumentParser(
        description="Sync Mezzanine and Wagon Shipping States."
    )
    parser.add_argument(
        "-y",
        "--yes",
        help="Always respond yes to safety prompts",
        action="store_true",
    )
    return parser.parse_args()


def getPersonMapping(cur):
    cur.execute("SELECT * from People")
    people = cur.fetchall()
    return {x["person_name"]: x["person_id"] for x in people}


def handleCreates(cursor, creates, mezz_ids, person_mapping):
    template = """INSERT INTO
    Check_Out (checkin_id, board_id, person_id, comment, checkout_date)
    VALUES (%s, %s, %s, %s, %s)
    """
    needed = [
        (
            mezz_ids[k]["checkin_id"],
            mezz_ids[k]["board_id"],
            person_mapping[v["person_name"]],
            v["comment"],
            v["date"],
        )
        for k, v in creates.items()
    ]
    cursor.executemany(template, needed)


def handleUpdates(cursor, updates, mezz_ids, person_mapping):
    template = """UPDATE Check_Out SET comment=%s, checkout_date=%s, person_id=%s where
    board_id=%s
    """
    needed = [
        (
            v["comment"],
            v["date"],
            person_mapping[v["person_name"]],
            mezz_ids[k]["board_id"],
        )
        for k, v in updates.items()
    ]
    cursor.executemany(template, needed)


def main():
    hostname = socket.gethostname()
    if "cmslab" not in hostname:
        print(f"This script must be run on the cmslab network. Aborting.")
        return

    args = parseArguments()
    confirm = makeConfirm(args.yes)
    password = getpass("Factor Inserter Password: ")
    wagon_conn, wagon_cur = getConnection(DB_INSERT_USERNAME, password, "WagonDB_PRO")
    engine_conn, engine_cur = getConnection(
        DB_INSERT_USERNAME, password, "EngineDB_PRO"
    )

    mezz_ids = getMezzIds(engine_cur)
    wagon_ids = getWagonIds(wagon_cur)
    person_mapping = getPersonMapping(engine_cur)

    mezz_creates, mezz_comment_updates = neededUpdates(wagon_ids, mezz_ids)
    print(f"Warning! About to modify the database table 'Check_Out' in EngineDB_PRO.")
    print(
        f"This action will create {len(mezz_creates)} new rows and update {len(mezz_comment_updates)} rows"
    )
    if not confirm(f"Are you sure you want to do this?"):
        print(f"Aborting!")
        return
    try:
        handleCreates(engine_cur, mezz_creates, mezz_ids, person_mapping)
        handleUpdates(engine_cur, mezz_comment_updates, mezz_ids, person_mapping)
        print(f"All done!")
        engine_conn.commit()

    

    except Exception as e:
        print(f"An exception occurred, rolling back transactions: {e}".format(e))
        engine_conn.rollback()
        wagon_conn.rollback()
        raise
    finally:
        if engine_conn.is_connected():
            engine_cur.close()
            engine_conn.close()
        if wagon_conn.is_connected():
            wagon_cur.close()
            wagon_conn.close()


if __name__ == "__main__":
    main()
