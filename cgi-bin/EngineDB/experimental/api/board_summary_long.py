#!../../cgi_runner.sh

import cgi
import asyncio

from board_report import boardReport
from collections import defaultdict 
import json


async def main():
    board_report = await boardReport()
    ret = defaultdict(lambda : defaultdict(list))
    for board in board_report.values():
        for state in board["qc_states"]:
            ret[board["typecode"]][state].append(board["full_id"])
    for x in ret.values():
        for y in x.values():
            y.sort()

    print(json.dumps(dict(ret)))


if __name__ == "__main__":
    print("Content-Type: application/json\n\n")
    asyncio.run(main())
