#!../../cgi_runner.sh

import cgi
import cgitb
import enum
import html
import itertools as it
import json
import sys
from collections import defaultdict

import connect
from latest_tests import getLatestResults
from needed_tests import getNeededTests


class TestState(str, enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    NOT_RUN = "NOT_RUN"


class Board:
    __slots__ = ("board_id", "full_id", "subtype", "checkin_time")

    def __init__(self, board_id, full_id, subtype, checkin_time):
        self.board_id = board_id
        self.full_id = full_id
        self.subtype = subtype
        self.checkin_time = checkin_time


def getBoards():
    db = connect.connect(0)
    cur = db.cursor(dictionary=True)
    cur.execute(
        """SELECT Board.board_id, Board.type_id as subtype, Board.full_id, Check_In.checkin_date as checkin_time FROM Board
    left join Check_In on Check_In.board_id = Board.board_id
    ;"""
    )

    data = [Board(**x) for x in cur.fetchall()]
    return data


def getBoardStates():
    boards = getBoards()
    needed_data = getNeededTests()
    latest_tests = getLatestResults()

    ret = {}
    for board in boards:
        fid = board.full_id
        bid = board.board_id
        ret[fid] = {
            "full_id": fid,
            "board_id": bid,
            "check_in": board.checkin_time,
            "typecode": board.subtype,
            "test_status": {
                x["test_name"]: TestState.NOT_RUN
                for x in needed_data[board.subtype]["needed_tests"]
            },
        }
    for test in latest_tests:
        ret[test["full_id"]]["test_status"][test["test_name"]] = (
            TestState.PASSED if test["successful"] else TestState.FAILED
        )

    return ret


def filterStates(data, filter_states):
    ret = {}
    for x, y in data.items():
        if all(y["test_status"].get(z) == s for z, s in filter_states.items()):
            ret[x] = y
    return ret


def filterStates(data, filter_states):
    ret = {}
    for x, y in data.items():
        if all(y["test_status"].get(z) == s for z, s in filter_states.items()):
            ret[x] = y
    return ret


def parseArgs():
    args = cgi.parse()
    return {x: TestState[y[0]] for x, y in args.items()}


def main():
    print("Content-Type: application/json\n\n")
    filters = parseArgs()
    needed_data = getNeededTests()
    latest_tests = getLatestResults()
    data = getBoardStates()
    if filters:
        data = filterStates(data, filters)
    print(json.dumps(data, default=str))


if __name__ == "__main__":
    cgitb.enable()
    main()
