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
