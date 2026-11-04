"""Validate real shipped media; --release enforces all narration/CUHK evidence."""
import argparse,hashlib,json,pathlib,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');args=parser.parse_args()
 data=json.loads((ROOT/'dist/content.json').read_text());manifest=json.loads((ROOT/'references/art-manifest.json').read_text());errors=[]
 for q in data['life']+data['train']:
  file=f'assets/{q["scene"]}'+('-16-v1.png' if q in data['life'] else '-pair-v1.png')
  path=ROOT/'dist'/file;entry=manifest.get(file)
  if not path.exists() or not entry:errors.append('Missing art '+file);continue
  if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:errors.append('Art changed without audit '+file)
  width,height=struct.unpack('>II',path.read_bytes()[16:24])
  if q in data['life']:
   if width*3!=height*4:errors.append('Not a 4:3 atlas '+file)
   if len(set(entry.get('frameHashes',[])))!=16:errors.append('Missing distinct frames '+file)
  elif width!=height*2:errors.append('Not two square panels '+file)
  if entry.get('visualReview')!='passed':errors.append('Visual review pending '+file)
 for file,entry in manifest.items():
  path=ROOT/'dist'/file
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:errors.append('Shared art changed without audit '+file)
 for file in ['assets/education-kai.ttf','assets/kai-variant-7240.woff2','assets/font-source.txt','assets/kai-variant-license.txt','assets/vocab-v1.png','assets/train-engine-16-v1.png','assets/train-carriages-16-v3.png']:
  if not (ROOT/'dist'/file).is_file():errors.append('Missing '+file)
 ready=json.loads((ROOT/'dist/audio-ready.json').read_text())['files'];missing=[]
 audio_manifest=json.loads((ROOT/'references/audio-manifest.json').read_text()) if (ROOT/'references/audio-manifest.json').exists() else {}
 for id,a in data['audio'].items():
  path=ROOT/'dist'/a['file']
  if a['file'] not in ready or not path.exists() or path.stat().st_size<1000:missing.append(id)
  elif args.release:
   entry=audio_manifest.get(id,{})
   if entry.get('text')!=a['text'] or entry.get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():errors.append('Audio source/content mismatch '+id)
   duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)],text=True).strip())
   if duration<=0:errors.append('Invalid audio '+id)
 audit=json.loads((ROOT/'references/cuhk-audit.json').read_text());curated=json.loads((ROOT/'references/readings-curated.json').read_text())
 pending=[c for c,jp in curated.items() if audit.get(c,{}).get('reading')!=jp or not audit.get(c,{}).get('status','').startswith('verified')]
 print('Illustrations:',len(data['life']),'16-frame atlases +',len(data['train']),'paired scenes')
 print('Narration:',len(data['audio'])-len(missing),'/',len(data['audio']),'ready; CUHK:',len(curated)-len(pending),'/',len(curated),'verified')
 if args.release and missing:errors.append('Narration missing: '+str(len(missing))+' clips')
 if args.release and pending:errors.append('CUHK verification pending: '+''.join(pending))
 if errors:raise SystemExit('\n'.join(errors))
 print('Release gate passed' if args.release else 'Image checks passed; audio/CUHK release status reported separately')
if __name__=='__main__':main()
