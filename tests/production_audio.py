"""Verify shipped HK narration in real Chromium, locally or at the deployed URL.
No substituted audio and no relaxed autoplay policy. This checks playback and
asset/text consistency; it is not a human linguistic listening assessment.
"""
import argparse,json,pathlib,shutil,os,urllib.request
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:8793/')
parser.add_argument('--output',default='evidence/production-audio-results.json')
args=parser.parse_args();base=args.base_url.rstrip('/')+'/'
with urllib.request.urlopen(base+'content.json') as r:data=json.load(r)
with urllib.request.urlopen(base+'audio-ready.json') as r:ready=json.load(r)
assert set(ready['files'])=={a['file'] for a in data['audio'].values()}
results=[]
def passed(name,details=''):
 results.append({'name':name,'status':'passed','details':details});print('PASS',name,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1280,'height':720});errors=[];bad=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:bad.append(str(r.status)+' '+r.url) if r.status>=400 else None)
 page.add_init_script('''window.actualSpeakers=[];window.audioEnded=[];const OriginalAudio=window.Audio;window.Audio=function(...args){const a=new OriginalAudio(...args);a.addEventListener('ended',()=>window.audioEnded.push(a.currentSrc));window.actualSpeakers.push(a);return a;};''')
 page.goto(base,wait_until='networkidle')
 durations=page.evaluate('''async files=>{const out={};for(const file of files){const a=document.createElement('audio');a.preload='metadata';await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('metadata timeout '+file)),20000);a.onloadedmetadata=()=>{clearTimeout(timer);resolve()};a.onerror=()=>{clearTimeout(timer);reject(Error('decode error '+file))};a.src=file;a.load()});if(!Number.isFinite(a.duration)||a.duration<=0)throw Error('invalid duration '+file);out[file]=a.duration;a.removeAttribute('src');a.load()}return out}''',ready['files'])
 assert len(durations)==78
 passed('all 78 real narration clips load and decode',{'count':len(durations),'totalSeconds':round(sum(durations.values()),2)})
 speaker='window.actualSpeakers[0]'
 for kind in ['life','train']:
  page.locator(f'[data-intro="{kind}"]').click();page.locator('button[data-action="review"]').first.click()
  assert page.locator('.review-card').count()==len(data[kind])
  for q in data[kind]:
   page.locator(f'[data-audio="{q["audio"]}"]').click()
   page.wait_for_function(speaker+'.currentTime>.12 && !'+speaker+'.paused')
   assert page.evaluate(speaker+'.currentSrc').split('/')[-1]==q['audio']+'.mp3'
   assert page.evaluate(speaker+'.error') is None
  page.locator('[data-action="pause"]').click();t=page.evaluate(speaker+'.currentTime');page.wait_for_timeout(250)
  assert page.evaluate(speaker+'.paused') and abs(page.evaluate(speaker+'.currentTime')-t)<.08
  page.locator('[data-action="pause"]').click();page.wait_for_function(speaker+'.currentTime>'+str(t+.1))
  page.locator('button[data-action="home"]').click()
  assert page.evaluate(speaker+'.paused') and page.evaluate(speaker+'.getAttribute("src")') is None
 passed('all 15 review sentences play their matching real clips; pause/resume/home cleanup')
 # An actual answer must finish before advancement, with default browser autoplay policy.
 page.locator('[data-intro="life"]').click();page.locator('[data-action="start"]').click();q=data['life'][0]
 page.locator(f'[data-option="{q["correct"]}"]').click();page.locator('[data-action="act"]').click()
 page.wait_for_timeout(3000)
 if durations[data['audio'][q['audio']]['file']]>2:
  assert page.locator('[aria-current="step"]').inner_text()=='1'
 page.wait_for_function("document.querySelector('[aria-current=step]')?.textContent==='2'",timeout=25000)
 assert page.evaluate('window.audioEnded').count(base+data['audio'][q['audio']]['file'])==1
 passed('life actor action plays full real sentence and advances once after audio/animation')
 page.locator('button[data-action="home"]').click();page.locator('[data-intro="train"]').click();page.locator('[data-action="start"]').click();q=data['train'][0]
 for i,id in enumerate(q['tokens']):
  page.locator(f'#word-bank [data-token="{id}"]').click();page.locator(f'[data-slot="{i}"]').click()
 page.wait_for_function("document.querySelector('[aria-current=step]')?.textContent==='2'",timeout=25000)
 assert page.evaluate('window.audioEnded').count(base+data['audio'][q['audio']]['file'])==1
 page.locator('button[data-action="home"]').click()
 passed('train plays full real sentence and advances once after narration/departure')
 assert len(page.evaluate('window.actualSpeakers'))==1
 assert errors==[],errors;assert bad==[],bad
 passed('single playback channel; no JavaScript or HTTP asset errors')
 if base.startswith('https://'):
  page.screenshot(path=str(ROOT/'evidence/live-home-1280.png'))
  page.set_viewport_size({'width':1920,'height':1080});page.screenshot(path=str(ROOT/'evidence/live-home-1920.png'))
  page.locator('[data-intro="life"]').click();page.locator('[data-action="start"]').click();page.locator('[data-action="pause"]').click();page.screenshot(path=str(ROOT/'evidence/live-life-1920.png'))
  page.locator('button[data-action="home"]').click();page.locator('[data-intro="train"]').click();page.locator('[data-action="start"]').click();page.screenshot(path=str(ROOT/'evidence/live-train-1920.png'))
 b.close()
output=ROOT/args.output;output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'base_url':base,'results':results,'pronunciationListeningReview':'not an automated speech-recognition or human listening assessment'},ensure_ascii=False,indent=2)+'\n')
