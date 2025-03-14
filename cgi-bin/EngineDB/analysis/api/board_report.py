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
from util import cacheDisk, catchExceptions, compileRuleSet


class TestState(str, enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    NOT_RUN = "NOT_RUN"


VIRTUAL_TESTS = ["Registered"]
VISUAL_INPECTION_NAME = "Visual Inspection"
THERMAL_INPECTION_NAME = "Thermal Cycle"

rules = {
    "AmbientQCPassed": ["EQ", ["NOT", "Registered", "Thermal Cycle"], TestState.PASSED],
    "VisualInspected": ["EQ", VISUAL_INPECTION_NAME, TestState.PASSED],
    "Failed": ["EQ", ["ANYNOT", "_"], TestState.FAILED],
    "QCPassed": ["EQ", ["NOT", "Registered"], TestState.PASSED],
    "ReadyToShip": ["EQ", ["NOT", "_"], TestState.PASSED],
}

rule_set = compileRuleSet(rules, lambda d,x: d[x]["test_state"])

def getBoardQCState(test_states):
    # print(test_states)
    return rule_set(test_states)


class Board:
    __slots__ = ("board_id", "full_id", "subtype", "checkin_time")

    def __init__(self, board_id, full_id, subtype, checkin_time):
        self.board_id = board_id
        self.full_id = full_id
        self.subtype = subtype
        self.checkin_time = checkin_time


# @cacheDisk()
def getBoards(subtypes=None, start_date=None, end_date=None):
    db = connect.connect(0)
    cur = db.cursor(dictionary=True)
    query = """SELECT Board.board_id, Board.type_id as subtype, Board.full_id, Check_In.checkin_date as checkin_time FROM Board
    left join Check_In on Check_In.board_id = Board.board_id """
    where_parts = []
    if start_date:
        where_parts.append(("Check_In.checkin_date > %s", (start_date,)))
    if end_date:
        where_parts.append(("Check_In.checkin_date < %s", (end_date,)))
    if subtypes:
        where_parts.append(
            (
                "Board.type_id in ( " + ",".join(["%s"] * len(subtypes)) + " )",
                tuple(subtypes),
            )
        )
    if where_parts:
        complete_where = "WHERE " + "and".join(f"( {x[0]} )" for x in where_parts)
        query += complete_where

    # print(query)
    where_params = tuple(it.chain.from_iterable(x[1] for x in where_parts))
    cur.execute(query, where_params)

    data = [Board(**x) for x in cur.fetchall()]
    return data


# @cacheDisk()
def getTests(test_ids):
    db = connect.connect(0)
    cur = db.cursor(dictionary=True)
    q = """SELECT Test.test_id, Test.successful, A.attach, Test.comments
    FROM Test
    left join
    (select _A.attach, _A.test_id
        from (
            select *,
                row_number() over (partition by test_id order by attach_id desc) as _rn from Attachments
        ) _A where _A._rn = 1) A on A.test_id = Test.test_id
    WHERE Test.test_id IN ( """
    q += ",".join(["%s"] * len(test_ids))
    q += ");"
    # print(q)
    # print(test_ids)
    cur.execute(q, test_ids)

    data = {x["test_id"]: x for x in (cur.fetchall())}
    return data


# @cacheDisk()
def getBoardStates(subtypes=None, start_date=None, end_date=None):
    boards = getBoards(subtypes, start_date, end_date)
    needed_data = getNeededTests()
    latest_tests = getLatestResults(
        subtypes=subtypes, start_date=start_date, end_date=end_date
    )

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
                x["test_name"]: {
                    "test_state": TestState.NOT_RUN,
                }
                for x in needed_data[board.subtype]["needed_tests"]
            },
        }
    for test in latest_tests:
        v = ret[test["full_id"]]["test_status"][test["test_name"]]
        v["test_state"] = TestState.PASSED if test["successful"] else TestState.FAILED
        v["test_id"] = test["test_id"]
        v["test_comment"] = test["comments"]

    for board in ret.values():
        board["qc_states"] = getBoardQCState(board["test_status"])

    return ret


def filterStates(data, filter_states):
    ret = {}
    for x, y in data.items():
        if all(
            y["test_status"].get(z, {}).get("test_state") == s
            for z, s in filter_states.items()
        ):
            ret[x] = y
    return ret


def addAttachments(data, include_tests=None):
    all_ids = []
    for d in data.values():
        all_ids += [
            x["test_id"]
            for k, x in d["test_status"].items()
            if "test_id" in x and (not include_tests or k in include_tests)
        ]
    attachments = getTests(all_ids)
    for d in data.values():
        for v in d["test_status"].values():
            if "test_id" in v:
                a = attachments.get(v["test_id"])
                v["attachment"] = json.loads(a["attach"]) if a else None


def parseArgs():
    args = dict(cgi.parse().items())
    include_attach = args.pop("include_attach", [])
    limit_subtypes = args.pop("subtypes", None)
    checkin_start = args.pop("start", [None])[0]
    checkin_end = args.pop("end", [None])[0]
    return dict(
        limit_subtypes=limit_subtypes,
        checkin_start=checkin_start,
        checkin_end=checkin_end,
        include_attach=include_attach,
        filter_states={x: TestState[y[0]] for x, y in args.items()},
    )


def boardReport(
    limit_subtypes=None,
    checkin_start=None,
    checkin_end=None,
    filter_states=None,
    include_attach=None,
):
    needed_data = getNeededTests()
    latest_tests = getLatestResults()
    data = getBoardStates(limit_subtypes, checkin_start, checkin_end)
    if filter_states:
        data = filterStates(data, filter_states)
    if include_attach and data:
        addAttachments(data, include_attach)
    print(json.dumps(data, default=str))


@catchExceptions
def main():
    print("Content-Type: application/json\n\n")
    args = parseArgs()
    needed_data = getNeededTests()
    latest_tests = getLatestResults()
    return boardReport(
        args["limit_subtypes"],
        args["checkin_start"],
        args["checkin_end"],
        args["filter_states"],
        args["include_attach"],
    )


if __name__ == "__main__":
    cgitb.enable()
    main()
