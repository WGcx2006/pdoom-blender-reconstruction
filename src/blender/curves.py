"""Deterministic vector-like curves for diagrams, hatching and spark trails."""
from __future__ import annotations
import math
import bpy
from .palette import flat_material, assign


def polyline(name, points, color='bone', width=0.012, cyclic=False, material=None, z=0.0):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 1
    data.bevel_depth = width
    data.bevel_resolution = 1
    spline = data.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        x, y = co[:2]
        pz = co[2] if len(co) > 2 else z
        point.co = (x, y, pz, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    assign(obj, material or flat_material(f'{name}_mat', color))
    return obj


def bezier(name, points, color='bone', width=0.012, cyclic=False, material=None):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 16
    data.bevel_depth = width
    data.bevel_resolution = 2
    spline = data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    assign(obj, material or flat_material(f'{name}_mat', color))
    return obj


def circle(name, center, radius, color='bone', width=0.012, segments=96, material=None):
    x, y, z = center
    points = [(x + radius * math.cos(i * math.tau / segments),
               y + radius * math.sin(i * math.tau / segments), z) for i in range(segments)]
    return polyline(name, points, color, width, True, material)


def rectangle(name, x0, y0, x1, y1, color='bone', width=0.012, z=0.0, material=None):
    return polyline(name, [(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)], color, width, True, material)


def grid(name, x0=-9.6, x1=9.6, y0=-5.4, y1=5.4, step=0.5,
         color='graphite', width=0.003, z=-0.2):
    objects = []
    count_x = int(round((x1 - x0) / step))
    count_y = int(round((y1 - y0) / step))
    for i in range(count_x + 1):
        x = x0 + i * step
        objects.append(polyline(f'{name}_x{i}', [(x,y0,z),(x,y1,z)], color, width))
    for i in range(count_y + 1):
        y = y0 + i * step
        objects.append(polyline(f'{name}_y{i}', [(x0,y,z),(x1,y,z)], color, width))
    return objects


def animate_draw(obj, frame_start, frame_end, start=0.0, end=1.0):
    obj.data.bevel_factor_end = start
    obj.data.keyframe_insert('bevel_factor_end', frame=frame_start)
    obj.data.bevel_factor_end = end
    obj.data.keyframe_insert('bevel_factor_end', frame=frame_end)


def dashed_line(name, start, end, dash=0.15, gap=0.10, color='ash', width=0.008, z=0.0):
    x0,y0 = start
    x1,y1 = end
    length = math.hypot(x1-x0,y1-y0)
    objects = []
    if length == 0:
        return objects
    ux,uy = (x1-x0)/length,(y1-y0)/length
    pos = 0.0
    index = 0
    while pos < length:
        stop = min(length,pos+dash)
        objects.append(polyline(f'{name}_{index}', [(x0+ux*pos,y0+uy*pos,z),(x0+ux*stop,y0+uy*stop,z)], color,width))
        pos += dash+gap
        index += 1
    return objects
