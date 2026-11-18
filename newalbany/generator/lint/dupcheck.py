import re,sys
for f in sys.argv[1:]:
    y=open(f).read().split('\n'); cur=None; keys={}; blk=None; bad=0
    for i,l in enumerate(y,1):
        m=re.match(r'^(\s*)- (\w+):$',l)
        if m: cur=m.group(2); keys={}; blk=None; continue
        if blk is not None and (len(l)-len(l.lstrip())>blk or not l.strip()): continue
        blk=None
        m=re.match(r'^(\s*)(\w+): (.*)$',l)
        if m and cur and m.group(2) not in ('Control','Variant','Properties','Children'):
            k=(len(m.group(1)),m.group(2))
            if k in keys: print('DUP',f,cur,m.group(2),i); bad+=1
            keys[k]=i
            if m.group(3)=='|-': blk=len(m.group(1))
    print(f,'dup props:',bad)
