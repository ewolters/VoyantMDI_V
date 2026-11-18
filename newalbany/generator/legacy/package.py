"""Rebuilds MDI_Deploy_Package.zip and the full package zip from outputs/ (no .py/.js files)."""
import zipfile, os, io
os.chdir(__import__("os").environ["MDI_OUTDIR"])
def deploy_files():
    for root, dirs, fs in os.walk('deploy'):
        dirs[:] = [d for d in dirs if d != 'generator']
        for f in fs:
            if f.endswith(('.py', '.js')): continue
            p = os.path.join(root, f); yield p, os.path.relpath(p, 'deploy')
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    for p, r in deploy_files(): z.write(p, 'deploy/' + r)
open('MDI_Deploy_Package.zip', 'wb').write(buf.getvalue())
FULL = 'NEW_ALBANY_MDI_Full_Package_2026-10-21.zip'
old = zipfile.ZipFile(FULL); new = io.BytesIO()
with zipfile.ZipFile(new, 'w', zipfile.ZIP_DEFLATED) as z:
    for i in old.infolist():
        n = i.filename
        if n.startswith('NEW_ALBANY_MDI/02_Deploy/') or n in ('NEW_ALBANY_MDI/KENNY_HANDOFF_for_Copilot.md', 'NEW_ALBANY_MDI/log.md'): continue
        z.writestr(i, old.read(n))
    for p, r in deploy_files(): z.write(p, 'NEW_ALBANY_MDI/02_Deploy/' + r)
    z.write('MDI_Deploy_Package.zip', 'NEW_ALBANY_MDI/02_Deploy/MDI_Deploy_Package.zip')
    z.write('KENNY_HANDOFF_for_Copilot.md', 'NEW_ALBANY_MDI/KENNY_HANDOFF_for_Copilot.md')
    z.write('log.md', 'NEW_ALBANY_MDI/log.md')
old.close()
open(FULL, 'wb').write(new.getvalue())
z = zipfile.ZipFile(FULL); n = z.namelist()
assert not [x for x in n if x.endswith(('.py', '.js'))] and z.testzip() is None
print(len(n), 'files OK;', [x for x in n if 'tools/' in x])
