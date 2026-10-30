#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send Short metadata to the webhook (n8n workflow trigger)."""
import os, sys, json, urllib.request, random

def main():
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "SOKT_WEBHOOK_URL", "https://flow.sokt.io/func/scri445wtgHf"
    )

    # Read pick data
    with open("pick.txt", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    key, name, start, end = lines[0], lines[1], int(lines[2]), int(lines[3])

    # Read iden.json for nasheed metadata
    iden = json.load(open(f"{key}/iden.json", encoding="utf-8"))
    segments = iden.get("segments", [])
    selected = segments[start-1:end]

    # Raw mp3 link (first segment)
    raw_url = f"https://raw.githubusercontent.com/AmmarBasha2011/Ammar-Records-Two/main/{key}/{start-1:03d}.mp3"

    # Title
    emojis = ["🤲", "💎", "🕊️", "🌙", "🤍", "😮", "💛", "🫶", "🌿", "❤️", "✨", "😊", "🕌", "☀️", "🌤️", "🕯️", "🌸", "🌻", "🌌", "🪴"]
    suffixes = ["هتساعدك تنام الليلة", "لو سمعتها هتفهم ليه بنعيش", "لما الدنيا تِضيق بيك", "بصوت هادي مالوش زي", "حاجة جميلة ليومك", "اللي محدش بيسمعها بتركيز", "خد بريك من اللي بيحصلك", "هتروق أي قلبك", "استمع قبل ما تفوتك", "بداية حلوة لليوم"]
    short_name = f"{random.choice(emojis)} {iden['name']} {random.choice(suffixes)}"

    # Description with segment texts
    seg_texts = "\n".join(f"  • {s['text']}" for s in selected)
    short_description = (
        f"تلاوة مباركة بصوت القارئ عمار الخطيب ✨\n"
        f"📖 {iden['name']} — شطر {start} إلى {end}\n\n"
        f"🔊 الأشطر المختارة:\n{seg_texts}\n\n"
        f"📚 المكتبة الكاملة (77 سورة + أنشيدة): https://github.com/AmmarBasha2011/Ammar-Records-Two\n\n"
        f"🤲 اللهم اجعل القرآن ربيع قلوبنا. شاركه مع من تحب."
    )

    short_tags = ["قرآن", "تلاوة", "عمار_الخطيب", "اسلام", "Shorts", iden["name"].replace(" ", "_"), "قرآن_كريم", "تلاوات", "انشودة"]

    # File size info
    video_size = 0
    video_path = os.path.join("build", "video.mp4")
    if os.path.exists(video_path):
        video_size = os.path.getsize(video_path)

    payload = {
        "link": raw_url,
        "video_url": "",
        "name": short_name,
        "description": short_description,
        "tags": short_tags,
        "nasheed": iden["name"],
        "segment_start": start,
        "segment_end": end,
        "segment_texts": [s["text"] for s in selected],
        "reciter": "عمار الخطيب",
        "video_size_bytes": video_size,
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    print(f"Sending webhook payload to {webhook_url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        status = resp.status
        body = resp.read().decode("utf-8", errors="replace")
        print(f"Webhook response: HTTP {status}")
        print(body[:500])

    if status >= 400:
        print(f"ERROR: webhook returned {status}")
        sys.exit(1)
    print("Webhook delivered ✓")

if __name__ == "__main__":
    main()
