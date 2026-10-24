"""Original-project fonts and editable Blender typography."""
from __future__ import annotations
from functools import lru_cache
import bpy
from .common import ROOT
from .palette import flat_material, assign

FONT_FILES = {
    'archivo': 'Archivo-w1000-700.ttf',
    'archivo_light': 'Archivo-w1000-300.ttf',
    'archivo_black': 'Archivo-w1000-900.ttf',
    'archivo_narrow': 'Archivo-w620-700.ttf',
    'archivo_wide': 'Archivo-w1250-700.ttf',
    'italic': 'ArchivoItalic-w1000-800.ttf',
    'mono': 'src/IBMPlexMono-Regular.ttf',
    'mono_bold': 'src/IBMPlexMono-Bold.ttf',
    'serif': 'Cormorant-400.ttf',
    'serif_italic': 'CormorantItalic-400.ttf',
}


def font(name='archivo'):
    path = ROOT / 'assets' / 'fonts' / FONT_FILES[name]
    path_string = str(path)
    for existing in bpy.data.fonts:
        if existing.filepath == path_string:
            return existing
    return bpy.data.fonts.load(path_string)


def text(name, body, x=0, y=0, size=0.5, color='bone', font_name='archivo',
         align='LEFT', valign='TOP', z=0.0, tracking=1.0, material=None):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = body
    data.font = font(font_name)
    data.size = size
    data.align_x = align
    data.align_y = valign
    data.space_character = tracking
    data.resolution_u = 6
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = (x,y,z)
    assign(obj, material or flat_material(f'{name}_mat', color))
    return obj


def label(name, body, x, y, size=0.16, color='ash', align='LEFT', z=0.0):
    return text(name, body, x, y, size, color, 'mono', align=align, z=z)


def fit_text(obj, max_width):
    bpy.context.view_layer.update()
    if obj.dimensions.x > max_width and obj.dimensions.x > 0:
        obj.scale.x *= max_width / obj.dimensions.x
    return obj


def reveal_text(obj, frame_start, frame_end):
    obj.hide_render = True
    obj.keyframe_insert('hide_render', frame=frame_start - 1)
    obj.hide_render = False
    obj.keyframe_insert('hide_render', frame=frame_start)
    return obj


def pulse(obj, frame, amount=1.08, length=8):
    base = tuple(obj.scale)
    obj.scale = base
    obj.keyframe_insert('scale', frame=frame - 1)
    obj.scale = tuple(v * amount for v in base)
    obj.keyframe_insert('scale', frame=frame + length // 3)
    obj.scale = base
    obj.keyframe_insert('scale', frame=frame + length)
