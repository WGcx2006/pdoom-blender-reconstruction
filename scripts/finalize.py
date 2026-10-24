#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
video=ROOT/'deliverables'/'pdoom_blender_1080p60.mp4'
validation=json.loads((ROOT/'deliverables'/'pdoom_blender_1080p60.ffprobe.json').read_text())
assert validation['passed']
result={
 'status':'completed_native_blender_reconstruction',
 'video':'deliverables/pdoom_blender_1080p60.mp4',
 'master':'src/pdoom_master.blend',
 'scene_manifest':'deliverables/scene_manifest.json',
 'scene_count':22,
 'blender_version':'5.2.2 LTS',
 'render_engine':'BLENDER_EEVEE',
 'resolution':[1920,1080],
 'fps':60,
 'frames':9399,
 'duration_seconds':156.650,
 'video_codec':'H.264 / libx264 CRF16',
 'pixel_format':'yuv420p',
 'color':'BT.709',
 'audio':'AAC 320k stereo 48kHz',
 'bytes':video.stat().st_size,
 'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
 'sequence_check':'9399/9399 frames present; zero missing; zero invalid; 240 sampled non-black frames',
 'encoded_review':'22 scene midpoints decoded from delivered MP4; no blackish midpoint',
 'loop_source_mae':0.0,
 'loop_encoded_mae':0.07806648662551441,
 'reference_basis':'66 valid locally rendered stills at fixed commit fa164b74; not a full reference-video comparison',
 'review':'reviews/full/review.json and reviews/full/encoded_contact_sheet.jpg',
 'known_approximations':[
   'Original GLSL/SDF detail is rebuilt with native Blender tube meshes, curves, procedural materials and editable typography',
   'Some secondary lyric/layout and high-frequency engraving details are simplified',
   'The reference auto-sampled short capture was stopped after more than one hour without a completed first clip'
 ],
 'local_use_only':'Original audio and lyrics are not covered by the repository MIT license; no public redistribution is made here'
}
out=ROOT/'deliverables'/'reproduction_result.json'; out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
review_path=ROOT/'reviews'/'full'/'review.json'
review=json.loads(review_path.read_text())
review['full_video_status']='completed_and_validated'
review['final_validation']='1920x1080 / 60fps / 9399 frames / 156.650s / H.264 / BT.709 / AAC / full decode passed'
review['loop_refinement']='Native opening cover and matching crop marks; source first/last MAE=0; encoded first/last MAE=0.078066 due to H.264 compression'
review['final_encoded_contact_sheet']='reviews/full/encoded_contact_sheet.jpg'
review_path.write_text(json.dumps(review,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
