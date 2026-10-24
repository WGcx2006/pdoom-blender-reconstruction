"""Camera conventions: one Blender unit represents 100 reference pixels."""
from __future__ import annotations
import bpy
from mathutils import Vector


def ortho_camera(name='Camera', scale=19.2, location=(0, 0, 20)):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    data.clip_start = 0.01
    data.clip_end = 500
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    bpy.context.scene.camera = obj
    return obj


def perspective_camera(name='Camera', location=(0, -8, 5), target=(0, 0, 0), lens=45):
    data = bpy.data.cameras.new(name)
    data.type = 'PERSP'
    data.lens = lens
    data.clip_start = 0.03
    data.clip_end = 500
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    point_at(obj, target)
    bpy.context.scene.camera = obj
    return obj


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def key_camera(obj, frame, location=None, target=None, lens=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert('location', frame=frame)
    if target is not None:
        point_at(obj, target)
        obj.keyframe_insert('rotation_euler', frame=frame)
    if lens is not None:
        obj.data.lens = lens
        obj.data.keyframe_insert('lens', frame=frame)
