"""Reusable native Blender geometry; no reference-image planes are used."""
from __future__ import annotations
import math
import bpy
from mathutils import Vector
from .palette import flat_material, principled_material, assign
from .curves import polyline, bezier


def mesh_object(name, vertices, faces, material=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, material)
    return obj


def plane(name, location=(0,0,0), size=(2,2), material=None):
    sx,sy = size[0]/2,size[1]/2
    vertices = [(-sx,-sy,0),(sx,-sy,0),(sx,sy,0),(-sx,sy,0)]
    obj = mesh_object(name, vertices, [(0,1,2,3)], material or flat_material(f'{name}_mat','ink2'))
    obj.location = location
    return obj


def cube(name, location=(0,0,0), scale=(1,1,1), material=None, bevel=0.0):
    sx,sy,sz = [v/2 for v in scale]
    vertices = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
                (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    obj = mesh_object(name, vertices, faces, material or principled_material(f'{name}_mat','ink2'))
    obj.location = location
    if bevel > 0:
        mod = obj.modifiers.new('soft_edges','BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj


def uv_sphere(name, location=(0,0,0), radius=1.0, scale=(1,1,1), material=None, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign(obj, material or principled_material(f'{name}_mat','bone'))
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def cylinder(name, location=(0,0,0), radius=1.0, depth=0.2, material=None, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material or principled_material(f'{name}_mat','bone'))
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def torus(name, location=(0,0,0), major_radius=1.0, minor_radius=0.1, material=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius,
                                    major_segments=64, minor_segments=10, location=location)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material or principled_material(f'{name}_mat','bone'))
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def paperclip(name, location=(0,0,0), scale=1.0, color='bone', width=0.045, material=None):
    points = [(-0.38,-0.92,0),(-0.62,-0.66,0),(-0.62,0.60,0),(-0.42,0.94,0),
              (0.10,1.08,0),(0.52,0.82,0),(0.60,0.36,0),(0.60,-0.72,0),
              (0.35,-1.10,0),(-0.10,-1.14,0),(-0.35,-0.86,0),(-0.35,0.47,0),
              (-0.16,0.68,0),(0.12,0.64,0),(0.23,0.40,0),(0.23,-0.55,0)]
    obj = bezier(name, [(x*scale,y*scale,0) for x,y,_ in points], color, width*scale, material=material)
    obj.location = location
    return obj


def spark(name, location=(0,0,0), radius=0.055, trail=((0,0,0),(0.8,0.25,0))):
    material = flat_material(f'{name}_glow','signal',3.0)
    core = uv_sphere(f'{name}_core', location, radius, material=material, segments=16, rings=8)
    points = [(location[0]+p[0],location[1]+p[1],location[2]+p[2]) for p in trail]
    line = polyline(f'{name}_trail', points, 'signal', radius*0.45, material=material)
    return core,line


def linked_copy(obj, name, location=None, scale=None, rotation=None):
    new = obj.copy()
    new.data = obj.data
    new.name = name
    bpy.context.collection.objects.link(new)
    if location is not None:
        new.location = location
    if scale is not None:
        new.scale = scale
    if rotation is not None:
        new.rotation_euler = rotation
    return new


def tube_mesh(name, points, radii, material=None, sides=12):
    vertices = []
    faces = []
    pts = [Vector(p) for p in points]
    for i,p in enumerate(pts):
        tangent = (pts[min(i+1,len(pts)-1)] - pts[max(i-1,0)]).normalized()
        reference = Vector((0,0,1)) if abs(tangent.z) < 0.9 else Vector((0,1,0))
        normal = tangent.cross(reference).normalized()
        binormal = tangent.cross(normal).normalized()
        radius = radii[i] if isinstance(radii,(list,tuple)) else radii
        for j in range(sides):
            angle = j*math.tau/sides
            co = p + radius*(math.cos(angle)*normal + math.sin(angle)*binormal)
            vertices.append(tuple(co))
    for i in range(len(pts)-1):
        for j in range(sides):
            a = i*sides+j
            b = i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(range(sides-1,-1,-1)))
    faces.append(tuple((len(pts)-1)*sides+j for j in range(sides)))
    obj = mesh_object(name,vertices,faces,material or principled_material(f'{name}_mat','bone',0.15,0.38))
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj
