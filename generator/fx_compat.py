"""Power Fx compatibility fixes applied to every generated app (newer Studio builds are stricter).
1. IfError(value, fallback) where the fallback (Notify/Clear) returns Boolean but value is a record/table
   -> IfError(value, fallback, true)   (3-arg form: result type = Boolean throughout)."""
import re
def _args(s, i):
    depth = 0; parts = []; start = i + 1; j = i; instr = False
    while j < len(s):
        c = s[j]
        if instr:
            if c == '"':
                if j + 1 < len(s) and s[j + 1] == '"': j += 2; continue
                instr = False
            j += 1; continue
        if c == '"': instr = True
        elif c == "'":
            k = s.find("'", j + 1)
            if k < 0: return None
            j = k + 1; continue
        elif c in '([{': depth += 1
        elif c in ')]}':
            depth -= 1
            if depth == 0: parts.append((start, j)); return parts, j
        elif c == ',' and depth == 1: parts.append((start, j)); start = j + 1
        j += 1
    return None
def fix_iferror(text):
    out = []; pos = 0
    for m in re.finditer(r'\bIfError\(', text):
        if m.start() < pos: continue
        r = _args(text, m.end() - 1)
        if not r: continue
        parts, end = r
        if len(parts) == 2:
            fb = text[parts[1][0]:parts[1][1]].strip()
            if fb.startswith(('Notify(', 'Clear(')):
                out.append(text[pos:end]); out.append(', true'); pos = end
    out.append(text[pos:])
    return ''.join(out)

# 2. Photo to flow as base64 TEXT instead of a File input (File inputs are typed differently across Power Apps builds:
#    "Invalid argument type (Record). Expecting a Text value"). {contentBytes: X, name: "y"} -> base64 text of X.
_PH = re.compile(r'\{contentBytes: ([A-Za-z0-9_.]+), name: "[^"]*"\}')
def photo_b64(text):
    return _PH.sub(lambda m: 'JSON(' + m.group(1) + ', JSONFormat.IncludeBinaryData)', text)   # flow strips the data: prefix and quotes
