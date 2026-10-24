"""Native vector charts and scientific-paper furniture."""
from __future__ import annotations
from .curves import polyline, rectangle, dashed_line
from .typography import label


def axes(name, x0=-8, x1=8, y0=-4, y1=4, x_label='', y_label='', color='ash'):
    polyline(f'{name}_x',[(x0,y0,0),(x1,y0,0)],color,0.012)
    polyline(f'{name}_y',[(x0,y0,0),(x0,y1,0)],color,0.012)
    if x_label:
        label(f'{name}_xlabel',x_label,x1,y0-0.28,0.16,color,'RIGHT')
    if y_label:
        obj = label(f'{name}_ylabel',y_label,x0-0.18,y1,0.16,color,'RIGHT')
        obj.rotation_euler.z = 1.57079632679


def line_chart(name, values, bounds=(-8,-3,8,4), color='signal', width=0.025):
    x0,y0,x1,y1 = bounds
    lo,hi = min(values),max(values)
    span = hi-lo or 1
    points = [(x0+(x1-x0)*i/(len(values)-1),y0+(y1-y0)*(v-lo)/span,0.02) for i,v in enumerate(values)]
    return polyline(name,points,color,width)


def bar_chart(name, values, bounds=(-8,-3,8,4), color='ash', width=0.02):
    from .geometry import cube
    from .palette import flat_material
    x0,y0,x1,y1 = bounds
    maximum = max(values) or 1
    slot = (x1-x0)/len(values)
    objects = []
    mat = flat_material(f'{name}_mat',color)
    for i,value in enumerate(values):
        height = (y1-y0)*value/maximum
        objects.append(cube(f'{name}_{i}',(x0+(i+0.5)*slot,y0+height/2,0),(slot*0.72,height,0.015),mat))
    return objects


def safe_frames():
    rectangle('title_safe',-8.64,-4.32,8.64,4.32,'graphite',0.008)
    rectangle('action_safe',-8.928,-4.86,8.928,4.86,'ash',0.008)
    label('title_safe_label','TITLE SAFE 90%',-8.55,4.48,0.14,'ash')
    label('action_safe_label','ACTION SAFE 93%',-8.85,5.08,0.14,'ash')


def crop_marks(color='bone'):
    objects = []
    for sx in (-1,1):
        for sy in (-1,1):
            x,y = sx*8.9,sy*4.7
            objects.append(polyline(f'crop_h_{sx}_{sy}',[(x-sx*0.5,y,0),(x+sx*0.25,y,0)],color,0.012))
            objects.append(polyline(f'crop_v_{sx}_{sy}',[(x,y-sy*0.5,0),(x,y+sy*0.25,0)],color,0.012))
    return objects


def leader_label(name, body, text_pos, target, color='ash', active=False):
    x,y = text_pos
    tx,ty,tz = target
    label(f'{name}_text',body,x,y,0.16,'signal' if active else color)
    end_x = x+2.2
    polyline(f'{name}_leader',[(x,y-0.18,0),(end_x,y-0.18,0),(tx,ty,tz)],'signal' if active else color,0.008)
