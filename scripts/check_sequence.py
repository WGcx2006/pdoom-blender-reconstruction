#!/usr/bin/env python3
"""Check frame continuity and sample image statistics without altering renders."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--final',action='store_true'); p.add_argument('--samples',type=int,default=120); args=p.parse_args()
    timeline=json.loads((ROOT/'src'/'timeline.json').read_text())
    base=ROOT/'renders'/('final' if args.final else 'preview')
    missing=[]; invalid=[]; stats=[]
    frames=list(range(timeline['total_frames']))
    scene_for={}
    for s in timeline['scenes']:
        for f in range(s['start_frame'],s['end_frame']): scene_for[f]=s['id']
    for f in frames:
        path=base/scene_for[f]/f'{f:06d}.png'
        if not path.is_file(): missing.append(f)
    available=[f for f in frames if f not in set(missing)]
    if available:
        indices=np.linspace(0,len(available)-1,min(args.samples,len(available)),dtype=int)
        for i in indices:
            f=available[i]; path=base/scene_for[f]/f'{f:06d}.png'
            im=cv2.imread(str(path))
            if im is None or im.size==0:
                invalid.append(f); continue
            stats.append({'frame':f,'mean':float(im.mean()),'std':float(im.std()),'bytes':path.stat().st_size})
    black=[x['frame'] for x in stats if x['mean']<0.5 and x['std']<0.5]
    result={'base':str(base),'expected_frames':timeline['total_frames'],'present_frames':len(available),
            'missing_count':len(missing),'missing_first':missing[:30],'invalid':invalid,
            'sample_count':len(stats),'black_sample_frames':black,'stats':stats,
            'complete':not missing and not invalid}
    out=ROOT/'renders'/'manifests'/('sequence_final.json' if args.final else 'sequence_preview.json')
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='stats'},indent=2),flush=True)
    if args.final and not result['complete']: raise SystemExit(1)

if __name__=='__main__': main()
