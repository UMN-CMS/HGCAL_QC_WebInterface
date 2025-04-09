import json
from functools import wraps, lru_cache
import re

from mysql.connector.aio import connect
import mysql
import asyncio


def catchExceptions(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(json.dumps({"error": "EXCEPTION", "reason": str(e)}))

    return inner


def compileRule(rule, accessor):
    op, *rest = rule
    rules = [compileRule(z, accessor) for z in rest]
    if op == "AND":
        return lambda x: all(z(x) for z in rules)
    elif op == "OR":
        return lambda x: any(z(x) for z in rules)
    elif op == "NOT":
        return lambda x: not r[0](x)
    elif op == "EQ":
        return compileEq(*rest, accessor)


def compileEq(cols, val, accessor):
    if isinstance(cols, str):
        return compileEq([cols], val, accessor)
    if cols[0] == "NOT":
        return lambda x: all(
            accessor(x, c) == val for c in (c for c in x if c not in cols[1:])
        )
    elif cols[0] == "ANY":
        return lambda x: any(accessor(x, c) == val for c in cols[1:])
    elif cols[0] == "ANYNOT":
        return lambda x: any(
            accessor(x, c) == val for c in (c for c in x if c not in cols[1:])
        )
    else:
        return lambda x: all(accessor(x, c) == val for c in cols)


def compileRuleSet(desc, accessor=lambda d, x: d[x]):
    compiled = {k: compileRule(v, accessor) for k, v in desc.items()}

    def ret(data):
        return [k for k, v in compiled.items() if v(data)]

    return ret


conn_cache = {}
async def getAsyncConnection(path, db_name):
    if (path,db_name) in conn_cache:
        return conn_cache[(path,db_name)]
    with open(path, "r") as f:
        getme = False
        for l in f:
            if getme:
                password = re.search(r"password='([a-zA-Z]+)',", l)[1]
                break
            if "FactoryReadUser" in l:
                getme = True
    # cnx = await connect(
    #     user="FactoryReadUser", password=password, database=db_name, host="cmslab0"
    # )
    cnx = mysql.connector.connect(
        user="FactoryReadUser", password=password, database=db_name, host="cmslab0"
    )
    conn_cache[(path,db_name)] = cnx
    return cnx


async def getBothConnections():
    c1, c2 = await asyncio.gather(
        getAsyncConnection("../../../EngineDB/connect.py", "EngineDB_PRO"),
        getAsyncConnection("../../../WagonDB/connect.py", "WagonDB_PRO"),
    )
    return c1, c2


# def getBothConnections():
#     import importlib.util
#     import sys
#
#     spec = importlib.util.spec_from_file_location(
#         "enginedb.connect", "../../../EngineDB/connect.py"
#     )
#     c1 = importlib.util.module_from_spec(spec)
#     sys.modules["enginedb.connect"] = c1
#     spec.loader.exec_module(c1)
#
#     spec2 = importlib.util.spec_from_file_location(
#         "wagondb.connect", "../../../WagonDB/connect.py"
#     )
#     c2 = importlib.util.module_from_spec(spec2)
#     sys.modules["wagondb.connect"] = c2
#     spec2.loader.exec_module(c2)

# c1.connect(0), c2.connect(0)
