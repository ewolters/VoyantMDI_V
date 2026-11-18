import yaml,sys
d=yaml.safe_load(open(sys.argv[1])); bad=0
def chk(name,k,v):
    global bad
    if not isinstance(v,str) or not v.startswith('='): return
    s=v[1:]; st=[]; i=0; instr=False
    while i<len(s):
        c=s[i]
        if instr:
            if c=='"':
                if i+1<len(s) and s[i+1]=='"': i+=2; continue
                instr=False
        elif c=='"': instr=True
        elif c=="'":
            j=s.index("'",i+1); i=j+1; continue
        elif c in '([{': st.append(c)
        elif c in ')]}':
            if not st or '([{'[')]}'.index(c)]!=st[-1]: print('MISMATCH',name,k,repr(s[max(0,i-60):i+10])); bad+=1; return
            st.pop()
        i+=1
    if instr or st: print('UNBALANCED',name,k,st,instr, s[:120]); bad+=1
def walk(l):
    for it in l:
        for n,v in it.items():
            for k,p in (v.get('Properties') or {}).items(): chk(n,k,p)
            walk(v.get('Children',[]))
walk(d); print('bad',bad)
sys.exit(1 if bad else 0)
