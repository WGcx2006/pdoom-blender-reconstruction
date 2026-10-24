"""Blender-native organic meshes approximating the original SDF silhouettes."""
from __future__ import annotations
import math
from .geometry import tube_mesh, uv_sphere
from .palette import principled_material, flat_material


def tentacle(name, center=(0,0,0), angle=0.0, length=4.0, radius=0.35,
             curl=1.5, segments=36, material=None, z=0.0):
    points = []
    radii = []
    for i in range(segments):
        u = i/(segments-1)
        a = angle + curl*u*u
        r = 0.35 + length*u
        points.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),z+0.25*math.sin(u*math.tau)))
        radii.append(radius*(1-u*0.82)*(0.9+0.1*math.sin(u*18)))
    return tube_mesh(name,points,radii,material)


def eye(name, location, radius=0.35):
    eyeball = uv_sphere(f'{name}_ball',location,radius,material=principled_material(f'{name}_ball_mat','ink2',0.2,0.2),segments=24,rings=12)
    iris_loc = (location[0],location[1],location[2]+radius*0.88)
    iris = uv_sphere(f'{name}_iris',iris_loc,radius*0.42,scale=(1,1,0.22),material=flat_material(f'{name}_iris_mat','ember',3.2),segments=24,rings=12)
    pupil = uv_sphere(f'{name}_pupil',(iris_loc[0],iris_loc[1],iris_loc[2]+radius*0.1),radius*0.16,scale=(1,1,0.18),material=flat_material(f'{name}_pupil_mat','ink'),segments=20,rings=10)
    return eyeball,iris,pupil
