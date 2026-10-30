#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a vertical Short from segment MP3s + background."""
import os, sys, subprocess, random, glob

BACKGROUNDS = sorted(glob.glob("assets/backgrounds/*.jpg") + glob.glob("assets/backgrounds/*.png") + glob.glob("assets/backgrounds/*.webp"))
SEG_DIR = "115"
OUT = "build/video.mp4"

def main():
    if not os.path.exists(SEG_DIR):
        print(f"ERROR: {SEG_DIR} not found", file=sys.stderr)
        return 1

    with open("pick.txt", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    key, name, start, end = lines[0], lines[1], int(lines[2]), int(lines[3])

    mp3s = []
    for i in range(start-1, end):
        mp3 = key + "/" + f"{i:03d}.mp3"
        if os.path.exists(mp3):
            mp3s.append(os.path.abspath(mp3))
        else:
            print(f"WARNING: {mp3} not found", file=sys.stderr)

    if not mp3s:
        print("ERROR: no mp3 files", file=sys.stderr)
        return 1

    os.makedirs("build", exist_ok=True)
    concat_list = os.path.abspath("build/concat.txt")
    with open(concat_list, "w") as f:
        for mp3 in mp3s:
            f.write('file ' + mp3.replace(chr(92), '/') + chr(10))

    bg = random.choice(BACKGROUNDS) if BACKGROUNDS else None
    if bg:
        bg_ext = "png" if bg.endswith(".png") else "jpg"
        bg_out = os.path.abspath("build/bg." + bg_ext)
        subprocess.run(["ffmpeg", "-y", "-i", bg, bg_out], capture_output=True)

    durations = []
    for mp3 in mp3s:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", mp3], capture_output=True, text=True)
        durations.append(float(r.stdout.strip()))
    total_dur = sum(durations)

    print(f"Render video: {len(mp3s)} segments, total {total_dur:.1f}s")

    # Build audio concat
    audio_out = os.path.abspath("build/audio.mp3")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", audio_out], capture_output=True)

    if bg:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", bg_out,
            "-i", audio_out,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "25",
            "-c:a", "aac", "-b:a", "128k", "-shortest",
            "-t", str(total_dur), "-movflags", "+faststart",
            OUT
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", audio_out,
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(total_dur), "-movflags", "+faststart",
            OUT
        ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR: {r.stderr[-500:]}", file=sys.stderr)
        return 1

    print(f"Video rendered: {os.path.getsize(OUT)} bytes")
    return 0

if __name__ == "__main__":
    main()
