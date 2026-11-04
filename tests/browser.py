"""Cloud Chromium integration checks. Run with a server on 8793; no teacher PC."""
import os,shutil,json,pathlib,time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'dist/content.json').read_text())
OUT=ROOT/'evidence';OUT.mkdir(exist_ok=True)
results=[]
def record(name,details=''):results.append({'name':name,'status':'passed','details':details});print('PASS',name,flush=True)
def home(page):page.locator('button[data-action="home"]').click()
def start(page,kind):
 home(page) if page.locator('button[data-action="home"]').count() else None
 page.locator(f'[data-intro="{kind}"]').click();page.locator('[data-action="start"]').click()
def point(page,selector):
 box=page.locator(selector).bounding_box();assert box,selector
 return {'x':box['x']+box['width']/2,'y':box['y']+box['height']/2}
def click_token(page,id,slot):
 page.locator(f'#word-bank [data-token="{id}"]').click()
 page.locator(f'[data-slot="{slot}"]').click()
def slottext(page,i):return page.locator(f'[data-slot="{i}"] .car-content').inner_text()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1280,'height':720},has_touch=True)
 errors=[];bad=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:bad.append(str(r.status)+' '+r.url) if r.status>=400 else None)
 page.goto(os.environ.get('GAME_TEST_URL','http://127.0.0.1:8793/'),wait_until='networkidle');page.evaluate('document.fonts.ready')
 assert page.locator('[data-intro]').count()==2
 home_text=page.locator('body').inner_text()
 assert all(text not in home_text for text in ['小島中文','小島生活任務','小島句子列車'])
 assert '小島中文' not in page.title()
 typography=page.locator('body').evaluate('(el)=>({weight:getComputedStyle(el).fontWeight,stroke:getComputedStyle(el).webkitTextStrokeWidth,family:getComputedStyle(el).fontFamily})')
 assert int(typography['weight'])>=900 and float(typography['stroke'].removesuffix('px'))>=.3
 assert '標楷體' in typography['family'] or 'EducationKai' in typography['family']
 assert 'home-island-background-v1.png' in page.locator('body').evaluate('(el)=>getComputedStyle(el).backgroundImage')
 record('homepage has two picture entrances, requested text removed, illustrated background and bold Kai')
 page.screenshot(path=str(OUT/'home-1280.png'))
 # Playback is explicitly muted because production voice generation has separate readiness checks.
 page.locator('[data-action="sound"]').click()
 for width,height in [(1280,720),(1920,1080)]:
  page.set_viewport_size({'width':width,'height':height})
  for kind in ['life','train']:
   start(page,kind)
   for i,q in enumerate(DATA[kind]):
    page.locator(f'[data-jump="{i}"]').click()
    last=page.locator('.life-bottom' if kind=='life' else '.word-bank').bounding_box()
    assert last['y']+last['height']<=height,(width,height,kind,i,last)
    for selector in ['header','.question-nav','.life-options' if kind=='life' else '.train-track']:
     r=page.locator(selector).bounding_box();assert r['x']>=0 and r['x']+r['width']<=width+1,(selector,r)
    cards=page.locator('.life-options .word-card' if kind=='life' else '.word-bank .word-card')
    assert cards.count()==(3 if kind=='life' else len(q['tokens']))
    assert page.locator('.train-slot').count()==(len(q['tokens']) if kind=='train' else 0)
    for el in cards.all():
     assert el.evaluate('(el)=>el.scrollHeight<=el.clientHeight+1'),el.inner_text()
    if i in [0,5] or kind=='train' and i==3:page.screenshot(path=str(OUT/f'{kind}-{i+1}-{width}.png'))
   record(f'{width}×{height} {kind}: all question layouts and cards fit')
 # Island: every question, retries, action gate, alternation, left/right visual gap.
 page.set_viewport_size({'width':1280,'height':720});start(page,'life')
 for i,q in enumerate(DATA['life']):
  page.locator(f'[data-jump="{i}"]').click()
  assert page.locator('.empty-cell').get_attribute('data-side')==('left' if i<5 else 'right')
  assert '選條件' not in page.locator('main').inner_text() and '選結果' not in page.locator('main').inner_text()
  wrong=next(id for id in q['options'] if id!=q['correct'])
  page.locator(f'[data-option="{wrong}"]').click();assert page.locator('.word-card.wrong').count()==1
  assert page.locator('[data-action="act"]').is_disabled()
  page.locator(f'[data-option="{q["correct"]}"]').click()
  assert page.locator('.gap').count()==0 and page.locator('[data-action="act"]').is_enabled()
  expected=2 if i%2==0 else 1
  assert page.locator('[data-action="act"]').get_attribute('aria-label')==f'同學 {expected} 觸發動作'
  page.wait_for_timeout(100);assert page.locator('[aria-current="step"]').inner_text()==str(i+1)
 record('all 10 life questions: unique answer UI, retry, visual side, role/action gate')
 # Real animation frames, direct freeze, controls responsive on pause, and cleanup.
 page.locator('[data-jump="0"]').click();q=DATA['life'][0]
 page.locator(f'[data-option="{q["correct"]}"]').click();page.locator('[data-action="act"]').click();page.wait_for_timeout(700)
 page.locator('[data-action="pause"]').click();frame=page.locator('[data-side="right"] .scene').get_attribute('data-frame')
 page.wait_for_timeout(700);assert page.locator('[data-side="right"] .scene').get_attribute('data-frame')==frame
 assert page.locator('.paused').count()==1 and page.locator('[role="dialog"]').count()==0
 page.locator('[data-action="pause"]').click();page.wait_for_timeout(500)
 assert page.locator('[data-side="right"] .scene').get_attribute('data-frame')!=frame
 page.locator('[data-jump="5"]').click();page.wait_for_timeout(2200)
 assert page.locator('[aria-current="step"]').inner_text()=='6'
 page.locator('[data-action="restart"]').click();assert page.locator('[aria-current="step"]').inner_text()=='1'
 record('life animation frame progression, pause/resume, jump cancels pending advance, restart')
 # Last question leads to complete review only after actor triggers and animation finishes.
 page.locator('[data-jump="9"]').click();q=DATA['life'][9]
 page.locator(f'[data-option="{q["correct"]}"]').click();page.locator('[data-action="act"]').click()
 page.wait_for_selector('.review-grid');assert page.locator('.review-card').count()==10
 record('life final question enters all-10 review')
 # Train click and keyboard alternative, replacement and return to word bank.
 start(page,'train');q=DATA['train'][0];a,c=q['tokens'][:2]
 click_token(page,a,0);click_token(page,c,1)
 page.locator('[data-slot="0"]').click();page.locator('[data-slot="1"]').click()
 assert slottext(page,0)==DATA['words'][c]['text'] and slottext(page,1)==DATA['words'][a]['text']
 page.locator('[data-slot="1"]').focus();page.keyboard.press('Delete');assert slottext(page,1)==''
 page.locator(f'#word-bank [data-token="{a}"]').focus();page.keyboard.press('Enter')
 page.locator('[data-slot="1"]').focus();page.keyboard.press('Enter');assert slottext(page,1)==DATA['words'][a]['text']
 record('train click placement, swap, keyboard select/place/delete')
 # CDP sends two real simultaneous touch contacts through native Pointer Events.
 page.locator('[data-jump="0"]').click();session=page.context.new_cdp_session(page)
 a,c=q['tokens'][:2];p1=point(page,f'#word-bank [data-token="{a}"]');p2=point(page,f'#word-bank [data-token="{c}"]')
 t1=point(page,'[data-slot="0"]');t2=point(page,'[data-slot="1"]')
 session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[dict(p1,id=1),dict(p2,id=2)]})
 session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[dict(t1,id=1),dict(t2,id=2)]})
 assert page.locator('.drag-ghost').count()==2
 session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[dict(t2,id=2)]})
 session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 assert slottext(page,0)==DATA['words'][a]['text'] and slottext(page,1)==DATA['words'][c]['text']
 assert page.locator('.drag-ghost').count()==0
 record('two simultaneous native touch drags, independent releases and cleanup')
 # Reject picking the same card twice.
 page.locator('[data-jump="0"]').click();p1=point(page,f'#word-bank [data-token="{a}"]')
 session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[dict(p1,id=1),dict(p1,id=2)]})
 session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[dict(t1,id=1),dict(t2,id=2)]})
 assert page.locator('.drag-ghost').count()==1
 session.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]})
 assert page.locator('.drag-ghost').count()==0 and page.locator('.train-slot[data-token]').count()==0
 record('same card ownership and touch cancellation preserve bank')
 # Drag a placed token back into bank (not Delete shortcut).
 click_token(page,a,0);p1=point(page,'[data-slot="0"]');bank=page.locator('#word-bank').bounding_box();dest={'x':bank['x']+3,'y':bank['y']+3}
 page.mouse.move(**p1);page.mouse.down();page.mouse.move(**dest,steps=5);page.mouse.up()
 assert slottext(page,0)==''
 record('drag placed card back to bank')
 # Wrong arrangements retain cards and show only the wrong positions.
 for i,id in enumerate(q['tokens']):click_token(page,id,(1 if i==0 else 0 if i==1 else i))
 assert page.locator('.wrong-slot').count()==2 and page.locator('.train-slot[data-token]').count()==len(q['tokens'])
 page.locator('[data-slot="0"]').click();page.locator('[data-slot="1"]').click()
 page.wait_for_timeout(600);f=page.locator('[data-engine]').get_attribute('data-frame');assert int(f)>0
 page.locator('[data-action="pause"]').click();position=page.locator('#rake').get_attribute('style');page.wait_for_timeout(500)
 assert page.locator('[data-engine]').get_attribute('data-frame')==f and page.locator('#rake').get_attribute('style')==position
 page.locator('[data-action="pause"]').click();page.wait_for_selector('[aria-current="step"]:has-text("2")')
 record('wrong positions retained; correct train uses changing wheel/steam frames; departure freeze and advance')
 # Solve every remaining sentence including high-tier equal blanks and last review.
 for i,q in enumerate(DATA['train'][1:],start=1):
  page.locator(f'[data-jump="{i}"]').click()
  if i>=3:assert page.locator('.slot-gap[style]').count()==0
  for j,id in enumerate(q['tokens']):click_token(page,id,j)
  page.wait_for_timeout(3300)
 assert page.locator('.review-card').count()==5
 record('all five train sentences complete and final review contains all five')
 # Direct review access from introductions and active rounds.
 for kind in ['life','train']:
  home(page);page.locator(f'[data-intro="{kind}"]').click();page.locator('button[data-action="review"]').first.click();assert page.locator('.review-card').count()==len(DATA[kind])
  page.locator('[data-action="restart"]').click();page.locator('button[data-action="review"]').first.click();assert page.locator('.review-card').count()==len(DATA[kind])
 record('complete reviews accessible from both intro and play')
 assert errors==[],errors;assert bad==[],bad
 record('no browser exceptions or failed local assets')
 results.append({'name':'production voice playback / CUHK new characters / live Pages','status':'unrun','details':'Separate release/manual checks; this suite tests progression using explicit mute and does not certify narration pronunciation or live Pages.'})
 (OUT/'browser-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 b.close()
