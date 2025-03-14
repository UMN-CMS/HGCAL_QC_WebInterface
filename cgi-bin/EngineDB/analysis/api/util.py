import json
from functools import wraps

from joblib import Memory, expires_after


def catchExceptions(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(json.dumps({"error": "EXCEPTION", "reason": str(e)}))

    return inner


def getCacheDir():
    return "/tmp/hgcal-qc-webinterface/cache"


MEMORY = Memory(getCacheDir(), verbose=0)


def cacheDisk():
    return MEMORY.cache(cache_validation_callback=expires_after(hours=1))


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
