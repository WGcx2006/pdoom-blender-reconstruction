#!/usr/bin/env python3
"""Render a scene or all scenes through Blender's native renderer."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BLENDER = Path(r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
RENDERER = ROOT/'src'/'blender'/'render_scene.py'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('scene', help='scene id or all')
    p.add_argument('--frames', default='')
    p.add_argument('--start', type=int, default=1)
    p.add_argument('--end', type=int, default=0)
    p.add_argument('--step', type=int, default=1)
    p.add_argument('--scale', type=int, default=100)
    p.add_argument('--samples', type=int, default=16)
    p.add_argument('--preview', action='store_true')
    p.add_argument('--no-motion-blur', action='store_true')
    p.add_argument('--force', action='store_true')
    args = p.parse_args()
    timeline = json.loads((ROOT/'src'/'timeline.json').read_text())
    ids = [x['id'] for x in timeline['scenes']] if args.scene == 'all' else [args.scene]
    records = []
    for scene_id in ids:
        blend = ROOT/'src'/'scenes'/f'{scene_id}.blend'
        if not blend.is_file():
            raise FileNotFoundError(blend)
        out = ROOT/'renders'/('preview' if args.preview else 'final')/scene_id
        out.mkdir(parents=True, exist_ok=True)
        log = ROOT/'renders'/'logs'/f'{scene_id}_{"preview" if args.preview else "final"}.log'
        log.parent.mkdir(parents=True, exist_ok=True)
        cmd = [str(BLENDER), '-b', str(blend), '--python-exit-code', '1', '--python', str(RENDERER), '--',
               '--frames', args.frames, '--start', str(args.start), '--end', str(args.end),
               '--step', str(args.step), '--output', str(out), '--scale', str(args.scale),
               '--samples', str(args.samples)]
        if args.no_motion_blur: cmd.append('--no-motion-blur')
        if args.force: cmd.append('--force')
        started = time.time()
        with log.open('w', encoding='utf-8') as handle:
            result = subprocess.run(cmd, stdout=handle, stderr=subprocess.STDOUT, check=False)
        record = {'scene': scene_id, 'command': cmd, 'exit_code': result.returncode,
                  'seconds': round(time.time()-started,3), 'log': str(log)}
        records.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if result.returncode != 0:
            raise RuntimeError(f'render failed: {scene_id}; see {log}')
    (ROOT/'renders'/'manifests').mkdir(parents=True, exist_ok=True)
    (ROOT/'renders'/'manifests'/f'{args.scene}_render.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
