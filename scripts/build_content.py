import json,hashlib,re,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
raw=[
('bottle','小明','打開水樽蓋','可以喝水',['刷牙','拍球']),
('bag','小美','打開書包','可以拿出課本',['洗手','跳繩']),
('tap','我','打開水龍頭','可以洗手',['畫畫','踢球']),
('ticket','我們','拿出車票','可以坐火車',['梳頭','掃地']),
('queue','小朋友','排好隊','可以上校巴',['吃雪糕','畫圖畫']),
('lamp','小明','按下開關','可以開燈',['可以踢球','可以吃香蕉']),
('milk','小美','打開雪櫃門','可以拿出牛奶',['可以跳繩','可以梳頭']),
('pencil','我','打開筆袋','可以拿出橡皮擦',['可以游泳','可以吃西瓜']),
('post','小明','貼上郵票','可以寄出這封信',['可以洗臉','可以踢足球']),
('lift','小美','按下按鈕','可以叫來升降機',['可以刷牙','可以吃餅乾'])]
trainraw=[
('box','我','打開盒蓋','可以拿出盒內的餅乾',['我','只有','打開盒蓋','，','才','可以拿出','盒內的餅乾','。']),
('umbrella','雨傘','打開','可以擋雨',['雨傘','只有','打開','，','才','可以擋雨','。']),
('glue','小明','打開膠水蓋','可以塗膠水',['小明','只有','打開','膠水蓋','，','才','可以塗膠水','。']),
('juice','我','投入硬幣','可以買到果汁',['我','只有','投入硬幣','，','才','可以買到','果汁','。']),
('flower','小花','得到水分','可以繼續生長',['小花','只有','得到水分','，','才','可以繼續','生長','。'])]
# Curated contextual readings; checked against retained CUHK evidence by verify_cuhk.py.
readings='樽:zeon1 喝:hot3 小:siu2 明:ming4 美:mei5 我:ngo5 們:mun4 朋:pang4 友:jau5 只:zi2 有:jau5 才:coi4 用:jung6 鑰:joek6 匙:si4 開:hoi1 鎖:so2 可:ho2 以:ji5 打:daa2 門:mun4 書:syu1 包:baau1 拿:naa4 出:ceot1 課:fo3 本:bun2 水:seoi2 龍:lung4 頭:tau4 洗:sai2 手:sau2 車:ce1 票:piu3 坐:co5 火:fo2 排:paai4 好:hou2 隊:deoi6 上:soeng5 校:haau6 巴:baa1 按:on3 下:haa6 關:gwaan1 燈:dang1 雪:syut3 櫃:gwai6 牛:ngau4 奶:naai5 筆:bat1 袋:doi6 橡:zoeng6 皮:pei4 擦:caat3 貼:tip3 郵:jau4 寄:gei3 這:ze5 封:fung1 信:seon3 鈕:nau2 叫:giu3 來:loi4 升:sing1 降:gong3 機:gei1 刷:caat3 牙:ngaa4 拍:paak3 球:kau4 跳:tiu3 繩:sing4 畫:waa2 踢:tek3 梳:so1 掃:sou3 地:dei6 吃:hek3 糕:gou1 圖:tou4 香:hoeng1 蕉:ziu1 游:jau4 泳:wing6 西:sai1 瓜:gwaa1 臉:lim5 足:zuk1 餅:beng2 乾:gon1 盒:hap6 蓋:goi3 內:noi6 的:dik1 雨:jyu5 傘:saan3 擋:dong2 膠:gaau1 塗:tou4 投:tau4 入:jap6 硬:ngaang6 幣:bai6 買:maai5 到:dou3 果:gwo2 汁:zap1 花:faa1 得:dak1 分:fan6 繼:gai3 續:zuk6 生:saang1 長:zoeng2'
charjp=dict(x.split(':') for x in readings.split())
words={}; audio={}
def clip(text,kind):
 id='zyc-v1-'+kind+'-'+hashlib.sha256(text.encode()).hexdigest()[:12]
 audio[id]={'text':text,'file':'assets/audio/'+id+'.mp3','voice':'zh-HK-HiuMaanNeural'}
 return id

def word(text,picture):
 key='w-'+hashlib.sha256(text.encode()).hexdigest()[:10]
 if key not in words:
  jp=' '.join(charjp[c] for c in text if c not in '，。')
  words[key]={'id':key,'text':text,'jyutpingTones':jp,'jyutping':re.sub('[1-6]','',jp),'picture':picture,'audio':clip({'，':'逗號','。':'句號'}.get(text,text),'word')}
 return key
levels=[]
condition_frames=[6,7,7,7,5,6,8,8,7,6]
result_frames=[15,15,15,15,15,15,15,15,12,15]
# Deliberately nonperiodic answer positions, same order for retries.
positions=[1,2,0,2,1,0,1,0,2,1]
for i,(scene,subject,condition,result,distractors) in enumerate(raw):
 mode='condition' if i<5 else 'result';answer=condition if i<5 else result
 options=[word(t,{'kind':'vocab','key':t.removeprefix('可以')}) for t in distractors]
 correct=word(answer,{'kind':'scene','scene':scene,'frame':condition_frames[i] if i<5 else result_frames[i]})
 options.insert(positions[i],correct)
 sentence=f'{subject}只有{condition}，才{result}。'
 prompt=f'{subject}只有'+('【？】' if i<5 else condition)+'，才'+(result if i<5 else '【？】')+'。'
 levels.append({'id':'life-'+scene,'scene':scene,'subject':subject,'condition':condition,'result':result,'mode':mode,'sentence':sentence,'prompt':prompt,'options':options,'correct':correct,'audio':clip(sentence,'sentence'),'questionAudio':clip(prompt.replace('【？】','……'),'question'),'frames':16,'conditionFrame':condition_frames[i],'resultFrame':result_frames[i]})
trains=[]
for i,(scene,subject,condition,result,tokens) in enumerate(trainraw):
 ids=[]
 for text in tokens:
  if text in ['，','。']: pic=None
  elif text in ['只有','才']:pic={'kind':'relation','key':text}
  elif text in ['我','小明']:pic={'kind':'person','key':text}
  else:pic={'kind':'train','scene':scene,'panel':0 if text in [subject,condition,'打開','膠水蓋','投入硬幣','得到水分'] else 1}
  ids.append(word(text,pic))
 sentence=f'{subject}只有{condition}，才{result}。'
 trains.append({'id':'train-'+scene,'scene':scene,'subject':subject,'condition':condition,'result':result,'sentence':sentence,'tokens':ids,'showLengthHints':i<3,'audio':clip(sentence,'sentence'),'frames':16})
for text in ['再試一試。','答對了！'] : clip(text,'feedback')
out={'life':levels,'train':trains,'words':words,'audio':audio,'feedback':{t:clip(t,'feedback') for t in ['再試一試。','答對了！']}}
(root/'dist/content.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if not (root/'dist/audio-ready.json').exists(): (root/'dist/audio-ready.json').write_text('{"files": []}\n')
used=set(''.join(w['text'] for w in words.values())+''.join(q['sentence'] for q in levels+trains))
charjp={c:jp for c,jp in charjp.items() if c in used}
(root/'references/readings-curated.json').write_text(json.dumps(charjp,ensure_ascii=False,indent=2)+'\n')
print(len(levels),'life',len(trains),'train',len(words),'words',len(audio),'clips')
