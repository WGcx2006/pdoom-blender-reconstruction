#!/usr/bin/env python3
"""Build same-time reference/reconstruction contact sheets and review metrics."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT/'reference'/'renders'/'stills'
OUT = ROOT/'reviews'


def ssim(a,b):
    a = cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float64)
    b = cv2.cvtColor(b,cv2.COLOR_BGR2GRAY).astype(np.float64)
    mu1=cv2.GaussianBlur(a,(11,11),1.5); mu2=cv2.GaussianBlur(b,(11,11),1.5)
    v1=cv2.GaussianBlur(a*a,(11,11),1.5)-mu1*mu1
    v2=cv2.GaussianBlur(b*b,(11,11),1.5)-mu2*mu2
    cov=cv2.GaussianBlur(a*b,(11,11),1.5)-mu1*mu2
    return float((((2*mu1*mu2+6.5025)*(2*cov+58.5225))/((mu1*mu1+mu2*mu2+6.5025)*(v1+v2+58.5225))).mean())


def compare(ref, ours):
    a=cv2.imread(str(ref)); b=cv2.imread(str(ours))
    if a is None or b is None: return {'valid':False}
    b=cv2.resize(b,(a.shape[1],a.shape[0]),interpolation=cv2.INTER_AREA)
    diff=cv2.absdiff(a,b)
    return {'valid':True,'mae':float(diff.mean()),'rmse':float(np.sqrt((diff.astype(np.float64)**2).mean())),
            'ssim':ssim(a,b),'ref_mean':float(a.mean()),'ours_mean':float(b.mean())}


def main():
    p=argparse.ArgumentParser(); p.add_argument('scene'); p.add_argument('--times',required=True); p.add_argument('--final',action='store_true'); args=p.parse_args()
    directory=OUT/f'scene_{args.scene}'/('final' if args.final else 'preview'); pairs=directory/'pairs'; diffs=directory/'differences'
    pairs.mkdir(parents=True,exist_ok=True); diffs.mkdir(parents=True,exist_ok=True)
    thumbs=[]; metrics=[]
    for value in args.times.split(','):
        t=float(value); ref=REF/f'f_{t:07.2f}.png'
        frame=math.floor(t*60+0.5)
        ours=ROOT/'renders'/('final' if args.final else 'preview')/args.scene/f'{frame:06d}.png'
        if not ref.is_file() or not ours.is_file():
            metrics.append({'time':t,'reference':str(ref),'ours':str(ours),'valid':False,'reason':'missing'}); continue
        m=compare(ref,ours); m.update({'time':t,'frame':frame,'reference':str(ref),'ours':str(ours)}); metrics.append(m)
        if not m['valid']: continue
        im1=Image.open(ref).convert('RGB').resize((640,360)); im2=Image.open(ours).convert('RGB').resize((640,360))
        pair=Image.new('RGB',(1280,390),(12,12,14)); pair.paste(im1,(0,30)); pair.paste(im2,(640,30))
        draw=ImageDraw.Draw(pair); draw.text((8,8),f'REF {args.scene} t={t:.2f}',fill='white'); draw.text((648,8),'BLENDER RECONSTRUCTION',fill='white')
        pair.save(pairs/f'{t:07.2f}.jpg',quality=92)
        a=cv2.imread(str(ref)); b=cv2.resize(cv2.imread(str(ours)),(a.shape[1],a.shape[0])); cv2.imwrite(str(diffs/f'{t:07.2f}.png'),cv2.absdiff(a,b))
        thumbs.append((t,pair))
    if thumbs:
        sheet=Image.new('RGB',(1280,390*len(thumbs)),(12,12,14))
        for i,(_,im) in enumerate(thumbs): sheet.paste(im,(0,i*390))
        sheet.save(directory/'contact_sheet.jpg',quality=90)
    (directory/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    (directory/'review.json').write_text(json.dumps({'scene':args.scene,'reviewed':False,'pairs':len(thumbs),'metrics':'metrics.json','notes':'Main agent must inspect images before sign-off.'},indent=2),encoding='utf-8')
    print(f'WROTE {directory} pairs={len(thumbs)}')

if __name__=='__main__': main()
