"""Blender-internal frame renderer with global filenames and resumable skips."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import time
import hashlib
import json
import bpy

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--frames',default='')
parser.add_argument('--start',type=int,default=1)
parser.add_argument('--end',type=int,default=0)
parser.add_argument('--step',type=int,default=1)
parser.add_argument('--output',required=True)
parser.add_argument('--scale',type=int,default=100)
parser.add_argument('--samples',type=int,default=16)
parser.add_argument('--no-motion-blur',action='store_true')
parser.add_argument('--force',action='store_true')
args = parser.parse_args(argv)
scene = bpy.context.scene
scene.render.resolution_percentage = args.scale
scene.render.use_motion_blur = not args.no_motion_blur if hasattr(scene.render,'use_motion_blur') else False
if hasattr(scene,'eevee'):
    for attr in ('taa_render_samples','taa_samples'):
        if hasattr(scene.eevee,attr):
            setattr(scene.eevee,attr,args.samples)
            break
output = Path(args.output)
output.mkdir(parents=True,exist_ok=True)
config = {'blend': bpy.data.filepath, 'blend_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
          'scale': args.scale, 'samples': args.samples, 'motion_blur': not args.no_motion_blur}
config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
config_path = output / 'render_config.json'
previous_hash = None
if config_path.is_file():
    try:
        previous_hash = json.loads(config_path.read_text()).get('hash')
    except Exception:
        previous_hash = None
cache_valid = previous_hash == config_hash
config_path.write_text(json.dumps({'hash': config_hash, **config}, indent=2))
if args.frames:
    frames = [int(x) for x in args.frames.split(',') if x.strip()]
else:
    end = args.end or scene.frame_end
    frames = list(range(args.start,end+1,args.step))
started = time.monotonic()
for index,local_frame in enumerate(frames,1):
    global_frame = scene['global_start_frame'] + local_frame - 1
    path = output / f'{global_frame:06d}.png'
    if cache_valid and path.is_file() and path.stat().st_size > 1024 and not args.force:
        print(f'SKIP {local_frame} {path}',flush=True)
        continue
    scene.frame_set(local_frame)
    scene.render.filepath = str(path)
    frame_started = time.monotonic()
    bpy.ops.render.render(write_still=True)
    print(f'FRAME {index}/{len(frames)} local={local_frame} global={global_frame} seconds={time.monotonic()-frame_started:.3f}',flush=True)
print(f'RENDER_COMPLETE frames={len(frames)} elapsed={time.monotonic()-started:.3f}',flush=True)
