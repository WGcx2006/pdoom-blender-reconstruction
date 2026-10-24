"""Build one or all native procedural scenes."""
from pathlib import Path
import sys
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene_library import build_scene
from blender.common import save_scene

args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
scene_id = args[0] if args else 'open'
scene = build_scene(scene_id)
save_scene(scene, Path(__file__).resolve().parents[1]/'scenes'/f'{scene_id}.blend')
print(f'BUILD_OK {scene_id}', flush=True)
