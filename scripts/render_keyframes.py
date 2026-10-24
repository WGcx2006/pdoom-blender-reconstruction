#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
timeline=json.loads((ROOT/'src'/'timeline.json').read_text())
for scene in timeline['scenes']:
    if scene['frame_count'] < 3:
        continue
    mid=scene['frame_count']//2+1
    end=scene['frame_count']-2
    frames=f'1,{mid},{end}'
    cmd=[sys.executable,str(ROOT/'scripts'/'render_frames.py'),scene['id'],'--frames',frames,'--scale','50','--samples','8','--preview','--no-motion-blur']
    print('KEYFRAMES',scene['id'],frames,flush=True)
    result=subprocess.run(cmd,check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
print('ALL_KEYFRAMES_OK',flush=True)
