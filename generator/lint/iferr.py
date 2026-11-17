import yaml,sys,re
def args_of(s,i):
    # s[i] == '(' ; return list of top-level arg strings and end index
    depth=0; out=[]; cur=''; j=i; instr=False
    while j<len(s):
        c=s[j]
        if instr:
            cur+=c
            if c=='"':
                if j+1<len(s) and s[j+1]=='"': cur+='"'; j+=2; continue
                instr=False
            j+=1; continue
        if c=='"': instr=True; cur+=c
        elif c=="'": k=s.index("'",j+1); cur+=s[j:k+1]; j=k+1; continue
        elif c in '([{':
            depth+=1
            if depth>1: cur+=c
        elif c in ')]}':
            depth-=1
            if depth==0: out.append(cur); return out,j
            cur+=c
        elif c==',' and depth==1: out.append(cur); cur=''
        else: cur+=c
        j+=1
    return out,j
for f in sys.argv[1:]:
    d=yaml.safe_load(open(f))
    def walk(l):
        for it in l:
            for n,v in it.items():
                for k,p in (v.get('Properties') or {}).items():
                    p=str(p)
                    for m in re.finditer(r'IfError\(',p):
                        a,_=args_of(p,m.end()-1)
                        if len(a)%2==0:
                            first=a[0].strip()[:40].replace('\n',' '); fb=a[1].strip()[:30].replace('\n',' ')
                            print(f.split('/')[-1],n,k,'nargs',len(a),'|',first,'|',fb)
                walk(v.get('Children',[]))
    walk(d)
