#!/usr/bin/env python3
"""Encode the continuous Blender PNG sequence without altering its visuals."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--preview',action='store_true'); p.add_argument('--output',default=''); args=p.parse_args()
    timeline=json.loads((ROOT/'src'/'timeline.json').read_text()); total=timeline['total_frames']
    source=ROOT/'renders'/('preview' if args.preview else 'final')
    seq=source/'sequence'; seq.mkdir(parents=True,exist_ok=True)
    for scene in timeline['scenes']:
        directory=source/scene['id']
        for frame in range(scene['start_frame'],scene['end_frame']):
            src=directory/f'{frame:06d}.png'; dst=seq/f'{frame:06d}.png'
            if not src.is_file(): raise FileNotFoundError(src)
            if not dst.exists(): os.link(src,dst)
    missing=[i for i in range(total) if not (seq/f'{i:06d}.png').is_file()]
    if missing: raise RuntimeError(f'missing frames: {missing[:10]} count={len(missing)}')
    output=Path(args.output) if args.output else ROOT/'deliverables'/'pdoom_blender_1080p60.mp4'
    output.parent.mkdir(parents=True,exist_ok=True)
    audio=ROOT/'assets'/'audio'/'pdoom.mp3'
    cmd=['ffmpeg','-y','-framerate','60','-start_number','0','-i',str(seq/'%06d.png'),'-i',str(audio),
         '-map','0:v:0','-map','1:a:0','-vf','scale=out_color_matrix=bt709,setparams=color_primaries=bt709:color_trc=bt709',
         '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-tune','grain',
         '-c:a','aac','-b:a','320k','-shortest','-movflags','+faststart',str(output)]
    print(' '.join(cmd),flush=True); subprocess.run(cmd,check=True)
    print(f'ENCODED {output}',flush=True)

if __name__=='__main__': main()
