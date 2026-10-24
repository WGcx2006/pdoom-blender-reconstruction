#!/usr/bin/env python3
"""Review frames decoded from the delivered MP4, not only the PNG sources."""
from pathlib import Path
import json
import cv2
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
video=ROOT/'deliverables'/'pdoom_blender_1080p60.mp4'
timeline=json.loads((ROOT/'src'/'timeline.json').read_text())
cap=cv2.VideoCapture(str(video))
items=[]; stats=[]
for scene in timeline['scenes']:
    frame=(scene['start_frame']+scene['end_frame']-1)//2
    cap.set(cv2.CAP_PROP_POS_FRAMES,frame)
    ok,bgr=cap.read()
    if not ok:
        raise RuntimeError(f'cannot decode frame {frame} {scene["id"]}')
    stats.append({'scene':scene['id'],'frame':frame,'mean':float(bgr.mean()),'std':float(bgr.std())})
    rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    im=Image.fromarray(rgb).resize((480,270))
    items.append((scene['id'],frame,im))
for name,frame in [('first',0),('last',timeline['total_frames']-1)]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,frame); ok,bgr=cap.read()
    if not ok: raise RuntimeError(f'cannot decode {name}')
    rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    Image.fromarray(rgb).save(ROOT/'reviews'/'full'/f'encoded_{name}.png')
cap.release()
cols=4; cw=500; ch=310
sheet=Image.new('RGB',(cols*cw,((len(items)+cols-1)//cols)*ch),(10,10,12)); draw=ImageDraw.Draw(sheet)
for i,(name,frame,im) in enumerate(items):
    x=(i%cols)*cw; y=(i//cols)*ch
    draw.text((x+12,y+8),f'{i+1:02d} {name} / f{frame}',fill=(238,233,223)); sheet.paste(im,(x+10,y+30))
out=ROOT/'reviews'/'full'/'encoded_contact_sheet.jpg'; sheet.save(out,quality=92)
(ROOT/'reviews'/'full'/'encoded_stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(out)
print('encoded review frames',len(items),'blackish', [x['scene'] for x in stats if x['mean']<0.5 and x['std']<0.5])
