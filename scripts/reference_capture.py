#!/usr/bin/env python3
"""Capture reference stills and videos without changing the reference project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
REPO = REFERENCE / "pdoom-video"
APP = REPO / "app"
RENDERER = APP / "scripts" / "render.ts"
BUN = REFERENCE / "tools" / "bun-windows-x64" / "bun.exe"
URL = "http://127.0.0.1:5173"
EXPECTED_COMMIT = "fa164b74fd0b26a99375715b619c55b4a0fb3d05"
STILLS = REFERENCE / "renders" / "stills"
SHORTS = REFERENCE / "renders" / "shorts"
FULL = REFERENCE / "renders" / "full" / "pdoom_reference.mp4"
QA = REFERENCE / "qa"
LOGS = QA / "logs"
PROVENANCE = REFERENCE / "provenance.json"
FPS = 60
WIDTH = 1920
HEIGHT = 1080
SHUTTER = "0.2"
SAMPLES = "auto"

TIMELINE_JS = r'''import { chromium } from "playwright-core";
const browser = await chromium.launch({channel:"chrome",headless:true,args:["--use-angle=metal","--enable-gpu-rasterization","--ignore-gpu-blocklist","--disable-background-timer-throttling","--disable-renderer-backgrounding","--disable-backgrounding-occluded-windows"]});
try {
  const page = await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  await page.goto("http://127.0.0.1:5173/?export=1");
  await page.waitForFunction(() => globalThis.__pdoom?.ready || globalThis.__pdoom?.error, null, {timeout:120000});
  const result = await page.evaluate(() => ({duration:globalThis.__pdoom.duration,timeline:globalThis.__pdoom.timeline,error:globalThis.__pdoom.error,errors:globalThis.__pdoom.errors}));
  if (result.error) throw new Error(result.error);
  console.log(JSON.stringify(result));
} finally { await browser.close(); }'''


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command_text(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def run_logged(name: str, command: list[str], log_path: Path, *, cwd: Path | None = None,
               capture: bool = False) -> tuple[dict, str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = utcnow()
    record = {
        "name": name,
        "command": command,
        "command_text": command_text(command),
        "cwd": str(cwd or ROOT),
        "log": rel(log_path),
        "started_at": started,
        "exit_code": None,
    }
    output = ""
    with log_path.open("w", encoding="utf-8", newline="") as log:
        log.write(f"started_at: {started}\ncommand: {command_text(command)}\ncwd: {cwd or ROOT}\n\n")
        log.flush()
        try:
            if capture:
                completed = subprocess.run(command, cwd=str(cwd or ROOT), stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                           errors="replace", check=False)
                output = completed.stdout or ""
                log.write(output)
                code = completed.returncode
            else:
                with subprocess.Popen(command, cwd=str(cwd or ROOT), stdout=log,
                                      stderr=subprocess.STDOUT) as process:
                    code = process.wait()
        except Exception as error:
            record["launch_error"] = f"{type(error).__name__}: {error}"
            log.write(f"\nlaunch_error: {record['launch_error']}\n")
            code = None
        record["exit_code"] = code
        record["finished_at"] = utcnow()
        log.write(f"\nexit_code: {code}\nfinished_at: {record['finished_at']}\n")
    record["status"] = "succeeded" if code == 0 else "failed"
    return record, output


def check_output(command: list[str]) -> str:
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace", check=True)
    return completed.stdout.strip()


def environment() -> dict:
    commit = check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"])
    if commit != EXPECTED_COMMIT:
        raise RuntimeError(f"reference commit is {commit}, expected {EXPECTED_COMMIT}")
    bun_version = check_output([str(BUN), "--version"])
    if bun_version != "1.4.4":
        raise RuntimeError(f"Bun version is {bun_version}, expected 1.4.4")
    with urllib.request.urlopen(URL, timeout=5) as response:
        http_status = response.status
    if http_status != 200:
        raise RuntimeError(f"Vite returned HTTP {http_status}")
    return {
        "reference_repo": str(REPO),
        "commit": commit,
        "commit_command": ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        "bun": str(BUN),
        "bun_version": bun_version,
        "bun_version_command": [str(BUN), "--version"],
        "vite_url": URL,
        "vite_http_status": http_status,
        "ffmpeg_version": check_output(["ffmpeg", "-version"]).splitlines()[0],
        "ffprobe_version": check_output(["ffprobe", "-version"]).splitlines()[0],
    }


def read_timeline() -> dict:
    command = [str(BUN), "--cwd", str(APP), "-e", TIMELINE_JS]
    record, output = run_logged("timeline", command, LOGS / "timeline" / "timeline.log",
                                cwd=APP, capture=True)
    if record["exit_code"] != 0:
        raise RuntimeError(f"timeline query failed; see {record['log']}")
    data = json.loads(output.strip())
    if data.get("errors"):
        raise RuntimeError(f"scene errors: {data['errors']}")
    if len(data["timeline"]) != 22:
        raise RuntimeError(f"expected 22 scenes, got {len(data['timeline'])}")
    data["query"] = record
    data["sources"] = {
        "timeline": "reference/pdoom-video/app/src/timeline.ts",
        "audio": "reference/pdoom-video/data/audio.json",
        "timeline_sha256": sha256(REPO / "app" / "src" / "timeline.ts"),
        "audio_sha256": sha256(REPO / "data" / "audio.json"),
    }
    write_json(QA / "timeline.json", data)
    return data


def still_filename(time: float) -> str:
    return f"f_{f'{time:.2f}'.rjust(7, '0')}.png"


def pixel_still_command(time: float, output: Path) -> list[str]:
    script = f'''import {{ chromium }} from "playwright-core";
const browser = await chromium.launch({{channel:"chrome",headless:true,args:["--use-angle=metal","--enable-gpu-rasterization","--ignore-gpu-blocklist","--disable-background-timer-throttling","--disable-renderer-backgrounding","--disable-backgrounding-occluded-windows"]}});
try {{
  const page = await browser.newPage({{viewport:{{width:1920,height:1080}},deviceScaleFactor:1}});
  await page.goto("{URL}/?export=1");
  await page.waitForFunction(() => globalThis.__pdoom?.ready || globalThis.__pdoom?.error, null, {{timeout:120000}});
  const result = await page.evaluate(async (t) => {{
    const subframes = await globalThis.__pdoom.still(t, 1, 0.5);
    return {{subframes, png: globalThis.__pdoom.png()}};
  }}, {time});
  await Bun.write({json.dumps(str(output))}, Buffer.from(result.png, "base64"));
  console.log(JSON.stringify({{time:{time}, subframes:result.subframes, output:{json.dumps(str(output))}}}));
}} finally {{ await browser.close(); }}'''
    return [str(BUN), "--cwd", str(APP), "-e", script]


def time_argument(time: float) -> str:
    return f"{time:.3f}".rstrip("0").rstrip(".")


def png_info(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
        valid = len(header) == 24 and header[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", header[16:24]) if valid else (None, None)
        return {
            "valid": bool(valid and width == WIDTH and height == HEIGHT),
            "width": width,
            "height": height,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    except Exception as error:
        return {"valid": False, "error": f"{type(error).__name__}: {error}"}


def still_plan(timeline: list[dict]) -> list[dict]:
    plan = []
    for scene_index, scene in enumerate(timeline, 1):
        start, end = float(scene["start"]), float(scene["end"])
        times = {"start": start + 0.1, "middle": (start + end) / 2, "end": end - 0.1}
        # Reuse the supplied stable frame, only 0.1 s from shoggoth's exact midpoint.
        if scene["id"] == "shoggoth":
            times["middle"] = 34.0
        for position, time in times.items():
            time = round(time, 3)
            plan.append({
                "scene_index": scene_index,
                "scene": scene["id"],
                "scene_start": start,
                "scene_end": end,
                "position": position,
                "time": time,
                "boundary_margin_seconds": round(min(time - start, end - time), 3),
                "file": rel(STILLS / still_filename(time)),
            })
    return plan


def run_stills(timeline: list[dict], force: bool) -> list[str]:
    STILLS.mkdir(parents=True, exist_ok=True)
    plan = still_plan(timeline)
    results = []
    failures = []
    for scene_index in range(1, 23):
        group = [item for item in plan if item["scene_index"] == scene_index]
        missing = [item for item in group
                   if force or not (ROOT / item["file"]).is_file() or (ROOT / item["file"]).stat().st_size == 0]
        command_record = None
        if missing:
            scene = group[0]["scene"]
            times = ",".join(time_argument(item["time"]) for item in missing)
            command = [str(BUN), "app/scripts/render.ts", "stills", "--t", times,
                       "--url", URL, "--out", str(STILLS)]
            command_record, _ = run_logged(f"stills_{scene_index:02d}_{scene}", command,
                                           LOGS / "stills" / f"{scene_index:02d}_{scene}.log", cwd=REPO)
        for item in group:
            result = dict(item)
            path = ROOT / item["file"]
            was_rendered = item in missing
            result["capture"] = "rendered" if was_rendered else "reused_existing"
            result["command"] = command_record["command"] if was_rendered and command_record else None
            result["command_text"] = command_record["command_text"] if was_rendered and command_record else None
            result["log"] = command_record["log"] if was_rendered and command_record else None
            result["exit_code"] = command_record["exit_code"] if was_rendered and command_record else None
            result.update(png_info(path))
            if was_rendered and not result["valid"]:
                fallback_record, _ = run_logged(
                    f"stills_{scene_index:02d}_{item['scene']}_{item['position']}_pixel_fallback",
                    pixel_still_command(item["time"], path),
                    LOGS / "stills" / f"{scene_index:02d}_{item['scene']}_{item['position']}.pixel-fallback.log",
                    cwd=APP,
                )
                result["pixel_fallback"] = fallback_record
                result.update(png_info(path))
                if result["valid"] and fallback_record["exit_code"] == 0:
                    result["capture"] = "rendered_pixel_fallback"
            result["status"] = "succeeded" if result["valid"] else "failed"
            if not result["valid"]:
                failures.append(f"still {item['scene']} {item['position']} t={item['time']}: {result.get('error', 'invalid or missing PNG')}")
            results.append(result)
        write_json(QA / "stills_index.json", {
            "generated_at": utcnow(), "boundary_margin_seconds": 0.1,
            "render_parameters": {"mode": "stills", "renderer_defaults": {"samples": 1, "shutter": 0.5},
                                  "width": WIDTH, "height": HEIGHT},
            "count": len(results), "frames": results,
        })
        print(f"stills {scene_index}/22: {group[0]['scene']}", flush=True)
    return failures


def outro_windows(timeline: list[dict], audio: dict) -> dict:
    outro = next(scene for scene in timeline if scene["id"] == "outro")
    beats = [float(b) for b in audio["beats"]
             if float(b) >= float(outro["start"]) - 0.05 and float(b) < float(outro["end"])]
    if not beats or beats[0] > float(outro["start"]) + 0.05:
        beats.insert(0, float(outro["start"]))

    def tb(index: float) -> float:
        whole = int(index)
        fraction = index - whole

        def integer(i: int) -> float:
            return beats[i] if i < len(beats) else beats[-1] + (i - len(beats) + 1) * 0.4644

        return integer(whole) + (integer(whole + 1) - integer(whole)) * fraction

    fade0 = min(30.0, float(len(beats) - 6))
    windows = {
        "morph": {"from": round(tb(24.5), 3), "to": round(tb(29.2), 3),
                  "reason": "end-card infinity to 8 to 0/0 to NaN metamorphosis"},
        "rewind": {"from": round(tb(fade0 + 0.9), 3), "to": float(outro["end"]),
                   "reason": "end-card collapse, regenerate click, accelerating plate rewind, opening reverse and loop park"},
    }
    return {"beat_count": len(beats), "fade_beat": fade0, "card_beat": 20, "windows": windows}


def short_plan(timeline: list[dict], audio: dict) -> tuple[list[dict], dict]:
    scenes = {scene["id"]: scene for scene in timeline}
    outro = outro_windows(timeline, audio)
    specs = [
        ("shoggoth_core", "shoggoth", 32.054, 35.054, "x-ray scan, creature and mask motion"),
        ("paperclips_core", "paperclips", 97.051, 100.051, "clip replication and overhead-to-floor camera move"),
        ("ilya_core", "ilya", 132.05, 135.05, "camera circles from behind the monitor toward the front"),
        ("outro_morph", "outro", outro["windows"]["morph"]["from"], outro["windows"]["morph"]["to"],
         outro["windows"]["morph"]["reason"]),
        ("outro_rewind", "outro", outro["windows"]["rewind"]["from"], outro["windows"]["rewind"]["to"],
         outro["windows"]["rewind"]["reason"]),
    ]
    plan = []
    for name, scene, start, end, reason in specs:
        if not (scenes[scene]["start"] <= start < end <= scenes[scene]["end"] + 0.001):
            raise RuntimeError(f"short {name} is outside scene {scene}: {start}..{end}")
        if not 2.0 <= end - start <= 4.0:
            raise RuntimeError(f"short {name} duration must be 2-4 seconds, got {end - start}")
        plan.append({"name": name, "scene": scene, "from": start, "to": end,
                     "duration": round(end - start, 3), "reason": reason,
                     "file": rel(SHORTS / f"{name}.mp4")})
    return plan, outro


def probe_video(path: Path, log_path: Path) -> tuple[dict, dict | None]:
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    record, output = run_logged(f"ffprobe_{path.stem}", command, log_path, capture=True)
    data = json.loads(output) if record["exit_code"] == 0 and output.strip() else None
    return record, data


def video_validation(path: Path, expected_frames: int, probe: dict | None) -> dict:
    checks = {"probe_available": probe is not None}
    if probe:
        videos = [stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"]
        stream = videos[0] if videos else {}
        checks.update({
            "width": stream.get("width") == WIDTH,
            "height": stream.get("height") == HEIGHT,
            "fps": stream.get("avg_frame_rate") == "60/1",
            "frame_count": int(stream.get("nb_frames", -1)) == expected_frames,
            "duration": abs(float(stream.get("duration", -100)) - expected_frames / FPS) <= 0.051,
            "h264": stream.get("codec_name") == "h264",
        })
    return {"checks": checks, "passed": all(checks.values())}


def inspect_short(item: dict, render_record: dict | None) -> dict:
    path = ROOT / item["file"]
    expected_frames = round(item["to"] * FPS) - round(item["from"] * FPS)
    probe_record, probe = probe_video(path, LOGS / "shorts" / f"{item['name']}.ffprobe.log")
    validation = video_validation(path, expected_frames, probe)
    decode_command = ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"]
    decode_record, _ = run_logged(f"decode_{item['name']}", decode_command,
                                  LOGS / "shorts" / f"{item['name']}.decode.log")
    contact = QA / f"shorts_contact_{item['name']}.png"
    middle, last = expected_frames // 2, expected_frames - 1
    contact_command = ["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf",
                       f"select='eq(n,0)+eq(n,{middle})+eq(n,{last})',scale=640:360,tile=3x1",
                       "-frames:v", "1", str(contact)]
    contact_record, _ = run_logged(f"contact_{item['name']}", contact_command,
                                   LOGS / "shorts" / f"{item['name']}.contact.log")
    stable = bool(render_record is None or render_record["exit_code"] == 0)
    stable = stable and validation["passed"] and decode_record["exit_code"] == 0 and contact_record["exit_code"] == 0
    result = dict(item)
    result.update({
        "expected_frames": expected_frames,
        "render": render_record,
        "ffprobe": probe_record,
        "probe_data": probe,
        "decode": decode_record,
        "contact_sheet": {"path": rel(contact), **contact_record},
        "validation": validation,
        "stable": stable,
        "status": "succeeded" if stable else "failed",
    })
    if path.is_file():
        result["bytes"] = path.stat().st_size
        result["sha256"] = sha256(path)
    return result


def run_shorts(timeline: list[dict], audio: dict, force: bool) -> list[str]:
    SHORTS.mkdir(parents=True, exist_ok=True)
    plan, outro = short_plan(timeline, audio)
    write_json(QA / "outro_timing.json", outro)
    results = []
    failures = []
    for item in plan:
        path = ROOT / item["file"]
        render_record = None
        if force or not path.is_file() or path.stat().st_size == 0:
            command = [str(BUN), "app/scripts/render.ts", "video", "--from", time_argument(item["from"]),
                       "--to", time_argument(item["to"]), "--fps", str(FPS), "--samples", SAMPLES,
                       "--shutter", SHUTTER, "--url", URL, "--out", str(path)]
            render_record, _ = run_logged(f"short_{item['name']}", command,
                                          LOGS / "shorts" / f"{item['name']}.render.log", cwd=REPO)
        result = inspect_short(item, render_record)
        results.append(result)
        if not result["stable"]:
            failures.append(f"short {item['name']}: validation={result['validation']['checks']}, decode_exit={result['decode']['exit_code']}")
        write_json(QA / "shorts_index.json", {
            "generated_at": utcnow(),
            "parameters": {"width": WIDTH, "height": HEIGHT, "fps": FPS, "samples": SAMPLES,
                           "shutter": float(SHUTTER), "audio": True, "crf": 16, "preset": "slow"},
            "count": len(results), "clips": results,
        })
        print(f"short {len(results)}/{len(plan)}: {item['name']} stable={result['stable']}", flush=True)
    return failures


def run_full(timeline: list[dict], force: bool) -> list[str]:
    plan, _ = short_plan(timeline, json.loads((REPO / "data" / "audio.json").read_text(encoding="utf-8")))
    index_path = QA / "shorts_index.json"
    if not index_path.is_file():
        return ["full export blocked: shorts_index.json is missing"]
    short_results = json.loads(index_path.read_text(encoding="utf-8")).get("clips", [])
    by_name = {item["name"]: item for item in short_results}
    unstable = [item["name"] for item in plan
                if not by_name.get(item["name"], {}).get("stable") or not (ROOT / item["file"]).is_file()]
    if unstable:
        return [f"full export blocked: unstable or missing shorts: {', '.join(unstable)}"]

    FULL.parent.mkdir(parents=True, exist_ok=True)
    duration = float(timeline[-1]["end"])
    expected_frames = round(duration * FPS)
    render_record = None
    if force or not FULL.is_file() or FULL.stat().st_size == 0:
        command = [str(BUN), "app/scripts/render.ts", "video", "--from", "0", "--to", time_argument(duration),
                   "--fps", str(FPS), "--samples", SAMPLES, "--shutter", SHUTTER,
                   "--url", URL, "--out", str(FULL)]
        running = {"generated_at": utcnow(), "status": "running", "command": command,
                   "command_text": command_text(command), "log": rel(LOGS / "full" / "pdoom_reference.render.log")}
        write_json(QA / "full_index.json", running)
        render_record, _ = run_logged("full_pdoom_reference", command,
                                      LOGS / "full" / "pdoom_reference.render.log", cwd=REPO)
    probe_record, probe = probe_video(FULL, LOGS / "full" / "pdoom_reference.ffprobe.log")
    validation = video_validation(FULL, expected_frames, probe)
    decode_command = ["ffmpeg", "-v", "error", "-i", str(FULL), "-map", "0:v:0", "-f", "null", "-"]
    decode_record, _ = run_logged("decode_full_pdoom_reference", decode_command,
                                  LOGS / "full" / "pdoom_reference.decode.log")
    stable = bool(render_record is None or render_record["exit_code"] == 0)
    stable = stable and validation["passed"] and decode_record["exit_code"] == 0
    result = {
        "generated_at": utcnow(), "file": rel(FULL), "from": 0, "to": duration,
        "expected_frames": expected_frames,
        "parameters": {"width": WIDTH, "height": HEIGHT, "fps": FPS, "samples": SAMPLES,
                       "shutter": float(SHUTTER), "audio": True, "crf": 16, "preset": "slow"},
        "render": render_record, "ffprobe": probe_record, "probe_data": probe,
        "decode": decode_record, "validation": validation,
        "stable": stable, "status": "succeeded" if stable else "failed",
    }
    if FULL.is_file():
        result["bytes"] = FULL.stat().st_size
        result["sha256"] = sha256(FULL)
    write_json(QA / "full_index.json", result)
    return [] if stable else [f"full export: validation={validation['checks']}, decode_exit={decode_record['exit_code']}"]


def update_provenance(env: dict, timeline: dict, stage: str, failures: list[str]) -> None:
    def optional(name: str) -> dict | None:
        path = QA / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

    stills = optional("stills_index.json")
    shorts = optional("shorts_index.json")
    full = optional("full_index.json")
    value = {
        "generated_at": utcnow(),
        "last_stage": stage,
        "status": "failed" if failures else "succeeded",
        "failures": failures,
        "environment": env,
        "renderer": "reference/pdoom-video/app/scripts/render.ts",
        "capture_script": {"path": "scripts/reference_capture.py", "sha256": sha256(Path(__file__).resolve())},
        "sources": timeline["sources"],
        "duration_seconds": timeline["duration"],
        "scene_count": len(timeline["timeline"]),
        "video_parameters": {"width": WIDTH, "height": HEIGHT, "fps": FPS, "samples": SAMPLES,
                             "shutter": float(SHUTTER), "url": URL},
        "artifacts": {
            "timeline": "reference/qa/timeline.json",
            "stills_index": "reference/qa/stills_index.json" if stills else None,
            "stills_succeeded": sum(x["status"] == "succeeded" for x in stills["frames"]) if stills else 0,
            "stills_expected": 66,
            "shorts_index": "reference/qa/shorts_index.json" if shorts else None,
            "shorts_stable": sum(x["stable"] for x in shorts["clips"]) if shorts else 0,
            "shorts_expected": 5,
            "full_index": "reference/qa/full_index.json" if full else None,
            "full_stable": full.get("stable") if full else None,
        },
        "logs": "reference/qa/logs",
    }
    write_json(PROVENANCE, value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["all", "stills", "shorts", "full"], default="all")
    parser.add_argument("--force", action="store_true", help="rerender outputs instead of reusing existing files")
    args = parser.parse_args()
    for directory in [STILLS, SHORTS, FULL.parent, QA, LOGS]:
        directory.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    env = None
    timeline = None
    try:
        env = environment()
        timeline = read_timeline()
        audio = json.loads((REPO / "data" / "audio.json").read_text(encoding="utf-8"))
        if abs(float(audio["duration"]) - float(timeline["duration"])) > 0.0001:
            raise RuntimeError("audio.json duration differs from page duration")
        if args.stage in ("all", "stills"):
            failures.extend(run_stills(timeline["timeline"], args.force))
        if args.stage in ("all", "shorts"):
            failures.extend(run_shorts(timeline["timeline"], audio, args.force))
        if args.stage in ("all", "full") and not failures:
            failures.extend(run_full(timeline["timeline"], args.force))
        elif args.stage == "all" and failures:
            failures.append("full export not started because an earlier stage failed")
    except KeyboardInterrupt:
        failures.append("interrupted by user")
        return_code = 130
    except Exception as error:
        failures.append(f"{type(error).__name__}: {error}")
        return_code = 1
    else:
        return_code = 1 if failures else 0
    finally:
        if env is not None and timeline is not None:
            update_provenance(env, timeline, args.stage, failures)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr, flush=True)
    print(f"capture stage={args.stage} exit={return_code}", flush=True)
    return return_code


if __name__ == "__main__":
    sys.exit(main())
