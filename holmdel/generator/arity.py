"""Checks argument counts of Power Automate expression functions in a flow definition."""
import json, re, sys
ARITY = {"trim": (1, 1), "toLower": (1, 1), "toUpper": (1, 1), "length": (1, 1), "empty": (1, 1), "first": (1, 1), "last": (1, 1),
 "int": (1, 1), "string": (1, 1), "json": (1, 1), "uriPath": (1, 1), "uriHost": (1, 1), "base64ToString": (1, 1), "not": (1, 1),
 "substring": (3, 3), "replace": (3, 3), "startsWith": (2, 2), "endsWith": (2, 2), "contains": (2, 2), "equals": (2, 2),
 "greater": (2, 2), "greaterOrEquals": (2, 2), "less": (2, 2), "lessOrEquals": (2, 2), "add": (2, 2), "sub": (2, 2), "mul": (2, 2), "div": (2, 2),
 "if": (3, 3), "split": (2, 2), "take": (2, 2), "skip": (2, 2), "addProperty": (3, 3), "setProperty": (3, 3), "formatDateTime": (1, 3),
 "addDays": (2, 3), "addMinutes": (2, 3), "convertFromUtc": (2, 3), "utcNow": (0, 1), "coalesce": (1, 99), "union": (2, 99),
 "and": (2, 99), "or": (2, 99), "concat": (1, 99), "createArray": (0, 99), "join": (2, 2), "indexOf": (2, 2), "body": (1, 1),
 "outputs": (1, 1), "items": (1, 1), "variables": (1, 1), "parameters": (1, 1), "actions": (1, 1), "triggerBody": (0, 0), "item": (0, 0),
 "workflow": (0, 0), "encodeUriComponent": (1, 1), "triggerOutputs": (0, 0), "result": (1, 1), "isInt": (1, 1)}
def strings(o):
    if isinstance(o, dict):
        for v in o.values(): yield from strings(v)
    elif isinstance(o, list):
        for v in o: yield from strings(v)
    elif isinstance(o, str): yield o
def exprs(s):
    if s.startswith('{"version":"0.3.0"'): return
    if s.startswith("@") and not s.startswith("@{"): yield s[1:]
    for m in re.finditer(r"@\{", s):
        j = m.end(); d = 1; q = False
        while j < len(s) and d:
            c = s[j]
            if c == "'": q = not q
            elif not q: d += (c == "{") - (c == "}")
            j += 1
        yield s[m.end():j - 1]
probs = []
def check(e):
    i = 0
    while i < len(e):
        m = re.match(r"([A-Za-z]+)\(", e[i:])
        if m and (i == 0 or not (e[i - 1].isalnum() or e[i - 1] == "_")) and not in_quote(e, i):
            name = m.group(1); start = i + len(m.group(0)); d = 1; q = False; args = 0; j = start; nonempty = False
            while j < len(e) and d:
                c = e[j]
                if c == "'": q = not q
                elif not q:
                    if c == "(": d += 1
                    elif c == ")": d -= 1
                    elif c == "," and d == 1: args += 1
                if d and not c.isspace(): nonempty = True
                j += 1
            n = args + 1 if nonempty else 0
            if name in ARITY and not (ARITY[name][0] <= n <= ARITY[name][1]): probs.append(f"{name}() has {n} args: {e[i:i+90]}")
            if name not in ARITY: probs.append(f"unknown function {name}")
        i += 1
def in_quote(e, i):
    return e[:i].count("'") % 2 == 1
for f in sys.argv[1:]:
    d = json.load(open(f))["properties"]["definition"]
    for s in strings(d):
        for e in exprs(s): check(e)
print("arity problems:", sorted(set(probs)) or "none")
