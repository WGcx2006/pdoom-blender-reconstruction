"""Read the committed audio analysis and word-timed lyrics deterministically."""
from __future__ import annotations
from functools import lru_cache
import json
import math
from .common import ROOT


@lru_cache(maxsize=1)
def audio():
    return json.loads((ROOT / 'assets' / 'data' / 'audio.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def lyrics():
    return json.loads((ROOT / 'assets' / 'data' / 'lyrics.json').read_text(encoding='utf-8'))


def env(name, t):
    data = audio().get(name, [])
    if not data:
        return 0.0
    fps = audio().get('fps', 100)
    x = t * fps
    i = math.floor(x)
    if i < 0:
        return data[0]
    if i >= len(data) - 1:
        return data[-1]
    f = x - i
    return data[i] * (1 - f) + data[i + 1] * f


def beat_at(t):
    beats = audio()['beats']
    if t <= beats[0]:
        return (t - beats[0]) / (beats[1] - beats[0])
    if t >= beats[-1]:
        return len(beats) - 1 + (t - beats[-1]) / (beats[-1] - beats[-2])
    lo, hi = 0, len(beats) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if beats[mid] <= t:
            lo = mid
        else:
            hi = mid
    return lo + (t - beats[lo]) / (beats[hi] - beats[lo])


def beat_pulse(t, sharpness=7.0):
    phase = beat_at(t) % 1.0
    return math.exp(-sharpness * phase)


def lines_between(start, end):
    return [line for line in lyrics()['lines'] if line['end'] > start and line['start'] < end]


def line_at(t):
    return next((line for line in lyrics()['lines'] if line['start'] <= t < line['end']), None)


def active_word(line, t):
    if not line:
        return None
    return next((word for word in line['words'] if word['start'] <= t < word['end']), None)


def line_progress(line, t):
    if not line:
        return 0.0
    return max(0.0, min(1.0, (t - line['start']) / max(0.001, line['end'] - line['start'])))


def word_is_sung(word, t):
    return t >= word['start']
