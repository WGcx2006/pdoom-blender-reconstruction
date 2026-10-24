#!/usr/bin/env python3
"""Validate final video metadata, frame sequence and decodeability."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    video=ROOT/'deliverables'/'pdoom_blender_1080p60.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    streams=probe['streams']; v=next(s for s in streams if s['codec_type']=='video'); a=next((s for s in streams if s['codec_type']=='audio'),{})
    checks={'width':v.get('width')==1920,'height':v.get('height')==1080,'fps':v.get('avg_frame_rate')=='60/1',
            'frames':int(v.get('nb_frames',-1))==9399,'h264':v.get('codec_name')=='h264',
            'pixel_format':v.get('pix_fmt')=='yuv420p','bt709':v.get('color_space')=='bt709',
            'audio':a.get('codec_name')=='aac'}
    decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
    checks['decode']=decode.returncode==0
    result={'video':str(video),'checks':checks,'passed':all(checks.values()),'video_stream':v,'audio_stream':a,'decode_stderr':decode.stderr}
    out=ROOT/'deliverables'/'pdoom_blender_1080p60.ffprobe.json'; out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)
    if not result['passed']: raise SystemExit(1)

if __name__=='__main__': main()
