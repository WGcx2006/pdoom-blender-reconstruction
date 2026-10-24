"""Optional compositor helpers; scenes remain renderable if the 5.x API changes."""


def configure_glare(scene, threshold=1.2, size=7, quality='MEDIUM'):
    import bpy
    try:
        if hasattr(scene,'compositing_node_group'):
            tree = bpy.data.node_groups.new('pdoom_compositor','CompositorNodeTree')
            scene.compositing_node_group = tree
            tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
            output = tree.nodes.new('NodeGroupOutput')
        else:
            scene.use_nodes = True
            tree = scene.node_tree
            tree.nodes.clear()
            output = tree.nodes.new('CompositorNodeComposite')
        layers = tree.nodes.new('CompositorNodeRLayers')
        glare = tree.nodes.new('CompositorNodeGlare')
        if 'Type' in glare.inputs:
            glare.inputs['Type'].default_value = 'Fog Glow'
            glare.inputs['Quality'].default_value = quality.title()
            glare.inputs['Threshold'].default_value = threshold
            glare.inputs['Size'].default_value = min(0.9, size / 18.0)
            glare.inputs['Strength'].default_value = 0.28
        else:
            glare.glare_type = 'FOG_GLOW'
            glare.quality = quality
            if hasattr(glare,'threshold'):
                glare.threshold = threshold
            if hasattr(glare,'size'):
                glare.size = size
        tree.links.new(layers.outputs['Image'],glare.inputs['Image'])
        tree.links.new(glare.outputs['Image'],output.inputs['Image'])
        scene.render.use_compositing = True
        return True
    except Exception as exc:
        print(f'COMPOSITOR_DISABLED {exc}',flush=True)
        scene.render.use_compositing = False
        return False
