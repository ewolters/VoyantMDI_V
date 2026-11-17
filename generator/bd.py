# Generates TS_Binder_v2.pa.yaml — operator troubleshooting binder (1920x1080, read-only)
exec(open("/tmp/claude-0/gen/theme.py").read())
src=open('/tmp/claude-0/gen/build6.py').read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
MUTE="RGBA(243, 244, 244, 1)"; PANEL="RGBA(248, 249, 249, 1)"; AMBL="RGBA(253, 236, 200, 1)"
RAD={"RadiusTopLeft":"=8","RadiusTopRight":"=8","RadiusBottomLeft":"=8","RadiusBottomRight":"=8"}

BODY=r'''
def rect(name,fill,x,y,w,h,indent=0,extra=None):
    d={"Fill":F(fill)}; d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Rectangle@2.3.0",d,indent)
def image(name,img,x,y,w,h,indent=0,extra=None):
    d={"Image":F(img),"ImagePosition":"=ImagePosition.Fit","Fill":F(MUTE)}; d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Image@2.2.3",d,indent)
def tip(name,text): EXTRA.setdefault(name,{})["Tooltip"]='="'+text.replace('"','""')+'"'
ISS='LookUp(colIss, ID = varIssueID)'
SEL='(ThisItem.ID = varIssueID)'

# header
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"TROUBLESHOOTING GUIDE"',190,20,460,50,size=24,bold=True,color=WHITE,font="Georgia"))
out.append(cap("cBLine","LINE",680,6,120,color=G5))
out.append(dd("ddBLine",'ForAll(SortByColumns(colLines, "DisplayOrder"), {Value: Line})',680,28,130,52,default='Coalesce(Param("line"), "209")',size=20,bold=True,onchange="Set(varIssueID, Blank())"))
out.append(ti("txtBSearch",'""',830,28,560,52,'false',hint='"search: wrinkle, skew, jam, cap…"',size=16,number=False,extra={"Align":"=Align.Left"}))
LOAD=('IfError(ClearCollect(colLk, Filter(Lookups, Active = true)), Notify("Could not load Lookups — " & FirstError.Message, NotificationType.Error));\n'
 'ClearCollect(colEq, ForAll(Sort(Filter(colLk, Category.Value = "Equipment"), SortOrder), {Value: Label}));\n'
 'ClearCollect(colLines, Lines);\n'
 'IfError(ClearCollect(colIss, Filter(TS_Issues, Active = true)), Notify("Could not load TS_Issues — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colFix, Filter(TS_Fixes, Active = true)), Notify("Could not load TS_Fixes — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colOcc, Filter(TS_Occurrences, OccurredAt >= DateAdd(Today(), -90, TimeUnit.Days))), Notify("Could not load TS_Occurrences", NotificationType.Warning));\n'
 'If(!varParamUsed && !IsBlank(Param("equip")), Set(varEquip, Param("equip")));\n'
 'Set(varParamUsed, true);\n'
 'Set(varLoaded, Now())')
out.append(btn("btnBRefresh",'"REFRESH"',LOAD,1410,28,130,52,fill=TEAL_D,color=WHITE,size=14,extra=RAD))
out.append(label("lblBInfo",'"Ranked by what actually fixed it (last 90 days)." & Char(10) & If(IsBlank(varLoaded), "Not loaded", "Loaded " & Text(varLoaded, "h:mm AM/PM"))',1560,14,346,64,size=11,color=G5,align="Right"))

# col 1: equipment
out.append(label("c1T",'"MACHINE"',12,100,300,30,size=12,bold=True,color=G9))
ek=[btn("gBEq",'ThisItem.Value & "  (" & CountRows(Filter(colIss, EquipType = ThisItem.Value && (IsBlank(Line) || Line = ddBLine.Selected.Value))) & ")"',
        'Set(varEquip, ThisItem.Value); Set(varIssueID, Blank())',4,4,292,64,
        fill=f'If(varEquip = ThisItem.Value, {TEAL_D}, {WHITE})',color=f'If(varEquip = ThisItem.Value, {WHITE}, {DARK})',size=16,indent=6,
        extra={"BorderColor":F(G5),"BorderThickness":"=1","Align":"=Align.Left","PaddingLeft":"=16",**RAD})]
gp={"Items":F("colEq"),"TemplateSize":"=72","TemplatePadding":"=0"}; gp.update(box(8,130,304,940))
out.append(ctrl("galBEq","Gallery@2.15.0",gp,0,ek,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))

# col 2: concerns
out.append(label("c2T",'If(IsBlank(varEquip) && IsBlank(txtBSearch.Text), "PICK A MACHINE  ←", "WHAT DO YOU SEE?")',324,100,620,30,size=12,bold=True,color=G9))
ISSITEMS=('SortByColumns(ForAll(Filter(colIss, (IsBlank(Line) || Line = ddBLine.Selected.Value) && (IsBlank(varEquip) || EquipType = varEquip || !IsBlank(txtBSearch.Text)) && (!IsBlank(varEquip) || !IsBlank(txtBSearch.Text))\n'
          '   && (IsBlank(txtBSearch.Text) || txtBSearch.Text in Concern || txtBSearch.Text in Appearance)) As i,\n'
          ' {ID: i.ID, Concern: i.Concern, Equip: i.EquipType, Appearance: i.Appearance, N: CountIf(colOcc, IssueID = i.ID)}), "N", SortOrder.Descending)')
ik=[rect("gBIBg",WHITE,0,0,612,108,indent=6,extra={"Fill":F(f'If({SEL}, RGBA(229, 243, 243, 1), {WHITE})'),"BorderColor":F(f'If({SEL}, {TEAL_D}, {G1})'),"BorderThickness":F(f'If({SEL}, 3, 1)')}),
    label("gBIName",'ThisItem.Concern',14,6,470,44,size=17,bold=True,color=DARK,indent=6),
    label("gBIApp",'If(IsBlank(varEquip), ThisItem.Equip & " · ", "") & Coalesce(ThisItem.Appearance, "")',14,48,470,54,size=12,color=G9,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    label("gBICnt",'Text(ThisItem.N) & "×"',500,14,100,44,size=20,bold=True,color=DARK,align="Center",indent=6),
    label("gBICap",'"last 90 days"',500,58,100,24,size=9,color=G9,align="Center",indent=6),
    btn("gBISel",'""','Set(varIssueID, ThisItem.ID); ClearCollect(colIssPh, Filter(TS_Photos, IssueID = ThisItem.ID))',0,0,612,108,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.06)"),"PressedFill":F("RGBA(0, 72, 81, 0.12)"),"BorderColor":F(CLEAR)})]
gp={"Items":F(ISSITEMS),"TemplateSize":"=116","TemplatePadding":"=0"}; gp.update(box(320,130,628,940))
out.append(ctrl("galBIss","Gallery@2.15.0",gp,0,ik,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("c2None",'"Nothing in the guide yet for this. Call maintenance — their fix gets added here."',332,140,600,60,size=14,color=G9,
   extra={"Visible":F('(!IsBlank(varEquip) || !IsBlank(txtBSearch.Text)) && CountRows(galBIss.AllItems) = 0')}))

# col 3: fixes for the selected concern
X3=960; W3=948
out.append(rect("c3Bg",PANEL,X3,100,W3,970))
out.append(label("c3Empty",'"← Pick what you see to get the fixes, in the order to try them."',X3+20,140,W3-40,60,size=16,color=G9,extra={"Visible":"=IsBlank(varIssueID)"}))
out.append(label("c3T",ISS+'.Concern',X3+20,108,W3-260,60,size=22,bold=True,color=DARK,font="Georgia"))
out.append(label("c3App",'Coalesce(' + ISS + '.Appearance, "")',X3+20,168,W3-260,80,size=13,color=G9,extra={"VerticalAlign":"=VerticalAlign.Top"}))
out.append(image("c3Img",'LookUp(colIssPh, Kind.Value = "Appearance").Thumbnail.Large',X3+W3-230,108,210,140))
FIXITEMS=('SortByColumns(ForAll(Filter(colFix, IssueID = varIssueID) As f,\n'
          ' {ID: f.ID, Cause: f.Cause, CM: f.Countermeasure, Chk: f.Check, NR: f.NormalRange, By: f.DoneBy.Value, Seq: Coalesce(f.SeqOrder, 999), Proc: f.ProcID,\n'
          '  Uses: CountIf(colOcc, FixID = f.ID)}), "Uses", SortOrder.Descending, "Seq", SortOrder.Ascending)')
OP='(ThisItem.By = "Operator")'
fk=[rect("gBFBg",WHITE,0,0,W3-40,226,indent=6,extra={"BorderColor":F(G1),"BorderThickness":"=1"}),
    label("gBFNo",'Text(ThisItem.Uses) & "×"',10,10,74,50,size=18,bold=True,color=WHITE,align="Center",indent=6,fill=TEAL_D),
    label("gBFCause",'ThisItem.Cause',96,6,W3-360,54,size=16,bold=True,color=DARK,indent=6),
    label("gBFBy",f'If({OP}, "YOU CAN DO THIS", "CALL " & Upper(ThisItem.By))',W3-260,12,210,34,size=11,bold=True,align="Center",indent=6,
          color=f'If({OP}, {WHITE}, {DARK})',fill=f'If({OP}, {TEAL}, {AMBL})'),
    label("gBFCM",'ThisItem.CM',14,62,W3-260,110,size=14,color=DARK,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    label("gBFNR",'If(IsBlank(ThisItem.NR) || ThisItem.NR = "NA", "", "Normal range: " & ThisItem.NR) & If(IsBlank(ThisItem.Chk), "", "    ·    Check: " & ThisItem.Chk)',14,178,W3-260,40,size=12,color=G9,indent=6),
    btn("gBFSteps",'"📷  SHOW STEPS"','Set(varViewProc, ThisItem.Proc); Set(varViewCause, ThisItem.Cause); ClearCollect(colPh, Filter(TS_Photos, ProcID = ThisItem.Proc)); ClearCollect(colPSteps, Sort(Filter(TS_Steps, ProcID = ThisItem.Proc), StepNo)); Set(varShowSteps, true)',
        W3-240,150,190,60,fill=TEAL_D,color=WHITE,size=13,indent=6,extra={"Visible":F('!IsBlank(ThisItem.Proc) && ThisItem.Proc > 0'),**RAD})]
gp={"Items":F(FIXITEMS),"TemplateSize":"=236","TemplatePadding":"=0"}; gp.update(box(X3+14,258,W3-28,740))
out.append(ctrl("galBFix","Gallery@2.15.0",gp,0,fk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("c3Esc",'Coalesce(' + ISS + '.Escalation, "Still not fixed after trying these? Call maintenance.")',X3+20,1004,W3-40,56,size=13,bold=True,color=DARK,fill=AMBL,
   extra={"PaddingLeft":"=14","Visible":"=!IsBlank(varIssueID)"}))
for n in ["c3T","c3App","c3Img","galBFix"]: EXTRA.setdefault(n,{})["Visible"]="=!IsBlank(varIssueID)"

# steps overlay
out.append(rect("ovVeil","RGBA(7, 39, 45, 0.55)",0,0,1920,1080,extra={"Visible":"=varShowSteps"}))
out.append(rect("ovPanel",WHITE,120,60,1680,960,extra={"Visible":"=varShowSteps"}))
out.append(label("ovT",'varViewCause',150,74,1400,56,size=22,bold=True,color=DARK,font="Georgia",extra={"Visible":"=varShowSteps"}))
out.append(btn("ovClose",'"✕  CLOSE"','Set(varShowSteps, false)',1620,74,160,52,fill=TEAL_D,color=WHITE,size=14,extra={"Visible":"=varShowSteps",**RAD}))
sk=[rect("gOBg",PANEL,0,0,800,420,indent=6),
    label("gON",'Text(ThisItem.StepNo)',10,10,56,56,size=22,bold=True,color=WHITE,align="Center",indent=6,fill=TEAL_D),
    label("gOI",'ThisItem.Instruction',76,6,710,60,size=15,bold=True,color=DARK,indent=6),
    label("gOK",'Coalesce(ThisItem.KeyPoint, "")',76,64,710,40,size=12,color=G9,indent=6),
    image("gOImg",'LookUp(colPh, StepNo = ThisItem.StepNo).Thumbnail.Large',10,108,780,302,indent=6)]
gp={"Items":F("colPSteps"),"WrapCount":"=2","TemplateSize":"=430","TemplatePadding":"=8","Visible":"=varShowSteps"}; gp.update(box(140,140,1640,870))
out.append(ctrl("galOSteps","Gallery@2.15.0",gp,0,sk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
'''
for _ in range(2):
    out=[]
    exec(BODY)
write_themed("/mnt/user-data/outputs/TS_Binder_v2.pa.yaml", "".join(out))
print("ok", len(out))
