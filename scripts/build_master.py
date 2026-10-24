"""Assemble all independently rendered scenes into a reviewable master blend."""
from pathlib import Path
import bpy
import json
ROOT=Path(__file__).resolve().parents[1]
timeline=json.loads((ROOT/'src'/'timeline.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
master=bpy.context.scene
master.name='PDOOM_MASTER_1080P60'
master.render.resolution_x=1920; master.render.resolution_y=1080; master.render.resolution_percentage=100
master.render.fps=60; master.frame_start=1; master.frame_end=timeline['total_frames']
master['reference_commit']='fa164b74fd0b26a99375715b619c55b4a0fb3d05'
master['scene_count']=22
for item in timeline['scenes']:
    path=ROOT/'src'/'scenes'/f"{item['id']}.blend"
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):
        dst.scenes=[item['id']]
    master.timeline_markers.new(item['id'],frame=item['start_frame']+1)
master['timeline_json']='src/timeline.json'
master['render_note']='Final frames are rendered from individual scene blends; master is for integrated inspection.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'src'/'pdoom_master.blend'),check_existing=False)
print('MASTER_OK',len(bpy.data.scenes),flush=True)
