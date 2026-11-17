import zipfile, os
os.chdir('/mnt/user-data/outputs')
OUT='NewAlbany_MDI_Install_for_Kenny_2026-10-21.zip'; R='NewAlbany_MDI_Install/'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    z.write('KENNY_HANDOFF_for_Copilot.md', R+'00_START_HERE_Install_Checklist.md')
    for root,dirs,fs in os.walk('deploy'):
        dirs[:]=[d for d in dirs if d!='generator']
        for f in fs:
            if f.endswith(('.py','.js')): continue
            p=os.path.join(root,f); z.write(p, R+'02_Deploy/'+os.path.relpath(p,'deploy'))
    full=zipfile.ZipFile('NEW_ALBANY_MDI_Full_Package_2026-10-21.zip')
    z.writestr(R+'Reference/New Albany Downtime Escalation Plan-Rev_1.pdf', full.read('NEW_ALBANY_MDI/05_Reference/New Albany Downtime Escalation Plan-Rev_1.pdf'))
z=zipfile.ZipFile(OUT); n=z.namelist()
assert not [x for x in n if x.lower().endswith(('.py','.js','.ps1','.exe','.bat','.cmd','.vbs'))] and z.testzip() is None
print(len(n),'files', os.path.getsize(OUT)//1024,'KB'); print('\n'.join(x for x in n if 'apps/' in x or 'FRONTIER' in x or '05_' in x))
