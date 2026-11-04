"""Check selected contextual readings against CUHK; preserve evidence, never invent it."""
import datetime,json,pathlib,re,time,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 curated=json.loads((ROOT/'references/readings-curated.json').read_text())
 old=json.loads((ROOT/'references/cuhk-audit.json').read_text()) if (ROOT/'references/cuhk-audit.json').exists() else {}
 audit={};errors=[]
 for c,reading in curated.items():
  if old.get(c,{}).get('status','').startswith('verified') and reading==old[c]['reading']:
   audit[c]=old[c];continue
  source='https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/search.php?q='+urllib.parse.quote_from_bytes(c.encode('big5'))
  try:
   with urllib.request.urlopen(source,timeout=30) as response: raw=response.read()
   html=raw.decode('big5',errors='replace')
   readings=sorted(set(re.findall(r'sound\.php\?s=([a-z]+[1-6])',html)))
   if reading not in readings:raise ValueError('Selected reading absent; offered: '+str(readings))
   evidence=ROOT/'references/cuhk-pages'/f'{ord(c):04x}.html';evidence.parent.mkdir(parents=True,exist_ok=True);evidence.write_bytes(raw)
   audit[c]={'reading':reading,'readings':readings,'source':source,'status':'verified-live','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evidenceFile':str(evidence.relative_to(ROOT))}
   print('Verified U+'+f'{ord(c):04X}',flush=True);time.sleep(.2)
  except Exception as exc:
   audit[c]={'reading':reading,'source':source,'status':'pending-live-check','error':str(exc)};errors.append(c);print('Blocked U+'+f'{ord(c):04X}',str(exc),flush=True)
   if '403' in str(exc):
    # A policy denial will not be fixed by repeating the same request for every character.
    for rest in curated:
     if rest not in audit:audit[rest]=old.get(rest,{'reading':curated[rest],'status':'pending-live-check'})
    break
 (ROOT/'references/cuhk-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 pending=[c for c in curated if not audit.get(c,{}).get('status','').startswith('verified')]
 if pending:raise SystemExit('CUHK check pending: '+''.join(pending))
if __name__=='__main__':main()
