"""Ilya: native Blender white-line room, redacted laptop and empty theatre."""
from pathlib import Path
import math
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blender.common import setup_scene, save_scene, time_to_local, local_to_time, add_area_light
from blender.cameras import perspective_camera, key_camera, point_at
from blender.curves import polyline, bezier, circle, rectangle
from blender.typography import text, label
from blender.geometry import cube, plane, uv_sphere, cylinder
from blender.palette import flat_material, principled_material, rgba

ROOT = Path(__file__).resolve().parents[2]
scene = setup_scene('ilya', preview=False, samples=16)
INFO = {'start_frame': scene['global_start_frame']}
F = lambda seconds: time_to_local(INFO, seconds)
INK = flat_material('ilya_ink', 'ink', 0.5)
BLACK = flat_material('ilya_black', 'black', 0.2)
BONE_DIM = flat_material('ilya_engraving_dim', 'bone', 0.06)
BONE_FAINT = flat_material('ilya_engraving_faint', 'bone', 0.025)
BONE_MED = flat_material('ilya_engraving_med', 'bone', 0.18)
STICKER_BONE = flat_material('ilya_sticker_bone', 'bone', 0.38)
STICKER_INK = flat_material('ilya_sticker_ink', 'ink2', 0.35)
SIGNAL_DIM = flat_material('ilya_sticker_signal', 'signal', 0.42)
SIGNAL = flat_material('ilya_signal', 'signal', 2.2)
EMBER = flat_material('ilya_ember', 'ember', 2.8)
METAL = principled_material('ilya_dark_aluminium', 'ink2', 0.30, 0.48)
DESK = flat_material('ilya_desk', 'ink', 0.30)
VELVET = principled_material('ilya_velvet', 'blood', 0.0, 0.94)


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b != a else float(t >= b)


def smooth(v):
    v = clamp(v)
    return v * v * (3.0 - 2.0 * v)


def cubic(v):
    v = clamp(v)
    return 4 * v**3 if v < 0.5 else 1 - (-2 * v + 2)**3 / 2


def mix(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def keyed_visibility(objects, changes):
    for obj in objects:
        for frame, hidden in changes:
            obj.hide_render = hidden
            obj.keyframe_insert('hide_render', frame=frame)


def multi_lines(name, lines, material, width=0.006):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 1
    data.bevel_depth = width
    data.bevel_resolution = 0
    for points in lines:
        spline = data.splines.new('POLY')
        spline.points.add(len(points) - 1)
        for p, co in zip(spline.points, points):
            p.co = (*co, 1.0)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def empty(name, location=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.parent = parent
    return obj


def emission_material(name, color, strength):
    return flat_material(name, color, strength)


def animate_emission(material, keys):
    socket = material.node_tree.nodes.get('Emission').inputs['Strength']
    for frame, value in keys:
        socket.default_value = value
        socket.keyframe_insert('default_value', frame=frame)


def camera_overlay(obj, cam, location):
    obj.parent = cam
    obj.location = location
    return obj


# Exact aligned-word and beat times from the reference data.
WHAT, DID, ILYA, SEE = 132.020, 132.284, 132.524, 132.818
WELL, NEVER, KNOW = 133.380, 133.880, 134.340
SLAM, SLIT, DARK = 132.958, 134.776, 135.231
KNOW_BAR, LED_OFF = 136.594, 137.049
WAS, IT, ALL, FOR, SHOW = 137.380, 137.797, 138.445, 139.149, 140.027
MEET, END = 139.776, 140.230
STAGE_CUT = 137.170
LID_OPEN = math.radians(112)
HINGE = (0.0, -1.05, 0.16)
S0 = (0.0, HINGE[1] + math.cos(LID_OPEN) * 1.075,
      HINGE[2] + math.sin(LID_OPEN) * 1.075)
GAP = (0.0, 1.085, 0.16)
LED = (0.0, 1.118, 0.07)

# Room camera: hold the stickered back, whip around on "Ilya see?", then sink to the LED.
room_cam = perspective_camera('ilya_room_camera', (0, -14, 3.7), S0, lens=50)
room_cam.data.sensor_width = 36
for frame in range(1, F(STAGE_CUT) + 1, 2):
    t = local_to_time(INFO, frame)
    close_k = cubic(prog(t, WELL, SLIT))
    base = mix(S0, GAP, close_k)
    base = mix(base, LED, cubic(prog(t, SLIT + 0.05, DARK)))
    if t < ILYA:
        u = smooth(prog(t, WHAT, ILYA))
        phi = math.pi + 0.05 * smooth(prog(t, WHAT - 0.1, WHAT)) + 0.25 * u
    else:
        phi = math.pi + 0.30 + (math.tau - 0.50 - math.pi - 0.30) * cubic(prog(t, ILYA, SLAM - 0.02))
        phi += 0.04 * smooth(prog(t, SLAM - 0.02, SLAM + 0.35))
        phi += 0.46 * cubic(prog(t, SLAM + 0.35, SLIT))
    r = 13.0 + (7.0 - 13.0) * cubic(prog(t, ILYA, SLAM))
    r += (6.2 - 7.0) * smooth(prog(t, WELL, SLIT))
    r += (3.2 - 6.2) * cubic(prog(t, SLIT, LED_OFF))
    height = 2.6 + (0.45 - 2.6) * cubic(prog(t, ILYA, SLIT))
    height += (0.16 - 0.45) * cubic(prog(t, SLIT, DARK + 0.1))
    pos = (base[0] + r * math.sin(phi), base[1] + r * math.cos(phi), base[2] + height)
    side = smooth(prog(t, 131.595, WHAT + 0.3)) * (1 - smooth(prog(t, SLIT - 0.4, SLIT + 0.1)))
    target = (base[0] - 1.35 * side, base[1], base[2])
    key_camera(room_cam, frame, pos, target, 50)

# Desk and restrained horizontal burin lines.
cube('desk_top', (0, 0, -0.18), (12.4, 6.6, 0.36), DESK, 0.04)
for x in (-5.75, 5.75):
    for y in (-2.85, 2.85):
        cube('desk_leg', (x, y, -3.7), (0.20, 0.20, 7.0), DESK)
lines = []
for i in range(76):
    y = -3.25 + i * 6.5 / 75
    lines.append([(-6.15, y, 0.012), (6.15, y, 0.012)])
multi_lines('desk_engraved_horizontal_burin', lines, BONE_DIM, 0.007)
multi_lines('desk_edge_engraving', [
    [(-6.2, -3.3, 0.02), (6.2, -3.3, 0.02), (6.2, 3.3, 0.02), (-6.2, 3.3, 0.02), (-6.2, -3.3, 0.02)],
    [(-6.2, -3.3, -0.14), (6.2, -3.3, -0.14)],
], BONE_MED, 0.009)

# Laptop base, keyboard and sleep light.
cube('laptop_base', (0, 0, 0.08), (3.10, 2.16, 0.16), METAL, 0.035)
cube('keyboard_well', (0, -0.28, 0.167), (2.70, 1.10, 0.015), BLACK)
key_lines = []
for i in range(13):
    x = -1.25 + i * 2.5 / 12
    key_lines.append([(x, -0.79, 0.181), (x, 0.20, 0.181)])
for i in range(6):
    y = -0.76 + i * 0.18
    key_lines.append([(-1.27, y, 0.181), (1.27, y, 0.181)])
multi_lines('keyboard_hairlines', key_lines, BONE_FAINT, 0.004)
rectangle('trackpad', -0.55, 0.43, 0.55, 0.93, 'graphite', 0.006, z=0.174, material=BONE_FAINT)
led_mat = emission_material('sleep_light_material', 'signal', 3.5)
led = uv_sphere('sleep_light', LED, 0.026, material=led_mat, segments=12, rings=6)
keyed_visibility([led], [(1, True), (F(DARK - 0.08), False), (F(LED_OFF), True)])
animate_emission(led_mat, [(F(DARK - 0.08), 0.2), (F(DARK + 0.05), 4.0),
                          (F(DARK + 0.45), 1.2), (F(KNOW_BAR), 4.0),
                          (F(LED_OFF - 0.12), 0.8), (F(LED_OFF), 0.0)])

# Hinged lid; all screen and sticker geometry is native and follows the hinge.
lid = empty('laptop_lid_hinge', HINGE)
lid.rotation_euler.x = LID_OPEN
for t, angle in [(WELL - 0.02, LID_OPEN), (NEVER, 1.42), (KNOW, 0.80),
                 (SLIT, 0.07), (DARK, 0.035), (DARK + 0.25, 0.0)]:
    lid.rotation_euler.x = angle
    lid.keyframe_insert('rotation_euler', frame=F(t))
body = cube('lid_aluminium', (0, 1.075, 0), (3.10, 2.15, 0.07), METAL, 0.025)
body.parent = lid
hatch = []
for i in range(42):
    y = 0.035 + i * 2.08 / 41
    hatch.append([(-1.50, y, 0.039), (1.50, y, 0.039)])
lid_hatch = multi_lines('lid_white_line_engraving', hatch, BONE_FAINT, 0.005)
lid_hatch.parent = lid

# Front screen: abstract glare and unreadable chart, then the downbeat REDACTED bar.
screen_mat = emission_material('screen_warm_glare', 'bone', 0.82)
screen = plane('screen_glare', (0, 1.075, -0.041), (2.96, 1.665), screen_mat)
screen.parent = lid
animate_emission(screen_mat, [(1, 0.82), (F(DARK), 0.82), (F(DARK + 0.03), 0.0)])
content_mat = flat_material('screen_unreadable_marks', 'ash', 0.24)
content = []
for i in range(5):
    y = 0.72 + i * 0.10
    content.append([(-1.05, y, -0.047), (-0.45 + (i % 3) * 0.13, y, -0.047)])
chart = []
for i in range(25):
    u = i / 24
    chart.append((0.12 + u * 1.05, 0.60 + 0.68 * u**4, -0.047))
content.append(chart)
marks = multi_lines('screen_glimpsed_marks', content, content_mat, 0.018)
marks.parent = lid
# The front glare is hidden while the camera is behind the laptop; this prevents a false horizon line.
keyed_visibility([screen, marks], [(1, True), (F(ILYA), False), (F(DARK + 0.03), True)])
redacted = empty('redaction_slam', (0, 1.075, -0.064), lid)
bar = plane('redaction_black_band', (0, 0, 0), (2.55, 0.87), BLACK)
bar.parent = redacted
red_type = text('redacted_word', 'R E D A C T E D', 0, 0, 0.255, 'signal', 'mono_bold',
                align='CENTER', valign='CENTER', material=SIGNAL)
red_type.parent = redacted
red_type.location = (0, 0, -0.008)
red_type.rotation_euler.y = math.pi
redacted.rotation_euler.z = -0.045
for frame, scale in [(F(SLAM - 0.07), 1.5), (F(SLAM), 1.0)]:
    redacted.scale = (scale, scale, scale)
    redacted.keyframe_insert('scale', frame=frame)
keyed_visibility([bar, red_type], [(1, True), (F(SLAM - 0.07), False), (F(DARK + 0.03), True)])

# Sticker helpers, all in lid-local XY on the back face.
def sticker_group(name, x, y, angle=0):
    group = empty(name, (x, y, 0.052), lid)
    group.rotation_euler.z = angle
    return group


def sticker_text(name, body, group, x, y, size, font='mono', mat=STICKER_INK):
    obj = text(name, body, x, y, size, 'bone', font, align='CENTER', valign='CENTER', material=mat)
    obj.parent = group
    return obj


def sticker_plane(name, group, loc, size, mat):
    obj = plane(name, loc, size, mat)
    obj.parent = group
    return obj


feel = sticker_group('sticker_feel_the_agi', -0.62, 1.66, -0.07)
sticker_plane('feel_orange_stock', feel, (0, 0, 0), (1.42, 0.40), SIGNAL_DIM)
sticker_text('feel_lettering', 'FEEL THE AGI', feel, 0, 0, 0.205, 'archivo_black')

mask = sticker_group('sticker_smiley_mask', 1.00, 1.47, 0.12)
disc = cylinder('mask_bone_disc', (0, 0, 0), 0.31, 0.012, STICKER_BONE, vertices=40)
disc.parent = mask
for x in (-0.105, 0.105):
    dot = cylinder('mask_dot', (x, 0.075, 0.010), 0.035, 0.008, STICKER_INK, vertices=16)
    dot.parent = mask
smile = bezier('mask_bland_smile', [(-0.15, -0.035, 0.014), (0, -0.16, 0.014), (0.15, -0.035, 0.014)],
               width=0.015, material=STICKER_INK)
smile.parent = mask

unicorn = sticker_group('sticker_tikz_unicorn', -0.68, 0.61, 0.05)
sticker_plane('unicorn_die_cut', unicorn, (0, 0, 0), (1.08, 0.99), STICKER_BONE)
sticker_plane('unicorn_ink_ground', unicorn, (0, 0, 0.007), (0.99, 0.90), STICKER_INK)
uno_lines = [
    [(-0.34, 0.02, 0.016), (-0.18, 0.18, 0.016), (0.15, 0.16, 0.016), (0.29, 0.27, 0.016), (0.35, 0.15, 0.016), (0.22, 0.04, 0.016), (-0.05, -0.02, 0.016), (-0.34, 0.02, 0.016)],
    [(-0.22, 0.0, 0.016), (-0.25, -0.27, 0.016), (-0.15, -0.27, 0.016), (-0.08, -0.01, 0.016)],
    [(0.10, 0.0, 0.016), (0.12, -0.27, 0.016), (0.22, -0.27, 0.016), (0.24, 0.03, 0.016)],
    [(-0.34, 0.08, 0.016), (-0.46, 0.18, 0.016), (-0.38, -0.02, 0.016)],
    [(0.25, 0.25, 0.016), (0.29, 0.44, 0.016), (0.34, 0.27, 0.016)],
]
uno = multi_lines('unicorn_single_stroke', uno_lines, STICKER_BONE, 0.009)
uno.parent = unicorn
sticker_text('unicorn_code', r'\draw[unicorn];', unicorn, 0, -0.37, 0.085, 'mono', STICKER_BONE)

conscious = sticker_group('sticker_slightly_conscious', 0.63, 0.66, -0.16)
oval = circle('conscious_oval', (0, 0, 0), 1.0, material=STICKER_BONE, width=0.012, segments=64)
oval.scale = (0.60, 0.25, 1)
oval.parent = conscious
sticker_text('conscious_line_1', 'SLIGHTLY', conscious, 0, 0.065, 0.13, 'mono_bold', STICKER_BONE)
sticker_text('conscious_line_2', 'CONSCIOUS', conscious, 0, -0.075, 0.13, 'mono_bold', STICKER_BONE)

qstar = sticker_group('sticker_q_star', 0.03, 1.10, 0.30)
star_points = []
for i in range(10):
    a = math.pi / 2 + i * math.pi / 5
    r = 0.28 if i % 2 == 0 else 0.135
    star_points.append((r * math.cos(a), r * math.sin(a), 0))
star = polyline('q_die_cut_star', star_points, width=0.025, cyclic=True, material=STICKER_BONE)
star.parent = qstar
sticker_text('q_lettering', 'Q*', qstar, 0, 0, 0.25, 'serif_italic', SIGNAL_DIM)

attention = sticker_group('sticker_attention', 0.47, 0.19, 0.02)
sticker_plane('attention_strip', attention, (0, 0, 0), (1.92, 0.22), STICKER_INK)
sticker_text('attention_lettering', 'attention is all you need', attention, 0, 0, 0.115, 'serif_italic', STICKER_BONE)

# The emitted slit contracts sideways; it is camera-space only after the camera has centred the laptop.
slit_mat = emission_material('closing_slit_material', 'bone', 1.7)
slit = plane('screen_slit_collapse', (0, 0, 0), (1.0, 0.008), slit_mat)
camera_overlay(slit, room_cam, (0, 0, -2))
for frame in range(F(SLIT), F(DARK + 0.12) + 1):
    t = local_to_time(INFO, frame)
    k = cubic(prog(t, SLIT + 0.05, DARK))
    slit.scale.x = 1.0 + (0.006 - 1.0) * k
    slit.keyframe_insert('scale', frame=frame)
keyed_visibility([slit], [(1, True), (F(SLIT), False), (F(DARK + 0.12), True)])

# Lyrics live in the dark at upper left, without a blackboard or backing panel.
lyric_mat_bone = flat_material('lyric_bone', 'bone', 0.93)
word_times = [("What", WHAT), ("did", DID), ("Ilya", ILYA), ("see?", SEE),
              ("We’ll", WELL), ("never", NEVER), ("know", KNOW)]
lyric_words = []
for row, indices in enumerate((range(0, 4), range(4, 7))):
    x = -0.615
    y = 0.245 - row * 0.092
    for i in indices:
        body, start = word_times[i]
        mat = emission_material(f'lyric_{i}_material', 'signal', 1.0)
        obj = text(f'lyric_{body}', body, size=0.079, font_name='serif_italic', material=mat)
        bpy.context.view_layer.update()
        width = obj.dimensions.x
        camera_overlay(obj, room_cam, (x, y, -2.0))
        end = [132.284, 132.524, 132.818, 133.380, 133.880, 134.340, 136.944][i]
        animate_emission(mat, [(1, 0.93), (F(start), 1.15), (F(end + 0.25), 0.93)])
        # Signal colour during the sung word, then cool back to bone.
        color_socket = mat.node_tree.nodes.get('Emission').inputs['Color']
        for frame, color in [(1, 'bone'), (F(start), 'signal'), (F(end + 0.25), 'bone')]:
            color_socket.default_value = rgba(color)
            color_socket.keyframe_insert('default_value', frame=frame)
        keyed_visibility([obj], [(1, True), (F(start - 0.03), False), (F(LED_OFF + 0.20), True)])
        lyric_words.append(obj)
        x += width + 0.026

know_bar = empty('know_withheld_bar')
camera_overlay(know_bar, room_cam, (0.185, 0.115, -1.975))
know_back = plane('know_black_redaction', (0, 0, 0), (0.29, 0.080), flat_material('know_bar_ink', 'ink2', 1.0))
know_back.parent = know_bar
know_border = rectangle('know_bar_hairline', -0.145, -0.04, 0.145, 0.04, material=BONE_FAINT, width=0.0015, z=0.001)
know_border.parent = know_bar
withheld = text('withheld_label', 'W I T H H E L D', 0, -0.064, 0.022, 'signal', 'mono',
                align='CENTER', valign='CENTER', material=SIGNAL_DIM)
withheld.parent = know_bar
for frame, value in [(F(KNOW_BAR), 0.001), (F(KNOW_BAR + 0.12), 1.0)]:
    know_bar.scale.x = value
    know_bar.keyframe_insert('scale', frame=frame)
keyed_visibility([know_back, know_border, withheld], [(1, True), (F(KNOW_BAR), False), (F(LED_OFF + 0.20), True)])

# A single weak warm bounce keeps the room engraved rather than realistically lit.
room_bounce = add_area_light('screen_bounce', (0, 1.0, 2.0), energy=24,
                             color=(1.0, 0.72, 0.48), size=3.0, target=(0, 0, 0))

ROOM_OBJECTS = list(scene.objects)

# Empty theatre, cut only after the sleep light dies.
theatre_cam = perspective_camera('ilya_theatre_camera', (0, 14.2, 1.45), (0, 2.42, 2.9), lens=50)
key_camera(theatre_cam, F(WAS), (0, 14.2, 1.45), (0, 2.42, 2.9), 50)
key_camera(theatre_cam, F(END), (0, 12.4, 1.40), (0, 2.42, 2.9), 50)

STAGE_BLACK = principled_material('theatre_black', 'ink', 0.0, 0.88)
cube('stage_deck', (0, -1.2, -0.30), (12.0, 11.0, 0.60), STAGE_BLACK)
# Proscenium: broad dark masses plus fine white-line architectural edges.
for x in (-4.42, 4.42):
    cube('proscenium_pilaster', (x, 3.0, 2.45), (0.72, 0.28, 4.90), STAGE_BLACK)
    lines = [[(x - 0.30, 2.84, 0.05), (x - 0.30, 2.84, 4.85)],
             [(x + 0.30, 2.84, 0.05), (x + 0.30, 2.84, 4.85)]]
    multi_lines('pilaster_engraving', lines, BONE_FAINT, 0.012)
cube('proscenium_fascia', (0, 3.0, 5.38), (9.90, 0.28, 0.92), STAGE_BLACK)
cube('proscenium_cornice', (0, 3.0, 5.93), (10.50, 0.40, 0.14), STAGE_BLACK)
arch_lines = [
    [(-4.95, 2.83, 4.92), (4.95, 2.83, 4.92)],
    [(-4.95, 2.83, 5.84), (4.95, 2.83, 5.84)],
    [(-5.25, 2.80, 5.94), (5.25, 2.80, 5.94)],
]
multi_lines('proscenium_white_line_engraving', arch_lines, BONE_FAINT, 0.012)
# Stage boards and the remaining spike marks; there are deliberately no props.
board_lines = []
for i in range(31):
    x = -5.4 + i * 0.36
    board_lines.append([(x, -5.5, 0.012), (x, 2.4, 0.012)])
multi_lines('stage_deck_engraving', board_lines, BONE_FAINT, 0.005)
for i, (x, y) in enumerate([(-1.4, -0.6), (1.1, -1.0), (-2.0, 0.8), (1.9, 0.6), (0, -1.5)]):
    multi_lines(f'empty_stage_spike_{i}', [[(x - 0.12, y, 0.025), (x + 0.12, y, 0.025)],
                                          [(x, y - 0.12, 0.025), (x, y + 0.12, 0.025)]], BONE_MED, 0.012)

# Traveller curtains: open edges at +/-3.1, meeting at zero on the beat before "show?".
curtains = []
for side in (-1, 1):
    group = empty('curtain_left' if side < 0 else 'curtain_right', (side * 4.45, 0, 0))
    verts, faces = [], []
    nx, nz = 32, 12
    for iz in range(nz + 1):
        z = iz * 4.9 / nz
        for ix in range(nx + 1):
            u = ix / nx
            local_x = side * (-4.45 * (1 - u))
            y = 2.42 + 0.12 * math.sin(u * math.tau * 8 + (0 if side > 0 else 2.1))
            verts.append((local_x, y, z))
    for iz in range(nz):
        for ix in range(nx):
            a = iz * (nx + 1) + ix
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    mesh = bpy.data.meshes.new('curtain_folds_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('curtain_velvet', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = group
    obj.data.materials.append(VELVET)
    folds = []
    for ix in range(0, nx + 1, 2):
        u = ix / nx
        x = side * (-4.45 * (1 - u))
        y = 2.42 + 0.12 * math.sin(u * math.tau * 8 + (0 if side > 0 else 2.1)) - 0.015
        folds.append([(x, y, 0.03), (x, y, 4.87)])
    fold_obj = multi_lines('curtain_engraved_folds', folds, BONE_FAINT, 0.009)
    fold_obj.parent = group
    for frame in range(F(FOR), F(MEET) + 1):
        t = local_to_time(INFO, frame)
        k = cubic(prog(t, FOR, MEET))
        group.scale.x = 0.30337 + (1.0 - 0.30337) * k
        group.keyframe_insert('scale', frame=frame)
    group.scale.x = 0.30337
    group.keyframe_insert('scale', frame=1)
    group.scale.x = 1.0
    group.keyframe_insert('scale', frame=F(END))
    curtains.append(group)

# Real spot light on the empty deck; only two lights in the theatre.
spot_data = bpy.data.lights.new('empty_stage_spotlight', 'SPOT')
spot_data.energy = 1450
spot_data.color = (1.0, 0.84, 0.65)
spot_data.spot_size = 0.29
spot_data.spot_blend = 0.42
spot_data.shadow_soft_size = 0.12
spot = bpy.data.objects.new('empty_stage_spotlight', spot_data)
bpy.context.collection.objects.link(spot)
spot.location = (0, -2.4, 8.6)
point_at(spot, (0, 0.1, 0))
for frame, energy in [(F(WAS), 0), (F(WAS + 0.025), 1800), (F(WAS + 0.05), 800),
                      (F(WAS + 0.1), 1450), (F(MEET), 1450), (F(SHOW + 0.08), 0)]:
    spot_data.energy = energy
    spot_data.keyframe_insert('energy', frame=frame)
add_area_light('proscenium_bounce', (0, 8.0, 5.5), energy=32,
               color=(1.0, 0.65, 0.42), size=7, target=(0, 2.8, 3.8))

# A few deterministic dust motes in the beam, no costly volume shader.
for i in range(22):
    u = ((i * 37) % 101) / 101
    z = 0.8 + ((i * 29) % 97) / 97 * 6.8
    spread = 0.12 + (8.6 - z) * 0.07
    x = math.sin(i * 12.37) * spread
    y = -2.4 + (8.6 - z) * 0.29 + math.cos(i * 7.1) * spread
    mote = uv_sphere(f'spot_dust_{i}', (x, y, z), 0.009 + 0.006 * u,
                     material=BONE_MED, segments=8, rings=4)

# Inscription physically lettered on the fascia, with a dim carved layer and sung signal layer.
question = [('WAS', WAS, -3.15), ('IT', IT, -1.85), ('ALL', ALL, -0.65),
            ('FOR', FOR, 0.85), ('SHOW?', SHOW, 2.70)]
carved = flat_material('question_carved', 'bone', 0.07)
for i, (word, start, x) in enumerate(question):
    common = dict(size=0.64, font_name='serif', align='CENTER', valign='CENTER')
    dim = text(f'fascia_carved_{word}', word, material=carved, **common)
    dim.location = (x, 2.835, 5.29)
    dim.rotation_euler = (math.pi / 2, math.pi, 0)
    hot = text(f'fascia_sung_{word}', word, material=SIGNAL, **common)
    hot.location = (x, 2.825, 5.29)
    hot.rotation_euler = (math.pi / 2, math.pi, 0)
    keyed_visibility([hot], [(1, True), (F(start - 0.02), False), (F(END - 0.03), True)])

# Camera-facing inscription remains legible above the empty stage, independent of fascia depth.
overlay_question = text('stage_question_overlay', 'WAS IT ALL FOR SHOW?', size=0.045, font_name='mono_bold',
                        color='signal', align='CENTER', valign='CENTER', material=SIGNAL)
camera_overlay(overlay_question, theatre_cam, (0, 0.28, -2.0))
keyed_visibility([overlay_question], [(1, True), (F(WAS), False), (F(END), True)])

# Curtain seam becomes a single central hairline, then the outro spark.
seam = plane('curtain_seam_light', (0, 0, 0), (0.005, 0.56), EMBER)
camera_overlay(seam, theatre_cam, (0, -0.015, -2))
for frame in range(F(MEET - 0.12), F(END) + 1):
    t = local_to_time(INFO, frame)
    k = prog(t, SHOW + 0.01, END - 0.045)**4
    seam.scale.y = max(0.001, 1 - k)
    seam.keyframe_insert('scale', frame=frame)
keyed_visibility([seam], [(1, True), (F(MEET - 0.12), False)])
spark = uv_sphere('outro_centre_spark', (0, 0, 0), 0.014, material=SIGNAL, segments=16, rings=8)
camera_overlay(spark, theatre_cam, (0, 0, -1.97))
keyed_visibility([spark], [(1, True), (F(END - 0.07), False)])
for frame, radius in [(F(END - 0.07), 0.2), (F(END - 0.01), 1.4)]:
    spark.scale = (radius, radius, radius)
    spark.keyframe_insert('scale', frame=frame)
spark_lines = []
for i in range(9):
    a = i * math.tau / 9 + 0.2
    r0, r1 = 0.018, 0.035 + 0.012 * (i % 3)
    spark_lines.append([(math.cos(a) * r0, math.sin(a) * r0, -1.96),
                        (math.cos(a) * r1, math.sin(a) * r1, -1.96)])
sputter = multi_lines('outro_spark_sputter', spark_lines, EMBER, 0.0018)
sputter.parent = theatre_cam
keyed_visibility([sputter], [(1, True), (F(END - 0.06), False)])

STAGE_OBJECTS = [obj for obj in scene.objects if obj not in ROOM_OBJECTS]
keyed_visibility(ROOM_OBJECTS, [(1, False), (F(STAGE_CUT), True)])
keyed_visibility(STAGE_OBJECTS, [(1, True), (F(STAGE_CUT), False)])
# Restore local visibility tracks after the broad room/stage visibility pass.
keyed_visibility([screen, marks], [(1, True), (F(ILYA), False), (F(DARK + 0.03), True)])
keyed_visibility([slit], [(1, True), (F(SLIT), False), (F(DARK + 0.12), True)])
keyed_visibility([led], [(1, True), (F(DARK - 0.08), False), (F(LED_OFF), True)])
keyed_visibility([bar, red_type], [(1, True), (F(SLAM - 0.07), False), (F(DARK + 0.03), True)])
for i, obj in enumerate(lyric_words):
    start = word_times[i][1]
    keyed_visibility([obj], [(1, True), (F(start - 0.03), False), (F(LED_OFF + 0.20), True)])
keyed_visibility([know_back, know_border, withheld], [(1, True), (F(KNOW_BAR), False), (F(LED_OFF + 0.20), True)])
keyed_visibility([seam], [(1, True), (F(MEET - 0.12), False)])
keyed_visibility([spark], [(1, True), (F(END - 0.07), False)])
keyed_visibility([sputter], [(1, True), (F(END - 0.06), False)])
physical_room = [obj for obj in ROOM_OBJECTS if obj not in lyric_words + [slit, led, know_back, know_border, withheld]]
keyed_visibility(physical_room, [(1, False), (F(DARK + 0.03), True)])
# Camera cuts are timeline-marker bindings, so arbitrary local-frame batch renders stay deterministic.
scene.timeline_markers.new('ROOM', frame=1).camera = room_cam
scene.timeline_markers.new('EMPTY_THEATRE', frame=F(STAGE_CUT)).camera = theatre_cam
scene.camera = room_cam

# One restrained bloom pass for signal/ember only; no volumetric or noise-heavy materials.
from blender.compositing import configure_glare
configure_glare(scene, threshold=0.9, size=7, quality='MEDIUM')

scene['ilya_slam_seconds'] = SLAM
scene['ilya_slit_seconds'] = SLIT
scene['ilya_dark_seconds'] = DARK
scene['ilya_know_withheld_seconds'] = KNOW_BAR
scene['ilya_curtains_meet_seconds'] = MEET
scene['ilya_design'] = 'Native white-line geometry; no reference-image planes, people, eyes or gallery.'
scene.frame_set(1)
save_scene(scene, ROOT / 'src' / 'scenes' / 'ilya.blend')
print(f'ILYA_BUILD_OK objects={len(scene.objects)} frames={scene.frame_end}', flush=True)
