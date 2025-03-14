#!../../cgi_runner.sh

import itertools as it
import json
from util import  getBothConnections



QUERY_ATTACH = """
  select LT.test_id, LT.board_id, Board.full_id, Board.type_id, LT.day, LT.successful, 
Test_Type.name as test_name, 
LT.comments, A.attach as attach from
   (select T.test_id, T.day, T.board_id, T.test_type_id, T.successful, T.comments from (
           select *, row_number() over (partition by Test.board_id,Test.test_type_id
                 order by Test.day desc, Test.test_id desc)
    as _rn from Test) T where T._rn = 1) LT
    left join Board on Board.board_id = LT.board_id
    left join Board_type on Board.type_id = Board_type.type_sn
    left join Test_Type on Test_Type.test_type = LT.test_type_id
    left join
    (select _A.attach, _A.test_id
        from (
            select *,
                row_number() over (partition by test_id order by attach_id desc) as _rn from Attachments
        ) _A where _A._rn = 1) A on A.test_id = LT.test_id
"""

QUERY = """
  select LT.test_id, LT.board_id, Board.full_id, Board.type_id, LT.day, LT.successful, Test_Type.name as test_name, LT.comments from
   (select T.test_id, T.day, T.board_id, T.test_type_id, T.successful, T.comments from (
           select *, row_number() over (partition by Test.board_id,Test.test_type_id
                 order by Test.day desc, Test.test_id desc)
    as _rn from Test) T where T._rn = 1) LT
    left join Board on Board.board_id = LT.board_id
    left join Board_type on Board.type_id = Board_type.type_sn
    left join Test_Type on Test_Type.test_type = LT.test_type_id
"""


def jsonPath(data, path):
    try:
        if path[0] == ".":
            path = path[1:]
        if path[0] == "[":
            sp = path.split("]", 1)
            x = int(sp[0][1:])
            new_path = sp[1]
        else:
            sp = path.split(".", 1)
            x = sp[0]
            if len(sp) == 1:
                new_path = None
            else:
                new_path = sp[1]
        if not new_path:
            return data[x]
        else:
            return jsonPath(data[x], sp[1])
    except (IndexError, KeyError, TypeError, ValueError) as e:
        return None


def sendError(string):
    print(json.dumps({"error": string}))


def getLatestResults(
    include_attach=False,
    include_tests=None,
    start_date=None,
    end_date=None,
    subtypes=None,
    full_id=None,
    jq_expr=None,
    dbs=None,
):
    if include_attach:
        query = QUERY_ATTACH
    else:
        query = QUERY

    where_parts = []
    order = "ORDER BY LT.day desc"

    if include_tests:
        where_parts.append(
            (
                "Test_Type.name in (" + ",".join(["%s"] * len(include_tests)) + " )",
                tuple(include_tests),
            )
        )
    if start_date:
        where_parts.append(("LT.day > %s", (start_date,)))
    if end_date:
        where_parts.append(("LT.day < %s", (end_date,)))
    if subtypes:
        where_parts.append(
            (
                "Board.type_id in (" + ",".join(["%s"] * len(subtypes)) + " )",
                tuple(subtypes),
            )
        )
    if full_id:
        where_parts.append(("Board.full_id = %s", (full_id,)))

    where_params = tuple(it.chain.from_iterable(x[1] for x in where_parts))

    if where_parts:
        complete_where = "WHERE " + "and".join(f"( {x[0]} )" for x in where_parts)
        query += complete_where

    query += order

    
    all_data = []
    for db in (dbs or getBothConnections()):
        cur = db.cursor(dictionary=True)
        cur.execute(query, where_params)
        data = list(cur.fetchall())

        for d in data:
            d["day"] = str(d["day"])

        if include_attach:
            for d in data:
                if d["attach"] is not None:
                    r = json.loads(d["attach"])
                    d["attach"] = r
        if jq_expr:
            import jq
            data = jq.compile(jq_expr).input_value(data).all()
            data = [x for x in data if x is not None]
        all_data += data
    return all_data


def main():
    print("Content-Type: application/json\n\n")

    args = cgi.parse()
    attach = False

    include_attach = bool(json.loads(args.get("include_attach", ["false"])[0]))
    include_tests = args.get("test")
    start_date = args.get("start_date") and args.get("start_date")[0]
    end_date = args.get("end_date") and args.get("end_date")[0]
    subtypes = args.get("subtypes")
    full_id = args.get("full_id")
    jq_expr = args.get("jq_expr")

    data = getLatestResults(
        include_attach=include_attach,
        include_tests=include_tests,
        start_date=start_date,
        end_date=end_date,
        subtypes=subtypes,
        full_id=full_id,
        jq_expr=jq_expr,
    )

    print(json.dumps(data, default=str))


if __name__ == "__main__":
    main()
