import re,sys
bad=0
for f in sys.argv[1:]:
    y=open(f).read()
    for w in ["Parent","Self","ThisItem","ThisRecord"]:
        for m in re.finditer(r'(?<![.\w"])'+w+r'(?![\w"(])', y):
            ctx=y[max(0,m.start()-30):m.end()+10]
            if w=="ThisItem" and y[m.end()]=='.': continue
            if w in("Self",) and y[m.end()]=='.': continue
            print(f,w,repr(ctx)); bad+=1
    for m in re.finditer(r'\{(\w+): ', y):
        if m.group(1) in ("Parent","Self","ThisItem","ThisRecord"): print('field named',m.group(1)); bad+=1
print('reserved issues:',bad)
