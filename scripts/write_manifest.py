#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
timeline=json.loads((ROOT/'src'/'timeline.json').read_text())
scenes=[]
for item in timeline['scenes']:
    blend=ROOT/'src'/'scenes'/f"{item['id']}.blend"
    scenes.append({**item,'blend':str(blend),'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
                   'builder': 'src/builders/build_ilya.py' if item['id']=='ilya' else 'src/builders/scene_library.py',
                   'native_blender':True})
manifest={'project':'pdoom-video Blender reconstruction','reference_commit':'fa164b74fd0b26a99375715b619c55b4a0fb3d05',
          'blender_version':'5.2.2 LTS','resolution':[1920,1080],'fps':60,'total_frames':9399,
          'master':'src/pdoom_master.blend','scenes':scenes,
          'render_engine':'BLENDER_EEVEE','samples':8,'motion_blur_shutter':0.2,
          'encoding':{'video':'libx264','crf':16,'pixel_format':'yuv420p','color':'BT.709','audio':'AAC 320k'}}
out=ROOT/'deliverables'/'scene_manifest.json'; out.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(out)
