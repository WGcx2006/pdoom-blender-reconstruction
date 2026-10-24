"""Shared pdoom palette and materials. Hex inputs are sRGB; shaders use linear RGB."""
from __future__ import annotations
import bpy

HEX = {
    'ink': '#0A0A0B', 'ink2': '#151517', 'graphite': '#5E5B57',
    'ash': '#9C978F', 'bone': '#EEE9DF', 'signal': '#FF4D12',
    'ember': '#FF8A3D', 'blood': '#C21D0B', 'acid': '#D8FF3C',
    'white': '#FFFFFF', 'black': '#000000',
}


def linear_channel(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def rgba(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    value = HEX.get(value, value).lstrip('#')
    rgb = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(linear_channel(c) for c in rgb) + (alpha,)


def flat_material(name: str, color: str = 'bone', strength: float = 1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = rgba(color)
    emission.inputs['Strength'].default_value = strength
    mat.node_tree.links.new(emission.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = rgba(color)
    return mat


def principled_material(name: str, color: str = 'bone', metallic: float = 0.0,
                        roughness: float = 0.45, emission_strength: float = 0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = rgba(color)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Emission Color'].default_value = rgba(color)
    bsdf.inputs['Emission Strength'].default_value = emission_strength
    mat.diffuse_color = rgba(color)
    return mat


def assign(obj, material):
    if material is not None:
        obj.data.materials.append(material)
    return obj
