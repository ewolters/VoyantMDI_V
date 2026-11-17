# Generates HxH_Board_v10.pa.yaml (1920x1080)
exec(open("/tmp/claude-0/gen/theme.py").read())
DARK="RGBA(7, 39, 45, 1)"; TEAL_D="RGBA(0, 72, 81, 1)"; TEAL="RGBA(0, 178, 169, 1)"; AQUA="RGBA(176, 227, 228, 1)"
G9="RGBA(117, 120, 123, 1)"; G5="RGBA(177, 179, 179, 1)"; G1="RGBA(217, 217, 214, 1)"; WHITE="RGBA(255, 255, 255, 1)"
GREEN="RGBA(46, 160, 67, 1)"; MUTE="RGBA(243, 244, 244, 1)"; INK="RGBA(60, 64, 67, 1)"; NOW="RGBA(229, 243, 243, 1)"; AMBER="RGBA(210, 153, 34, 1)"; RED="RGBA(207, 34, 46, 1)"; CLEAR="RGBA(0, 0, 0, 0)"
out=[]
EXTRA={}
def ind(s,n): return "\n".join((" "*n+l) if l else l for l in s.split("\n"))
def ctrl(name, ctype, props, indent=0, children=None, variant=None):
    p=" "*indent
    s=f"{p}- {name}:\n{p}    Control: {ctype}\n"
    if variant: s+=f"{p}    Variant: {variant}\n"
    s+=f"{p}    Properties:\n"
    props=dict(props); props.update(EXTRA.get(name, {}))
    for k,v in props.items():
        v=str(v)
        if "\n" in v or ": " in v or "#" in v or v.startswith("=\"") is False and False:
            s+=f"{p}      {k}: |-\n"+ind(v, indent+8)+"\n"
        else:
            s+=f"{p}      {k}: {v}\n"
    if children:
        s+=f"{p}    Children:\n"+"".join(children)
    return s
def F(v): return "="+v
def box(x,y,w,h): return {"X":F(str(x)),"Y":F(str(y)),"Width":F(str(w)),"Height":F(str(h))}
def label(name,text,x,y,w,h,size=12,bold=False,color=DARK,font="Arial",align=None,fill=None,valign=None,pb=None,indent=0,extra=None):
    d={"Text":F(text),"Font":F("Font."+font),"Size":F(str(size)),"Color":F(color)}
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if align: d["Align"]=F("Align."+align)
    if fill: d["Fill"]=F(fill)
    if valign: d["VerticalAlign"]=F("VerticalAlign."+valign)
    if pb is not None: d["PaddingBottom"]=F(str(pb))
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Label@2.5.1",d,indent)
def cap(name,text,x,y,w,color=G9,indent=0): return label(name,f'"{text}"',x,y,w,20,size=9,bold=True,color=color,indent=indent)
def dd(name,items,x,y,w,h,default=None,onchange=None,size=14,bold=False,indent=0,extra=None):
    d={"Items":F(items)}
    if default: d["Default"]=F(default)
    if onchange: d["OnChange"]=F(onchange)
    d.update({"Font":F("Font.Arial"),"Size":F(str(size)),
      "ChevronBackground":F(WHITE),"ChevronFill":F(G9),"ChevronHoverBackground":F(G1),"ChevronHoverFill":F(DARK),
      "ChevronDisabledBackground":F(WHITE),"ChevronDisabledFill":F(G1),
      "SelectionFill":F(TEAL_D),"SelectionColor":F(WHITE),"HoverFill":F(AQUA),"PressedFill":F(AQUA),
      "FocusedBorderColor":F(TEAL_D),"HoverBorderColor":F(G9)})
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/DropDown@2.3.1",d,indent)
def ti(name,default,x,y,w,h,onchange,hint='""',size=14,bold=False,number=True,indent=0,extra=None):
    d={"Default":F(default),"HintText":F(hint)}
    if number: d["Format"]=F("TextFormat.Number")
    d.update({"Font":F("Font.Arial"),"Size":F(str(size)),"Align":F("Align.Center"),"BorderColor":F(G5),"FocusedBorderColor":F(TEAL_D),"HoverBorderColor":F(G9),"OnChange":F(onchange)})
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/TextInput@2.3.2",d,indent)
def btn(name,text,onselect,x,y,w,h,fill=TEAL,color=DARK,size=12,indent=0,extra=None):
    d={"Text":F(text),"OnSelect":F(onselect),"Font":F("Font.Arial"),"Size":F(str(size)),"FontWeight":F("FontWeight.Bold"),
       "Fill":F(fill),"Color":F(color),"HoverFill":F("ColorFade(Self.Fill, -15%)"),"BorderColor":F("Self.Fill")}
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/Button@2.2.0",d,indent)
def rect(name,fill,x,y,w,h): d={"Fill":F(fill)}; d.update(box(x,y,w,h)); return ctrl(name,"Rectangle@2.3.0",d)

