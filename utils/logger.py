from __future__ import annotations
import json, sys, time

def log(level: str, msg: str, **kwargs):
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": level.upper(),
        "msg": msg, **kwargs
    }
    sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def info(msg, **kw): log("info", msg, **kw)
def warn(msg, **kw): log("warn", msg, **kw)
def err(msg,  **kw): log("error", msg, **kw)
