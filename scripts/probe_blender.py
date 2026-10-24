"""Run inside Blender to record available render devices and API capabilities."""
import bpy
import json
from pathlib import Path

scene = bpy.context.scene
engines = []
try:
    engines = [x.identifier for x in scene.render.bl_rna.properties['engine'].enum_items]
except Exception as exc:
    engines = [f'unavailable: {exc}']
info = {
    'version': bpy.app.version_string,
    'engines': engines,
    'has_eevee': hasattr(scene, 'eevee'),
    'eevee_properties': list(scene.eevee.bl_rna.properties.keys()) if hasattr(scene, 'eevee') else [],
    'render_motion_blur': hasattr(scene.render, 'use_motion_blur'),
    'render_motion_blur_shutter': hasattr(scene.render, 'motion_blur_shutter'),
    'scene_use_nodes': hasattr(scene, 'use_nodes'),
    'scene_compositing_node_group': hasattr(scene, 'compositing_node_group'),
    'cycles_devices': [],
}
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for backend in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            info['cycles_devices'].append({'backend': backend, 'devices': [
                {'name': d.name, 'type': d.type} for d in prefs.devices
            ]})
        except Exception as exc:
            info['cycles_devices'].append({'backend': backend, 'error': str(exc)})
except Exception as exc:
    info['cycles_error'] = str(exc)
out = Path(bpy.path.abspath('//')) / 'reference' / 'qa' / 'blender_probe.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(info, indent=2), encoding='utf-8')
print(json.dumps(info, indent=2))
