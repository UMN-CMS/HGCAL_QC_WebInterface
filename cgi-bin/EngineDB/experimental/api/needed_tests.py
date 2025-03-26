#!../../cgi_runner.sh

import json
from util import getBothConnections
import asyncio

QUERY = """
    select Test_Type.name as test_name, Board_type.type_id as board_type_id, Test_Type.test_type as test_type_id, Board_type.name as board_type_name, Board_type.type_sn as board_typecode from Test_Type
    left join Type_test_stitch on Test_Type.test_type = Type_test_stitch.test_type_id
    left join Board_type on Type_test_stitch.type_id = Board_type.type_id;
"""


async def getStitch():
    all_data = []
    for db in getBothConnections():
        cur = db.cursor(dictionary=True)
        cur.execute(QUERY)
        all_data += list(cur.fetchall())
    return all_data


async def getNeededTests():
    ret = {}
    data = await getStitch()
    for t in data:
        bti = t["board_typecode"]
        if bti not in ret:
            ret[bti] = {
                "board_typecode": t["board_typecode"],
                "board_type_id": t["board_type_id"],
                "needed_tests": [],
            }
        ret[bti]["needed_tests"].append(
            {
                "test_type_id": t["test_type_id"],
                "test_name": t["test_name"],
            }
        )
    return ret


async def main():
    data = await getNeededTests()
    print(json.dumps(data, default=str))


if __name__ == "__main__":
    print("Content-Type: application/json\n\n")
    asyncio.run(main())
