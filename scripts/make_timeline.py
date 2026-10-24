#!/usr/bin/env python3
"""Generate the authoritative zero-based global frame timeline."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reference" / "qa" / "timeline.json"
OUTPUT = ROOT / "src" / "timeline.json"
FPS = 60


def js_round(value: float) -> int:
    return math.floor(value + 0.5)


def main() -> None:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    scenes = []
    for index, item in enumerate(raw["timeline"]):
        start_frame = js_round(float(item["start"]) * FPS)
        end_frame = js_round(float(item["end"]) * FPS)
        scenes.append({
            "index": index,
            "id": item["id"],
            "start": float(item["start"]),
            "end": float(item["end"]),
            "start_frame": start_frame,
            "end_frame": end_frame,
            "frame_count": end_frame - start_frame,
            "blender_frame_start": 1,
            "blender_frame_end": end_frame - start_frame,
        })
    total = js_round(float(raw["duration"]) * FPS)
    assert len(scenes) == 22
    assert scenes[0]["start_frame"] == 0
    assert scenes[-1]["end_frame"] == total == 9399
    assert all(scenes[i]["end_frame"] == scenes[i + 1]["start_frame"] for i in range(21))
    result = {
        "fps": FPS,
        "width": 1920,
        "height": 1080,
        "duration": float(raw["duration"]),
        "total_frames": total,
        "frame_convention": "zero-based global [start_frame,end_frame); Blender local frames are one-based",
        "source": "reference/qa/timeline.json",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "scenes": scenes,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT} with {len(scenes)} scenes and {total} frames")


if __name__ == "__main__":
    main()
