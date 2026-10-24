"""Scene setup, global/local frame mapping and reproducible render defaults."""
from __future__ import annotations
from functools import lru_cache
import json
import math
from pathlib import Path
import bpy
from .palette import rgba

ROOT = Path(__file__).resolve().parents[2]
FPS = 60


@lru_cache(maxsize=1)
def timeline():
    return json.loads((ROOT / 'src' / 'timeline.json').read_text(encoding='utf-8'))


def scene_info(scene_id):
    return next(item for item in timeline()['scenes'] if item['id'] == scene_id)


def js_round(value):
    return math.floor(value + 0.5)


def global_to_local(info, global_frame):
    return global_frame - info['start_frame'] + 1


def local_to_global(info, local_frame):
    return info['start_frame'] + local_frame - 1


def time_to_local(info, seconds):
    return js_round(seconds * FPS) - info['start_frame'] + 1


def local_to_time(info, local_frame):
    return local_to_global(info, local_frame) / FPS


def setup_scene(scene_id, preview=False, samples=16):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = scene_id
    info = scene_info(scene_id)
    scene.frame_start = 1
    scene.frame_end = info['frame_count']
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 50 if preview else 100
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.render.image_settings.compression = 25
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.use_sequencer = False
    scene.render.use_compositing = False
    scene.render.use_persistent_data = True
    if hasattr(scene.render, 'use_motion_blur'):
        scene.render.use_motion_blur = True
    if hasattr(scene.render, 'motion_blur_shutter'):
        scene.render.motion_blur_shutter = 0.2
    if hasattr(scene, 'eevee'):
        for attr in ('taa_render_samples', 'taa_samples'):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, samples)
                break
    scene.view_settings.view_transform = 'Standard'
    try:
        scene.view_settings.look = 'None'
    except TypeError:
        pass
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    world = bpy.data.worlds.new('pdoom_ink_world')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = rgba('ink')
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25
    scene.world = world
    scene['scene_id'] = scene_id
    scene['global_start_frame'] = info['start_frame']
    scene['global_end_frame'] = info['end_frame']
    scene['source_start_seconds'] = info['start']
    scene['source_end_seconds'] = info['end']
    scene['reference_commit'] = 'fa164b74fd0b26a99375715b619c55b4a0fb3d05'
    scene['render_palette'] = 'ink/bone/signal; Standard sRGB; BT.709 encode'
    return scene


def save_scene(scene, path=None):
    path = Path(path or ROOT / 'src' / 'scenes' / f"{scene['scene_id']}.blend")
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    print(f'SAVED {path}', flush=True)
    return path


def background_plane(name='background', color='ink', z=-5.0, strength=1.0):
    from .geometry import plane
    from .palette import flat_material
    return plane(name, (0,0,z), (30,20), flat_material(f'{name}_mat', color, strength))


def set_linear_animation(obj):
    """Best-effort linear interpolation across both legacy and layered Actions."""
    ad = getattr(obj, 'animation_data', None)
    action = getattr(ad, 'action', None) if ad else None
    if not action:
        return
    try:
        for curve in action.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = 'LINEAR'
    except AttributeError:
        pass


def add_area_light(name, location, energy=500, color=(1,1,1), size=5, target=(0,0,0)):
    from .cameras import point_at
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.color = color
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    point_at(obj, target)
    return obj
