"""(Copy of holmdel/generator/lint2.py, plus functions New Albany flows use. Keep the two in step.)
Static checks for a Power Automate flow definition, covering every class of runtime error hit so far.

  - every @-expression parses (balanced parens/brackets, closed strings)
  - every function is a known WDL function, with a valid argument count, and no empty arguments
  - addProperty/setProperty/removeProperty names are literals without . [ ] @ (the Make_copies failure)
  - actions()/body()/outputs()/result() name an action that exists in the flow
  - items('X') is used inside foreach/until X; variables('V') names an initialized variable
  - runAfter targets exist in the same scope
  - Foreach/Until/If/Scope/Query/Select/Compose/Wait/... shapes have their required keys
Usage: python3 lint2.py flow.json [flow.json ...]
"""
import json, re, sys

ARITY = {  # name: (min, max)
 "base64": (1, 1), "base64ToBinary": (1, 1), "decodeBase64": (1, 1), "float": (1, 1),
 "trim": (1, 1), "toLower": (1, 1), "toUpper": (1, 1), "length": (1, 1), "empty": (1, 1), "first": (1, 1), "last": (1, 1),
 "int": (1, 1), "string": (1, 1), "json": (1, 1), "uriPath": (1, 1), "uriHost": (1, 1), "base64ToString": (1, 1), "not": (1, 1),
 "substring": (2, 3), "replace": (3, 3), "startsWith": (2, 2), "endsWith": (2, 2), "contains": (2, 2), "equals": (2, 2),
 "greater": (2, 2), "greaterOrEquals": (2, 2), "less": (2, 2), "lessOrEquals": (2, 2), "add": (2, 2), "sub": (2, 2), "mul": (2, 2), "div": (2, 2),
 "if": (3, 3), "split": (2, 2), "take": (2, 2), "skip": (2, 2), "addProperty": (3, 3), "setProperty": (3, 3), "removeProperty": (2, 2),
 "formatDateTime": (1, 3), "addDays": (2, 3), "addMinutes": (2, 3), "convertFromUtc": (2, 3), "utcNow": (0, 1),
 "coalesce": (1, 99), "union": (2, 99), "and": (2, 99), "or": (2, 99), "concat": (1, 99), "createArray": (0, 99),
 "join": (2, 2), "indexOf": (2, 2), "body": (1, 1), "outputs": (1, 1), "items": (1, 1), "variables": (1, 1), "parameters": (1, 1),
 "actions": (1, 1), "result": (0, 1), "triggerBody": (0, 0), "triggerOutputs": (0, 0), "item": (0, 0), "workflow": (0, 0),
 "encodeUriComponent": (1, 1), "isInt": (1, 1), "ticks": (1, 1), "less": (2, 2)}
SHAPES = {"Foreach": ["foreach", "actions"], "Until": ["expression", "limit", "actions"], "If": ["expression", "actions"],
          "Scope": ["actions"], "Query": ["inputs"], "Select": ["inputs"], "Compose": ["inputs"], "Wait": ["inputs"],
          "InitializeVariable": ["inputs"], "SetVariable": ["inputs"], "AppendToArrayVariable": ["inputs"],
          "OpenApiConnection": ["inputs"], "Response": ["inputs"]}

def tokens(e):
    i, out = 0, []
    while i < len(e):
        c = e[i]
        if c == "'":
            j = i + 1; buf = ""
            while True:
                if j >= len(e): raise ValueError("unclosed string")
                if e[j] == "'":
                    if j + 1 < len(e) and e[j + 1] == "'": buf += "'"; j += 2; continue
                    break
                buf += e[j]; j += 1
            out.append(("str", buf)); i = j + 1
        elif c.isalpha() or c == "_":
            j = i
            while j < len(e) and (e[j].isalnum() or e[j] in "_$"): j += 1
            out.append(("id", e[i:j])); i = j
        elif c.isdigit() or (c == "-" and i + 1 < len(e) and e[i + 1].isdigit()):
            j = i + 1
            while j < len(e) and (e[j].isdigit() or e[j] == "."): j += 1
            out.append(("num", e[i:j])); i = j
        elif c in "()[],?.": out.append((c, c)); i += 1
        elif c.isspace(): i += 1
        else: raise ValueError(f"unexpected character {c!r}")
    return out

class P:
    def __init__(s, t, ctx): s.t, s.i, s.ctx = t, 0, ctx
    def peek(s): return s.t[s.i] if s.i < len(s.t) else (None, None)
    def take(s, k=None):
        tok = s.peek()
        if k and tok[0] != k: raise ValueError(f"expected {k}, got {tok[1]!r}")
        s.i += 1; return tok
    def expr(s):
        k, v = s.peek()
        if k == "str": s.take(); node = ("lit", v)
        elif k == "num": s.take(); node = ("lit", v)
        elif k == "id":
            s.take()
            if v in ("true", "false", "null") and s.peek()[0] != "(": node = ("lit", v)
            else:
                s.take("("); args = []
                if s.peek()[0] != ")":
                    while True:
                        if s.peek()[0] in (",", ")"): raise ValueError(f"empty argument in {v}()")
                        args.append(s.expr())
                        if s.peek()[0] == ",": s.take(); continue
                        break
                s.take(")"); node = ("call", v, args); s.ctx.call(v, args)
        else: raise ValueError(f"unexpected {v!r}")
        while s.peek()[0] in ("?", "[", "."):
            if s.peek()[0] == "?": s.take()
            if s.peek()[0] == "[": s.take(); s.expr(); s.take("]")
            elif s.peek()[0] == ".": s.take(); s.take("id")
        return node

class Ctx:
    def __init__(s, all_actions, variables, loops, where, probs):
        s.all, s.vars, s.loops, s.where, s.probs = all_actions, variables, loops, where, probs
    def err(s, m): s.probs.append(f"{s.where}: {m}")
    def call(s, f, args):
        if f not in ARITY: s.err(f"unknown function {f}()"); return
        lo, hi = ARITY[f]
        if not lo <= len(args) <= hi: s.err(f"{f}() takes {lo}-{hi} args, got {len(args)}")
        lit = lambda a: a[1] if a[0] == "lit" else None
        if f in ("addProperty", "setProperty", "removeProperty") and len(args) >= 2:
            n = lit(args[1])
            if n is None: s.err(f"{f}() property name is not a literal")
            elif re.search(r"[.\[\]@]", n): s.err(f"{f}() property name {n!r} has . [ ] or @")
        if f in ("actions", "body", "outputs", "result") and args:
            n = lit(args[0])
            if n is None: s.err(f"{f}() name is not a literal")
            elif n not in s.all: s.err(f"{f}('{n}') - no such action")
        if f == "items" and args:
            n = lit(args[0])
            if n not in s.loops: s.err(f"items('{n}') used outside that loop")
        if f == "variables" and args:
            n = lit(args[0])
            if n not in s.vars: s.err(f"variables('{n}') never initialized")

def exprs_in(s):
    if s.startswith("@@"): return
    if s.startswith("@") and not s.startswith("@{"): yield s[1:]; return
    for m in re.finditer(r"@\{", s):
        j, d, q = m.end(), 1, False
        while j < len(s) and d:
            c = s[j]
            if c == "'": q = not q
            elif not q: d += (c == "{") - (c == "}")
            j += 1
        if d: raise ValueError("unclosed @{")
        yield s[m.end():j - 1]

def walk_strings(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from walk_strings(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(o, str): yield path, o

def lint(path):
    d = json.load(open(path))["properties"]["definition"]
    probs, all_actions, variables = [], {}, set()
    def collect(acts):
        for n, a in acts.items():
            if n in all_actions: probs.append(f"duplicate action name {n}")
            all_actions[n] = a
            if a["type"] == "InitializeVariable":
                for v in a["inputs"]["variables"]: variables.add(v["name"])
            for k in ("actions",):
                if k in a: collect(a[k])
            if a["type"] == "If": collect(a.get("else", {}).get("actions", {}))
    collect(d["actions"])
    def visit(acts, loops, scope):
        for n, a in acts.items():
            t = a["type"]
            for k in SHAPES.get(t, []):
                if k not in a: probs.append(f"{scope}/{n}: {t} missing '{k}'")
            for r in a.get("runAfter", {}):
                if r not in acts: probs.append(f"{scope}/{n}: runAfter '{r}' not in the same scope")
            own = {k: v for k, v in a.items() if k not in ("actions", "else")}
            inner_loops = loops | ({n} if t in ("Foreach",) else set())
            for p, s in walk_strings(own):
                if p.endswith("/OSTS") or (t == "Compose" and n == "OSTS"): continue
                try:
                    for e in exprs_in(s):
                        ctx = Ctx(all_actions, variables, inner_loops if t == "Foreach" and p == "/foreach" and False else inner_loops, f"{scope}/{n}{p}", probs)
                        if p == "/foreach": ctx.loops = loops   # a loop's own foreach expression runs outside it
                        pr = P(tokens(e), ctx); pr.expr()
                        if pr.i != len(pr.t): probs.append(f"{scope}/{n}{p}: trailing tokens in expression")
                except ValueError as ex:
                    probs.append(f"{scope}/{n}{p}: parse error: {ex}")
            if "actions" in a: visit(a["actions"], inner_loops, f"{scope}/{n}")
            if t == "If": visit(a.get("else", {}).get("actions", {}), loops, f"{scope}/{n}(else)")
    visit(d["actions"], set(), "")
    return probs

bad = 0
for f in sys.argv[1:]:
    p = lint(f)
    print(f"{f}: {'clean' if not p else str(len(p)) + ' problem(s)'}")
    for x in p: print("   ", x)
    bad += len(p)
sys.exit(1 if bad else 0)
