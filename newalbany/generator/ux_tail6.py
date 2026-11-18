NXT=('With({n: First(Filter(colHours, InShift && Now() >= StartT && IsBlank(Cum))),\n'
     '      od: CountRows(Filter(colHours, InShift && Now() >= DateAdd(StartT, SlotMin, TimeUnit.Minutes) && IsBlank(Cum)))},\n')
out.append(label("lblNext", 'If(Coalesce(Value(txtCrew.Text), 0) <= 0, "NEXT ▸ ENTER" & Char(10) & "ACTUAL CREW", '+NXT+'  If(IsBlank(n),\n     If(CountRows(Filter(colHours, InShift && IsBlank(Cum))) = 0, "✓ ALL HOURS ENTERED", "✓ UP TO DATE"),\n     "NEXT ▸ " & Text(n.StartT, "h:mm AM/PM") & " counter" & If(od > 0, Char(10) & Text(od) & If(od = 1, " hour", " hours") & " overdue", ""))))',
   1280,100,256,72,size=15,bold=True,align="Center",
   extra={"Fill":F(f'If(Coalesce(Value(txtCrew.Text), 0) <= 0, {YEL}, '+NXT+f'  If(IsBlank(n), {GREEN}, od > 0, {RED}, {YEL})))'),
          "Color":F(f'If(Coalesce(Value(txtCrew.Text), 0) <= 0, {DARK}, '+NXT+f'  If(IsBlank(n) || od > 0, {WHITE}, {DARK})))'),
          "Tooltip":'="What the operator owes the board right now. Yellow = this hour is due. Red = hours have ended with no counter entered."'}))
# legend
def sw(name,fill,border,x): d={"Fill":F(fill),"BorderColor":F(border),"BorderThickness":"=2"}; d.update(box(x,953,16,16)); return ctrl(name,"Rectangle@2.3.0",d)
out.append(sw("lgY",YEL,YELB,200)); out.append(label("lgYt",'"Fill in now"',220,948,100,26,size=10,bold=True,color=G9))
out.append(sw("lgR",LRED,REDB,322)); out.append(label("lgRt",'"Overdue"',342,948,80,26,size=10,bold=True,color=G9))
out.append(sw("lgW",W_,GB,424)); out.append(label("lgWt",'"Done / optional"',444,948,120,26,size=10,bold=True,color=G9))
out.append(sw("lgP","RGBA(130, 80, 223, 1)","RGBA(130, 80, 223, 1)",566)); out.append(label("lgPt",'"★ Exceptional hour"',586,948,140,26,size=10,bold=True,color=G9))
out.append(label("lgTip",'"● = operator entry   ·   hover any box or column header for help"',730,948,420,26,size=10,color=G9))
