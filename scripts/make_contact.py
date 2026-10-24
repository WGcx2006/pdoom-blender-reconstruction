#!/usr/bin/env python3
from pathlib import Path
import json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
timeline=json.loads((ROOT/'src'/'timeline.json').read_text())
items=[]
for scene in timeline['scenes']:
    frame=scene['start_frame']
    path=ROOT/'renders'/'preview'/scene['id']/f'{frame:06d}.png'
    if path.is_file():
        im=Image.open(path).convert('RGB').resize((480,270))
        items.append((scene['id'],im))
cols=4; cellw=500; cellh=310
sheet=Image.new('RGB',(cols*cellw,((len(items)+cols-1)//cols)*cellh),(10,10,12))
draw=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(items):
    x=(i%cols)*cellw; y=(i//cols)*cellh
    draw.text((x+12,y+8),f'{i+1:02d}  {name}',fill=(238,233,223))
    sheet.paste(im,(x+10,y+30))
out=ROOT/'reviews'/'full'; out.mkdir(parents=True,exist_ok=True)
sheet.save(out/'timeline_contact_sheet.jpg',quality=92)
print(out/'timeline_contact_sheet.jpg')
