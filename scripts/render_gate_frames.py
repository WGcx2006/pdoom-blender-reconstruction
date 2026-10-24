#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
timeline={x['id']:x for x in json.loads((ROOT/'src'/'timeline.json').read_text())['scenes']}
gates={
 'shoggoth':[29.88,30.65,34.0,36.0,38.32],
 'paperclips':[96.70,97.50,99.32,100.80,101.95],
 'ilya':[131.69,133.50,135.91,137.50,140.13],
 'outro':[140.33,144.0,148.44,152.0,156.55],
}
for scene,times in gates.items():
    info=timeline[scene]
    frames=[round(t*60)-info['start_frame']+1 for t in times]
    cmd=[sys.executable,str(ROOT/'scripts'/'render_frames.py'),scene,'--frames',','.join(map(str,frames)),'--scale','50','--samples','12','--preview','--no-motion-blur','--force']
    print('GATE',scene,frames,flush=True)
    result=subprocess.run(cmd,check=False)
    if result.returncode: raise SystemExit(result.returncode)
print('GATE_FRAMES_OK',flush=True)
