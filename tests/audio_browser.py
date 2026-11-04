"""Native HTMLAudio lifecycle test using an isolated six-second test tone.
No fixture is shipped or mistaken for Cantonese narration.
"""
import os,shutil,json,pathlib,subprocess,tempfile
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'dist/content.json').read_text())
with tempfile.TemporaryDirectory() as folder:
 audio=pathlib.Path(folder)/'six-seconds.mp3'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','sine=frequency=440:duration=6','-q:a','8',str(audio)],check=True)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or shutil.which('chromium'),headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  page=b.new_page(viewport={'width':1280,'height':720})
  page.add_init_script('''window.testMedia=[];const NativeAudio=window.Audio;window.Audio=function(...args){const a=new NativeAudio(...args);window.testMedia.push(a);return a;};''')
  page.route('**/audio-ready.json',lambda r:r.fulfill(json={'files':[v['file'] for v in data['audio'].values()]}))
  page.route('**/assets/audio/*.mp3',lambda r:r.fulfill(path=str(audio),content_type='audio/mpeg'))
  page.goto('http://127.0.0.1:8793',wait_until='networkidle')
  page.locator('[data-intro="life"]').click();page.locator('[data-action="start"]').click()
  q=data['life'][0];page.locator(f'[data-option="{q["correct"]}"]').click();page.locator('[data-action="act"]').click()
  page.wait_for_timeout(1800)
  media='window.testMedia[0]'
  assert page.evaluate(media+'.currentTime')>0
  page.locator('[data-action="pause"]').click();t=page.evaluate(media+'.currentTime');page.wait_for_timeout(450)
  assert page.evaluate(media+'.paused') and abs(page.evaluate(media+'.currentTime')-t)<.08
  page.locator('[data-action="pause"]').click();page.wait_for_timeout(1400)
  assert page.locator('[aria-current="step"]').inner_text()=='1','must wait for six-second audio after animation'
  page.wait_for_function("document.querySelector('[aria-current=step]')?.textContent==='2'",timeout=20000)
  print('PASS native audio pause/resume and both audio/animation completion gates')
  # Mute during a currently playing answer must settle its gate exactly once.
  q=data['life'][1];page.locator(f'[data-option="{q["correct"]}"]').click();page.locator('[data-action="act"]').click();page.wait_for_timeout(1800)
  page.locator('[data-action="sound"]').click();assert page.evaluate(media+'.paused');page.wait_for_function("document.querySelector('[aria-current=step]')?.textContent==='3'",timeout=10000)
  print('PASS muting mid-answer stops audio and advances once')
  page.locator('[data-action="sound"]').click();page.locator('[data-action="read"]').click();page.wait_for_timeout(200)
  page.locator('[data-jump="7"]').click();page.locator('button[data-action="home"]').click();page.wait_for_timeout(500)
  assert page.evaluate(media+'.paused') and page.evaluate(media+'.getAttribute("src")') is None
  assert page.locator('[data-intro]').count()==2
  print('PASS jump/home clears native audio and leaves no delayed transition')
  page.locator('[data-intro="life"]').click();page.locator('button[data-action="review"]').first.click()
  page.locator('[data-audio]').first.click();page.wait_for_timeout(250)
  page.locator('[data-action="pause"]').click();t=page.evaluate(media+'.currentTime');page.wait_for_timeout(250)
  assert page.evaluate(media+'.paused') and abs(page.evaluate(media+'.currentTime')-t)<.08
  assert page.locator('.review-card').count()==10 and page.locator('[role="dialog"]').count()==0
  page.locator('[data-action="pause"]').click()
  page.wait_for_function(media+'.currentTime>'+str(t+.1))
  print('PASS review audio direct freeze/resume without hiding pictures')
  (ROOT/'evidence/audio-browser-results.json').write_text(json.dumps({'passed':4,'fixture':'isolated six-second tone, never production narration','checks':['native audio pause/resume and both completion gates','mute stops audio and advances once','jump/home clears audio and stale transitions','review voice pause/resume without overlay']},ensure_ascii=False,indent=2)+'\n')
  b.close()
