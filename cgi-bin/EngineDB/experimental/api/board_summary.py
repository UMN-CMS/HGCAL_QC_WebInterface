#!../../cgi_runner.sh

import cgi
import asyncio

from board_report import boardReport
from collections import Counter
from util import catchExceptions, compileRuleSet, getBothConnections
import json


async def main():
    board_report = await boardReport()
    counter = Counter(
        (x["typecode"], y) for x in board_report.values() for y in x["qc_states"]
    )
    ret = {
        x: {y[1]: counter[y] for y in [u for u in counter if u[0] == x]}
        for x in sorted(set(z[0] for z in counter))
    }
    print(json.dumps(ret))


if __name__ == "__main__":
    print("Content-Type: application/json\n\n")
    asyncio.run(main())
