#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a vertical Short from segment MP3s + background."""
import os, subprocess, random, glob

BACKGROUNDS = sorted(glob.glob("assets/backgrounds/*.jpg") + glob.glob("assets/backgrounds/*.png") + glob.glob("assets/backgrounds/*.webp"))
SEG_DIR = "115"
OUT = "build/video.mp4"

def main():
    if not os.path.exists(SEG_DIR):
        print(f"ERROR: {SEG_DIR} not found", file=sys.stderr)
        return 1

    # Read pick.txt
    with open("pick.txt", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    key, name, start, end = lines[0], lines[1], int(lines[2]), int(lines[3])

    mp3s = []
    for i in range(start-1, end):
        mp3 = os.path.join(key, f"{i:03d}.mp3")
        if os.path.exists(mp3):
            mp3s.append(mp3)
        else:
            print(f"WARNING: {mp3} not found", file=sys.stderr)

    if not mp3s:
        print("ERROR: no mp3 files", file=sys.stderr)
        return 1

    os.makedirs("build", exist_ok=True)
    concat_list = "build/concat.txt"
    with open(concat_list, "w") as f:
        for mp3 in mp3s:
            f.write(f"file '{mp3}'\n")

    bg = random.choice(BACKGROUNDS) if BACKGROUNDS else None
    if bg:
        bg_ext = "png" if bg.endswith(".png") else "jpg"
        bg_out = f"build/bg.{bg_ext}"
        subprocess.run(["ffmpeg", "-y", "-i", bg, bg_out], capture_output=True)

    # Duration
    durations = []
    for mp3 in mp3s:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", mp3], capture_output=True, text=True)
        durations.append(float(r.stdout.strip()))
    total_dur = sum(durations)

    print(f"Render video: {len(mp3s)} segments, total {total_dur:.1f}s")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list]
    if bg:
        cmd += ["-i", bg_out]
    cmd += [
        "-filter_complex", f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[p];[p]pad=1080:1920:(ow-iw)/2:(oh-ih)/2[v]",
        "-map", "[v]",
        "-map", "1:a?" if bg else "-map", "0:a",
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "25",
        "-t", f"{total_dur:.1f}", "-movflags", "+faststart", OUT
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR: {r.stderr[-500:]}", file=sys.stderr)
        return 1

    print(f"Video rendered: {os.path.getsize(OUT)} bytes")
    return 0

if __name__ == "__main__":
    main()
