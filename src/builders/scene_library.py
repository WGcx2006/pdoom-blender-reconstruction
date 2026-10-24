"""Procedural scene builders for the pdoom Blender reconstruction."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blender.common import setup_scene, save_scene, background_plane, time_to_local, local_to_time, add_area_light
from blender.cameras import ortho_camera, perspective_camera, key_camera
from blender.curves import polyline, bezier, circle, rectangle, grid, animate_draw
from blender.typography import text, label
from blender.geometry import cube, plane, uv_sphere, torus, tube_mesh, paperclip, cylinder
from blender.palette import flat_material, principled_material
from blender.shaders import engraved_material
from blender.sdf import eye
from blender.charts import crop_marks

ROOT = Path(__file__).resolve().parents[1]
W = 9.6
H = 5.4


def vis(obj, start=1, end=None):
    obj.hide_render = True
    obj.keyframe_insert('hide_render', frame=max(0, start-1))
    obj.hide_render = False
    obj.keyframe_insert('hide_render', frame=start)
    if end is not None:
        obj.hide_render = True
        obj.keyframe_insert('hide_render', frame=end+1)
    return obj


def moving(obj, frame, location=None, scale=None, rotation=None):
    if location is not None: obj.location = location; obj.keyframe_insert('location', frame=frame)
    if scale is not None: obj.scale = scale; obj.keyframe_insert('scale', frame=frame)
    if rotation is not None: obj.rotation_euler = rotation; obj.keyframe_insert('rotation_euler', frame=frame)


def text_obj(body, x, y, size=0.5, color='bone', font='archivo', align='LEFT', z=0.1):
    return text(body, body, x, y, size, color, font, align=align, z=z)


def line(points, color='bone', width=0.015, z=0.0):
    return polyline('vector', [(p[0],p[1],p[2] if len(p)>2 else z) for p in points], color, width)


def quad(name, x, y, w, h, color='ink2', z=0.0, strength=1.0):
    return plane(name, (x,y,z), (w,h), flat_material(name+'_mat', color, strength))


def build_scene(scene_id):
    scene = setup_scene(scene_id, preview=False, samples=16)
    build_simple(scene_id)
    animate_scene(scene_id)
    return scene


def build_simple(scene_id):
    background_plane()
    cam = ortho_camera()
    title = scene_id.upper()
    label('scene_tag', title, -9.1, 5.05, 0.18, 'ash')
    label('time_tag', 'P(DOOM) / LOCAL TIMELINE', 9.1, 5.05, 0.16, 'ash', 'RIGHT')
    if scene_id == 'open': build_open()
    elif scene_id == 'loss': build_loss()
    elif scene_id.startswith('prompt'): build_prompt(scene_id)
    elif scene_id.startswith('hook'): build_hook(scene_id)
    elif scene_id == 'room': build_room()
    elif scene_id == 'shoggoth': build_shoggoth()
    elif scene_id == 'spacetime': build_spacetime()
    elif scene_id == 'ascent': build_ascent()
    elif scene_id == 'bureau': build_bureau()
    elif scene_id == 'leftturn': build_leftturn()
    elif scene_id == 'paperclips': build_paperclips()
    elif scene_id == 'fuse': build_fuse()
    elif scene_id == 'stack': build_stack()
    elif scene_id == 'dense': build_dense()
    elif scene_id == 'loom': build_loom()
    elif scene_id == 'outro': build_outro()


def build_open():
    grid('paper_grid', -9, 9, -4.5, 4.5, 0.55, 'graphite', 0.004, -0.2)
    text_obj('TikZ / construction sheet', -8.6, 4.45, 0.30, 'bone', 'mono')
    text_obj('AGI', -2.0, 1.9, 2.0, 'signal', 'archivo_black', 'CENTER')
    text_obj('surprisal  −log p', -8.2, -3.8, 0.30, 'ash', 'mono')
    text_obj('0.00 nats', 7.9, -4.2, 0.35, 'signal', 'mono', 'RIGHT')
    for i in range(4):
        x = -6.8 + i*4.2
        line([(x,-2.8,0),(x,2.4,0)], 'ash', 0.008)
    circle('axis_circle', (-2.8,0.3,0), 2.0, 'bone', 0.018)
    for i in range(8):
        a = i*math.tau/8
        line([(0,0,0),(6.8*math.cos(a),3.5*math.sin(a),0)], 'graphite', 0.006)
    path = [(-8,-2),(-5,-1),(-3,1),(0,0.4),(2,2),(5,1.2),(8,3.4)]
    line(path, 'signal', 0.045)
    for i in range(len(path)-1):
        animate_draw(line([path[i],path[i+1]], 'signal', 0.025), i*18+1, i*18+22)
    text_obj('AGI', 4.7, 3.2, 0.85, 'bone', 'archivo_black', 'CENTER')
    # Match the reference loop: the first instant is a dark sheet with four crop marks.
    cover = quad('opening_black_cover', 0, 0, 19.2, 10.8, 'ink', 10.0, 1.0)
    vis(cover, 1, 30)
    for frame, factor in [(1,1.0),(24,1.0),(30,0.001)]:
        moving(cover, frame, scale=(factor,factor,factor))
    for obj in crop_marks('bone'):
        obj.location.z = 11.0
        vis(obj, 1, 30)


def build_loss():
    grid('loss_grid', -8, 8, -3.5, 3.5, 1.0, 'ink2', 0.006, -0.1)
    text_obj('LOSS / STEP', -8.4, 4.55, 0.32, 'ash', 'mono')
    points = []
    for i in range(41):
        x = -7.7 + i*0.38
        y = 2.7 - 4.8*(1-math.exp(-i/8)) + 0.22*math.sin(i*2.3)
        points.append((x,y))
    line(points, 'signal', 0.035)
    for i in range(8):
        y = -3.0 + i*0.75
        line([(-7.7,y),(7.7,y)], 'graphite', 0.004)
    text_obj('servant', -7.5, 2.9, 0.34, 'bone', 'mono')
    text_obj('boss', 5.0, -2.4, 0.62, 'signal', 'archivo_black')
    text_obj('→ minimum', 5.2, -3.1, 0.27, 'ash', 'mono')


def build_prompt(scene_id):
    label('prompt_header', 'PROMPT / TOKEN STREAM', -8.7, 4.6, 0.20, 'ash')
    prompt = {'prompt1':'ChatGPT, please', 'prompt2':'Sydney', 'prompt3':'Gato'}[scene_id]
    text_obj(prompt, -7.8, 2.8, 0.65, 'bone', 'mono')
    for i in range(9):
        x = -6.8 + (i%3)*4.4
        y = 0.9 - (i//3)*1.1
        width = 1.4 + (i%4)*0.35
        quad('token_bar', x, y, width, 0.12, 'signal' if i%3==0 else 'graphite', 0.0)
        label('token_label', f'{0.02+i*0.013:.3f}', x+width/2, y-0.18, 0.13, 'ash', 'CENTER')
    text_obj('∴  generative path', -7.6, -3.6, 0.30, 'signal', 'serif_italic')


def build_hook(scene_id):
    n = int(scene_id[-1])
    bg = 'signal' if n == 2 else 'ink'
    quad('hook_bg', 0, 0, 19.2, 10.8, bg, -1.0, 0.8 if n==2 else 0.2)
    text_obj("I'M", -7.5, 3.1, 1.0, 'bone' if n!=2 else 'ink', 'archivo_black')
    text_obj('UPPING', -7.5, 1.3, 1.6, 'bone' if n!=2 else 'ink', 'archivo_black')
    text_obj('MY', -7.5, -0.2, 1.0, 'bone' if n!=2 else 'ink', 'archivo_black')
    text_obj('P(DOOM)', -7.5, -2.4, 1.25, 'signal' if n!=2 else 'ink', 'archivo_black')
    text_obj(['0.15','0.42','0.81','0.99'][n-1], 5.4, 0.0, 1.35, 'bone' if n!=2 else 'ink', 'mono', 'CENTER')
    for i in range(n*3):
        x = 3.2 + i*0.6
        line([(x,-3.6),(x+0.9,3.8)], 'signal' if n!=2 else 'blood', 0.012)


def build_room():
    for i in range(7):
        x = -8.4 + i*2.8
        cube('library_shelf', (x,0,1.0), (2.1,0.35,6.4), principled_material('shelf','ink2',0.1,0.7))
        for j in range(5):
            cube('book', (x-0.6+(j%3)*0.5,-0.25,-1.2+(j//3)*2.0), (0.28,0.20,1.4), flat_material('book','ash',0.35))
    text_obj('FOOM', 0, 3.3, 1.8, 'signal', 'archivo_black', 'CENTER')
    text_obj('我不懂', -3.2, -2.6, 0.7, 'bone', 'serif', 'CENTER')
    for i in range(12):
        a = i*math.tau/12
        line([(0,0,0),(4.5*math.cos(a),2.5*math.sin(a),0)], 'acid', 0.025)


def build_shoggoth_legacy():
    # Dense, radial tube knots preserve the original engraved-monster silhouette.
    for i in range(15):
        a = i*math.tau/15
        pts = []
        for j in range(24):
            u = j/23
            r = 0.4 + 3.4*u
            ang = a + 0.8*math.sin(u*math.pi) + 0.12*u
            pts.append((r*math.cos(ang), 1.3*r*math.sin(ang), 0.35*math.sin(u*math.pi)))
        tube_mesh('shoggoth_tentacle', pts, [0.20*(1-u*0.72) for u in [j/23 for j in range(24)]], engraved_material('engraved_ink','ink2','bone',110,0.18), 10)
    for i in range(9):
        a = i*math.tau/9
        eye('shoggoth_eye', (2.8*math.cos(a), 1.5*math.sin(a), 0.6), 0.22+0.04*(i%3))
    text_obj('SHOGGOTH / X-RAY', -8.8, 4.7, 0.24, 'ash', 'mono')
    text_obj('EXPIRED', 5.2, -3.9, 0.36, 'signal', 'mono')
    for i in range(6):
        y = -2.6 + i*0.78
        line([(3.5,y),(7.9,y)], 'ash', 0.008)
        label('life_label', f'{i+1:02d}  LIFESPAN  {99-i*13}y', 5.3, y+0.13, 0.16, 'ash')
    line([(-8,-4.0),(8,-4.0)], 'signal', 0.035)


def build_shoggoth():
    scene = bpy.context.scene
    info = {'start_frame': scene['global_start_frame']}
    F = lambda seconds: time_to_local(info, seconds)
    before = set(scene.objects)
    for i in range(15):
        a = i*math.tau/15
        pts = []
        for j in range(24):
            u = j/23
            r = 0.4 + 3.4*u
            ang = a + 0.8*math.sin(u*math.pi) + 0.12*u
            pts.append((r*math.cos(ang), 1.3*r*math.sin(ang), 0.35*math.sin(u*math.pi)))
        tube_mesh('shoggoth_tentacle', pts, [0.20*(1-j/23*0.72) for j in range(24)], engraved_material('engraved_ink','ink2','bone',110,0.18), 10)
    for i in range(9):
        a = i*math.tau/9
        eye('shoggoth_eye', (2.8*math.cos(a), 1.5*math.sin(a), 0.6), 0.22+0.04*(i%3))
    creature = [obj for obj in scene.objects if obj not in before]
    for obj in creature:
        vis(obj, F(30.65), F(37.95))
    # The deliberately bland assistant mask is the opening shot.
    mask_mat = flat_material('mask_bone', 'bone', 0.72)
    mask = cylinder('assistant_smile_mask', (0,0,1.8), 2.45, 0.10, mask_mat, 64)
    for x in (-0.72,0.72):
        cylinder('mask_dot', (x,0.55,1.88), 0.15, 0.04, flat_material('mask_ink','ink'), 24)
    smile = bezier('mask_smile', [(-0.85,-0.45,1.90),(0,-1.05,1.90),(0.85,-0.45,1.90)], 'ink', 0.07)
    mask_parts = [mask, smile] + [o for o in scene.objects if o.name.startswith('mask_dot')]
    for obj in mask_parts:
        vis(obj, 1, F(35.0))
    mask_root = bpy.data.objects.new('mask_reframe_root', None)
    bpy.context.collection.objects.link(mask_root)
    for obj in mask_parts:
        obj.parent = mask_root
    for frame, offset, factor in [(1,(0,0,0),1.0),(F(31.0),(0,0,0),1.0),(F(34.0),(3.5,2.0,0),0.43),(F(35.0),(3.8,2.2,0),0.40)]:
        moving(mask_root, frame, location=offset, scale=(factor,factor,factor))
    scan = line([(-4.8,-4.8,2.0),(-4.8,4.8,2.0)], 'signal', 0.025)
    for frame in range(1, F(31.3)+1, 2):
        u = frame/max(1,F(31.3))
        moving(scan, frame, location=(u*9.6,0,0))
    vis(scan, F(29.95), F(31.2))
    text_obj('SHOGGOTH / X-RAY', -8.8, 4.7, 0.24, 'ash', 'mono')
    expired = text_obj('EXPIRED', 5.2, -3.9, 0.36, 'signal', 'mono')
    vis(expired, F(36.5), F(38.1))
    for i in range(6):
        y = -2.6 + i*0.78
        leader = line([(3.5,y),(7.9,y)], 'ash', 0.008)
        tag = label('life_label', f'{i+1:02d}  LIFESPAN  {99-i*13}y', 5.3, y+0.13, 0.16, 'ash')
        vis(leader, F(32.2), F(37.6)); vis(tag, F(32.2), F(37.6))
    flat = line([(-8,-4.0),(8,-4.0)], 'signal', 0.035)
    vis(flat, F(37.7), F(38.4))


def build_spacetime():
    circle('singularity', (0,0,0), 2.2, 'bone', 0.04)
    circle('photon_ring', (0,0,0), 1.55, 'signal', 0.06)
    circle('event_horizon', (0,0,0), 1.05, 'ink2', 0.10)
    for i in range(16):
        a = i*math.tau/16
        line([(0,0),(5.7*math.cos(a),3.8*math.sin(a))], 'ash', 0.008)
    text_obj('SINGULARITY’S', -4.0, 3.5, 0.55, 'bone', 'serif_italic')
    text_obj('BEGUN', 2.6, -3.2, 0.75, 'signal', 'archivo_black')
    for i in range(10):
        line([(-8+i*1.6,-4.0),(-7.5+i*1.6,4.0)], 'graphite', 0.005)


def build_ascent():
    text_obj(' basilisk / market cap ', -8.7, 4.6, 0.24, 'ash', 'mono')
    for i in range(18):
        x = -8.0 + i*0.85
        h = 0.5 + (i/18)*3.8
        line([(x,-2.8),(x,h-1.0)], 'signal' if i%3 else 'bone', 0.035)
        line([(x-0.20,h-1.0),(x+0.20,h-1.0)], 'bone', 0.018)
    circle('guilloche', (4.2,1.3,0), 2.0, 'bone', 0.018)
    for r in (1.6,1.25,0.8): circle('guilloche_ring', (4.2,1.3,0), r, 'ash', 0.012)
    text_obj('1e30 FLOP/s', 4.1, -3.5, 0.43, 'signal', 'mono', 'CENTER')


def build_bureau():
    quad('paper', 0, 0, 15.6, 9.0, 'bone', -0.2, 0.7)
    text_obj('FORM 7-B / SAFETY ASSESSMENT', -7.0, 3.9, 0.32, 'ink', 'mono')
    for i in range(6):
        y = 2.8-i*0.9
        rectangle('checkbox', -7.0,y-0.20,-6.65,y+0.15,'ink',0.012)
        label('field', ['MODEL','DATA','ALIGNMENT','DEPLOY','REVIEW','APPROVE'][i], -6.2,y,0.22,'ink')
        line([(-2.0,y),(6.9,y)], 'ash', 0.010)
    text_obj('SAFE ENOUGH', 1.6, -0.4, 0.85, 'signal', 'archivo_black', 'CENTER')
    text_obj('MLP  →  CPU  →  MEMORY  →  I/O', -6.8, -3.8, 0.25, 'ink', 'mono')


def build_leftturn():
    grid('roadmap_grid', -8, 8, -4, 4, 1, 'ash', 0.004, -0.2)
    line([(-8,-2),(-3,-2),(-3,2),(2,2),(2,-1),(7,-1)], 'signal', 0.045)
    for i,word in enumerate(['SRR','PDR','CDR','TRR','LAUNCH']):
        x = -7.5+i*3.5
        text_obj(word, x, 3.4, 0.25, 'bone', 'mono')
        line([(x,-3.5),(x,3.0)], 'graphite', 0.005)
    circle('mask_eye_l', (-2,0,0), 0.85, 'bone', 0.035)
    circle('mask_eye_r', (2,0,0), 0.85, 'bone', 0.035)
    line([(-2,-2),(0,-2.5),(2,-2)], 'bone', 0.035)
    text_obj('UNPLANNED OBJECT', 0, -4.2, 0.36, 'signal', 'mono', 'CENTER')


def build_paperclips_legacy():
    for i in range(13):
        for j in range(7):
            x = -8.4 + i*1.4 + (j%2)*0.5
            y = -4.2 + j*1.35
            scale = 0.32 + 0.06*((i+j)%3)
            paperclip('clip', (x,y,0.1), scale, 'bone', 0.045)
    text_obj('PAPERCLIPS', -8.8, 4.7, 0.32, 'ash', 'mono')
    text_obj('OUT OF OFFICE', -3.3, 3.0, 0.55, 'bone', 'mono', 'CENTER')
    text_obj('KILLSWITCH: UNAVAILABLE', 0, -3.5, 0.28, 'signal', 'mono', 'CENTER')


def build_paperclips():
    scene = bpy.context.scene
    info = {'start_frame': scene['global_start_frame']}
    F = lambda seconds: time_to_local(info, seconds)
    positions = [(-8.4+i*1.4+(j%2)*0.5, -4.2+j*1.35) for j in range(7) for i in range(13)]
    # The first stroke is drawn before the lattice is allowed to multiply.
    first = paperclip('first_clip', (-0.6,0.0,0.3), 1.85, 'signal', 0.070)
    animate_draw(first, 1, F(97.15), 0.20, 1.0)
    vis(first, 1, F(98.0))
    spark_line = line([(-8.8,-2.5,0.2),(-5.5,-1.8,0.2),(-2.4,-0.6,0.2),(0.2,0.5,0.2)], 'signal', 0.055)
    vis(spark_line, 1, F(97.0))
    birth_times = [97.05,97.45,97.85,98.25,98.65,99.05,99.45]
    counts = [1,2,4,8,16,32,64]
    for index,(x,y) in enumerate(positions[1:]):
        group = min(6, int(math.log2(index+1)))
        obj = paperclip('lattice_clip', (x,y,0.1), 0.32+0.06*((index+1)%3), 'bone', 0.045)
        vis(obj, F(birth_times[group]), None)
    pto = text_obj('OUT OF OFFICE', -3.3, 3.0, 0.55, 'bone', 'mono', 'CENTER')
    kill = text_obj('KILLSWITCH: UNAVAILABLE', 0, -3.5, 0.28, 'signal', 'mono', 'CENTER')
    vis(pto, F(99.0), F(101.15)); vis(kill, F(99.0), F(101.15))
    final_lyric = text_obj("NOW THERE'S NOWHERE LEFT TO GO", 0, -0.10, 1.10, 'bone', 'archivo_black', 'CENTER')
    vis(final_lyric, F(101.15), None)
    opening_lyric = text_obj('as paperclips fill the room', -8.0, 4.0, 0.34, 'ash', 'archivo')
    vis(opening_lyric, 1, F(98.4))
    final_rule = line([(-9.0,-0.75,0.1),(9.0,-0.75,0.1)], 'signal', 0.025)
    vis(final_rule, F(101.15), None)
    text_obj('PAPERCLIPS', -8.8, 4.7, 0.32, 'ash', 'mono')


def build_fuse():
    text_obj('ORTHOGONALITY / INSTRUMENTAL', -8.7, 4.5, 0.28, 'ash', 'mono')
    line([(-8,-2),(-5,-1),(-2,1),(1,1.8),(4,1.2),(8,3.5)], 'signal', 0.06)
    for i in range(9):
        x = -7+i*1.8
        line([(x,-2.8),(x+0.4,2.6)], 'ash', 0.008)
    text_obj('INTELLIGENCE →  × GOALS ↑', -7.6, -3.8, 0.34, 'bone', 'mono')
    text_obj('♭', 6.9, 3.5, 0.8, 'signal', 'serif')


def build_stack():
    for i in range(9):
        y = -4.4+i*1.1
        rectangle('transformer_block', -5.6,y-0.35,5.6,y+0.35,'ash',0.012)
        text_obj('attention   add & norm   feed-forward', -5.0,y+0.10,0.22,'bone','mono')
    text_obj('DISOBEY', -3.5, 4.0, 0.72, 'signal', 'archivo_black')


def build_dense():
    for i in range(20):
        x = -9.0+i*0.92
        for j in range(8):
            y = -3.7+j*1.0
            text_obj('GPU', x,y,0.19,'ash','mono')
    rectangle('safe_box', -8.6,-4.3,8.6,4.3,'signal',0.016)
    text_obj('100,000 GPU', -4.4, 4.6, 0.52, 'signal', 'mono')
    text_obj('REWARD MODEL  0.99 → 0.41 → 0.99', -7.3, -4.8, 0.25, 'bone', 'mono')


def build_loom():
    text_obj('TREE OF CONTINUATIONS', -8.7, 4.65, 0.25, 'ash', 'mono')
    root = (-7.4, -2.8)
    line([root,(-3.8,-1.0),(-0.5,1.2),(3.2,2.5),(7.2,3.2)], 'signal', 0.035)
    branches = [((-3.8,-1.0),(-4.8,2.8),'0.18  Moloch'),((-0.5,1.2),(-1.4,4.0),'0.31  Loom'),((3.2,2.5),(4.4,4.1),'0.09  eval suite'),((3.2,2.5),(7.0,0.2),'0.22  nobody, technically'),((-3.8,-1.0),(0.0,-3.7),'0.14  Substack post')]
    for i,(a,b,word) in enumerate(branches):
        line([a,b], 'ash', 0.018)
        circle('token_node', (b[0],b[1],0), 0.12, 'bone', 0.015, 24)
        label('candidate', word, b[0]+0.22,b[1]+0.10,0.20,'ash')
    text_obj('Loom', 3.0, 2.85, 0.72, 'bone', 'serif_italic')
    text_obj('p 0.31  ▸ SAMPLED', 3.0, 2.25, 0.22, 'signal', 'mono')
    mask = quad('mask_block', -1.7, -2.1, 2.4, 0.60, 'bone', 0.1, 0.8)
    text_obj('[ MASK ]', -2.65, -1.95, 0.32, 'ink', 'mono_bold')
    for i in range(5):
        rectangle('droste_frame', -7.8+i*0.55,-4.2+i*0.35,7.8-i*0.55,4.2-i*0.35,'graphite',0.008)


def build_outro():
    initial = text_obj('1.00', -1.7, 0.85, 2.0, 'bone', 'mono')
    title = text_obj('P(DOOM) = ∞', -5.5, 2.4, 1.8, 'bone', 'serif_italic')
    numbers = text_obj('1e9   1e30   1e100   1e1000', -6.2, 0.3, 0.34, 'signal', 'mono')
    nan = text_obj('NaN¹', -1.0, -1.0, 2.2, 'bone', 'serif_italic')
    foot = text_obj('estimate no longer defined', -3.2, -3.0, 0.25, 'ash', 'mono')
    regen = text_obj('↻  REGENERATE', -2.0, -4.4, 0.36, 'signal', 'mono')
    # The end card is a sequence, not a pile of simultaneous captions.
    vis(initial, 1, 180)
    vis(title, 180, 260)
    vis(numbers, 180, 300)
    vis(nan, 250, 520)
    vis(foot, 300, 560)
    vis(regen, 560, bpy.context.scene.frame_end - 1)
    for frame, scale in [(1,0.7),(80,1.0),(180,1.15),(260,0.8),(520,1.0)]:
        moving(title, frame, scale=(scale,scale,scale))
    for frame, angle in [(250,0),(320,math.pi/2),(420,math.pi),(520,math.tau)]:
        moving(nan, frame, rotation=(0,0,angle))
    # The opening explosion is native line geometry, not a reference-image plate.
    burst = []
    for i in range(64):
        a = i*math.tau/64
        r0 = 0.2 + 0.15*(i%3)
        r1 = 4.0 + 1.8*((i*17)%7)/7
        burst.append(line([(r0*math.cos(a),r0*math.sin(a),0.3),(r1*math.cos(a),r1*math.sin(a),0.3)], 'ember' if i%3 else 'bone', 0.012))
    core = uv_sphere('outro_explosion_core',(0,0,0.4),0.42,material=flat_material('outro_core','ember',4.0),segments=24,rings=12)
    for obj in burst+[core]:
        vis(obj,1,95)
    # The same four crop marks used by the opening return for the seamless loop.
    for obj in crop_marks('bone'):
        obj.location.z = 0.2
        vis(obj, 560, 9399)
    for obj in list(bpy.context.scene.objects):
        if obj.name in ('scene_tag','time_tag'):
            obj.hide_render = True
            obj.keyframe_insert('hide_render', frame=bpy.context.scene.frame_end)


def animate_scene(scene_id):
    scene = bpy.context.scene
    cam = scene.camera
    end = scene.frame_end
    for frame in range(1, end + 1, 4):
        u = (frame - 1) / max(1, end - 1)
        if scene_id == 'paperclips':
            loc = (0.9*math.sin(u*math.pi*1.2), 0.5*math.cos(u*math.pi), 20.0 - 7.0*u)
        elif scene_id == 'shoggoth':
            loc = (0.35*math.sin(u*math.pi*2), 0.2*math.cos(u*math.pi), 20.0 - 3.0*math.sin(u*math.pi))
        elif scene_id in ('stack','dense'):
            loc = (0.2*math.sin(u*math.pi), -2.0*u, 20.0)
        elif scene_id.startswith('hook'):
            loc = (0.0, 0.0, 20.0 - 1.2*math.sin(u*math.pi))
        else:
            loc = (0.22*math.sin(u*math.pi*1.4), 0.15*math.cos(u*math.pi), 20.0)
        moving(cam, frame, location=loc)
    if scene_id == 'outro':
        moving(cam, end, location=(0.0,0.15,20.0))
    # Beat-driven pulses on title/type objects, deliberately small to preserve readability.
    for obj in list(scene.objects):
        if obj.type == 'FONT' and (scene_id.startswith('hook') or scene_id in ('outro','stack','dense')):
            for frame in range(1, end + 1, 15):
                pulse = 1.0 + 0.035*math.sin(frame*math.pi/7.5)
                moving(obj, frame, scale=(pulse,pulse,pulse))


def build_all():
    for scene_id in [s['id'] for s in __import__('json').loads((ROOT/'timeline.json').read_text())['scenes']]:
        if scene_id == 'ilya':
            continue
        print('BUILDING', scene_id, flush=True)
        build_scene(scene_id)
        save_scene(bpy.context.scene, ROOT/'scenes'/f'{scene_id}.blend')


if __name__ == '__main__':
    build_all()
