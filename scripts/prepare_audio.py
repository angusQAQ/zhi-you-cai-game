"""Generate prerecorded HK Cantonese in authorized cloud/CI, never in the game."""
import asyncio, hashlib, json, os, pathlib, ssl, subprocess
import aiohttp, edge_tts
ROOT=pathlib.Path(__file__).resolve().parents[1]
async def main():
 data=json.loads((ROOT/'dist/content.json').read_text());files=[];audit={}
 proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
 async with aiohttp.TCPConnector(ssl=ssl.create_default_context()) as connector:
  for id,clip in data['audio'].items():
   target=ROOT/'dist'/clip['file'];target.parent.mkdir(parents=True,exist_ok=True)
   if not target.exists():
    temporary=target.with_suffix('.partial.mp3')
    try:
     await edge_tts.Communicate(clip['text'],clip['voice'],rate='-8%',proxy=proxy,connector=connector).save(str(temporary))
     subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(temporary)],check=True,capture_output=True)
     temporary.replace(target)
    finally:temporary.unlink(missing_ok=True)
   duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(target)],text=True).strip())
   if duration<=0 or target.stat().st_size<1000:raise ValueError('Invalid audio: '+id)
   audit[id]={**clip,'duration':duration,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'provider':'Microsoft Edge Read Aloud; not CUHK recordings'}
   files.append(clip['file']);print('Verified',id,flush=True)
 (ROOT/'dist/audio-ready.json').write_text(json.dumps({'files':files},ensure_ascii=False,indent=2)+'\n')
 (ROOT/'references/audio-manifest.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':asyncio.run(main())
