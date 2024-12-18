#!./cgi_runner.sh

import cgitb; cgitb.enable()

import base64
import cgi
import html
import json
import sys

import add_test_functions_engine
import base
import connect

LATEST_TEST_QUERY = """
  select LT.test_id, Board.full_id, Board.type_id, LT.day, LT.successful, Test_Type.name as test_name, replace(replace(comments, "\n", ""), "_", " ") as comments, A.attach as last_attach from
   (select T.test_id, T.day, T.board_id, T.test_type_id, T.successful from (
           select *, row_number() over (partition by Test.board_id,Test.test_type_id
                 order by Test.day desc, Test.test_id desc)
    as _rn from Test) T where T._rn = 1) LT
	left join Board on Board.board_id = LT.board_id
	left join Board_type on Board.type_id = Board_type.type_sn
	left join Test_Type on Test_Type.test_type = LT.test_type_id
    left join
    (select _A.attach, _A.test_id from (
            select *, row_number() over (partition by test_id order by attach_id desc) as _rn from Attachments 
        ) _A where _A._rn = 1) A on A.test_id = LT.test_id
     where Board.full_id = %s and Test_Type.name = "Eye Opening";
"""


def sendJson(data):
    print("Content-Type: application/json")
    print()
    print(json.dumps(data))


def sendText(data):
    print("Content-Type: text/plain")
    print()
    print(data)


def sendPdf(data, fname):
    print("Content-Type: application/pdf\n")
    print(f"Content-Disposition: inline; filename={fname}\n")
    sys.stdout.flush()
    sys.stdout.buffer.write(data)


def main():
    db = connect.connect(0)
    arguments = cgi.FieldStorage()
    cur = db.cursor(dictionary=True)
    arguments = cgi.FieldStorage()
    if "full_id" not in arguments:
        return sendJson({"error": f"You must supply a full id."})

    if "chip" not in arguments:
        return sendJson({"error": f'You must supply a chip, ie "DAQ".'})

    full_id = html.escape(arguments["full_id"].value)
    chip = html.escape(arguments["chip"].value)
    cur.execute(LATEST_TEST_QUERY, (full_id,))
    found = cur.fetchone()
    if found is None:
        return sendJson({"error": f'Could not find  a board with ID="{full_id}"'})

    data = json.loads(found["last_attach"])
    test_data = data["test_data"]
    if chip not in test_data:
        return sendJson({"error": f'Chip "{chip}" was not recorded for this board'})

    chip_data = test_data[chip]
    if "image" not in chip_data:
        return sendJson(
            {"error": f"This board's eye opening test does not have an image."}
        )

    raw_pdf = base64.b64decode(chip_data["image"])
    sendPdf(raw_pdf, f"eye_image_{full_id}_{chip}.pdf")


main()
