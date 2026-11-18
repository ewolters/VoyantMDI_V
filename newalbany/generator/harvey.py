# Harvey-ball images for Newspaper progress (0/25/50/75/100) as static SVG data URIs.
import urllib.parse
def _svg(p, stroke, fill, canceled=False):
    s = "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'>"
    s += f"<circle cx='20' cy='20' r='17' fill='white' stroke='{stroke}' stroke-width='3'/>"
    if canceled:
        s += f"<line x1='9' y1='31' x2='31' y2='9' stroke='{stroke}' stroke-width='3'/>"
    elif p == 100:
        s += f"<circle cx='20' cy='20' r='15.5' fill='{fill}'/>"
    elif p == 25:
        s += f"<path d='M20,20 L20,4.5 A15.5,15.5 0 0,1 35.5,20 Z' fill='{fill}'/>"
    elif p == 50:
        s += f"<path d='M20,20 L20,4.5 A15.5,15.5 0 0,1 20,35.5 Z' fill='{fill}'/>"
    elif p == 75:
        s += f"<path d='M20,20 L20,4.5 A15.5,15.5 0 1,1 4.5,20 Z' fill='{fill}'/>"
    s += "</svg>"
    return "data:image/svg+xml;utf8," + urllib.parse.quote(s, safe="")
HB_OK  = {p: _svg(p, "#004851", "#004851") for p in (0, 25, 50, 75, 100)}
HB_LATE= {p: _svg(p, "#CF222E", "#004851") for p in (0, 25, 50, 75, 100)}
HB_DONE= _svg(100, "#2EA043", "#2EA043")
HB_CAN = _svg(0, "#B1B3B3", "#B1B3B3", canceled=True)
def HBSW(table, pexpr):
    return "Switch(" + pexpr + ", " + ", ".join(f'{p}, "{table[p]}"' for p in (0, 25, 50, 75)) + f', "{table[100]}")'
def HB_EXPR(pexpr, lateexpr, statusexpr):
    """Power Fx Image expression for one action."""
    return (f'If({statusexpr} = "Canceled", "{HB_CAN}", {pexpr} >= 100, "{HB_DONE}", {lateexpr}, '
            + HBSW(HB_LATE, pexpr) + ", " + HBSW(HB_OK, pexpr) + ")")
def PROG(rec):
    """Progress with a fallback from status for rows created before the Progress column existed."""
    return f'Coalesce({rec}.Progress, Switch({rec}.Status.Value, "Done", 100, "In progress", 50, 0))'
def CYCLE_PATCH(rec, refresh):
    """Step progress 0 -> 25 -> 50 -> 75 -> 100 -> 0; status follows."""
    P = PROG(rec)
    return (f'If({rec}.Status.Value = "Canceled", Notify("Canceled action. Open it to change.", NotificationType.Information),\n'
            f' With({{nx: Switch({P}, 0, 25, 25, 50, 50, 75, 75, 100, 0)}}, With({{st: If(nx = 0, "Open", nx = 100, "Done", "In progress")}},\n'
            f'  If(IsError(Patch(Newspaper, LookUp(Newspaper, ID = {rec}.ID), {{Progress: nx, Status: {{Value: st}}, ClosedDate: If(nx = 100, Now(), Blank())}})),\n'
            f'   Notify("Not saved. Check your connection and try again.", NotificationType.Error),\n'
            f'   {refresh}))))')
