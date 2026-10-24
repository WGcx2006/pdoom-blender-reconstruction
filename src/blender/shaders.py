"""Procedural paper, engraved metal and screen-like materials."""
from __future__ import annotations
from .palette import rgba


def engraved_material(name, base='ink2', line='bone', scale=150.0, metallic=0.25):
    import bpy
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = 0.42
    tex = nodes.new('ShaderNodeTexCoord')
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value = scale
    wave.inputs['Distortion'].default_value = 2.2
    wave.inputs['Detail'].default_value = 2.0
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = rgba(base)
    ramp.color_ramp.elements[1].position = 0.56
    ramp.color_ramp.elements[1].color = rgba(line)
    links.new(tex.outputs['Generated'],wave.inputs['Vector'])
    links.new(wave.outputs['Color'],ramp.inputs[0])
    links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
    links.new(ramp.outputs['Color'],bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 0.35
    links.new(bsdf.outputs[0],out.inputs[0])
    return mat


def paper_material(name='paper', color='bone'):
    import bpy
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = rgba(color)
    bsdf.inputs['Roughness'].default_value = 0.85
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 180
    noise.inputs['Roughness'].default_value = 0.7
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.025
    links.new(noise.outputs['Fac'],bump.inputs['Height'])
    links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    return mat
