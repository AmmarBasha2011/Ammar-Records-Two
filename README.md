# Ammar-Records-Two

> **خط أنابيب محتوى قرآن وأناشيد** — توليد Shorts عمودية (9:16) تلقائياً مع نشر عبر webhook.

---

## 📖 نظرة عامة

هذا الريبو خط أنابيب محتوى متكامل:
1. **تخزين** مقاطع صوتية (آيات قرآنية + أشطر أناشيد) في مجلدات مرقمة
2. **بيانات وصفية** لكل مجلد عبر `iden.json` (النوع، الاسم، المقاطع، الأوقات)
3. **بناء** Shorts عمودية (1080×1920) من نطاقات مقاطع عشوائية
4. **نشر** تلقائي عبر webhook (n8n/sokt.io) — بدون YouTube OAuth
5. **رفع** الفيديو إلى GitHub Release (`latest-short`) للتحميل لاحقاً

---

## 📁 هيكل الريبو

```
Ammar-Records-Two/
├── .github/workflows/
│   ├── video-autopost.yml      # كل 30 دقيقة: اختيار مقاطع → بناء Short → webhook
│   ├── video-cleanup.yml       # 5 دقائق بعد النشر: تنظيف latest-short
│   └── video-reupload.yml      # يومياً 18:15 UTC: إعادة رفع أفضل Short
├── 115/                        # أنشودة: النفس تبكي على الدنيا (13 مقطع)
│   ├── 000.mp3 ... 012.mp3
│   └── iden.json
├── 116/                        # أنشودة: قصيدة ليس الغريب (71 مقطع)
│   ├── 000.mp3 ... 070.mp3
│   └── iden.json
├── assets/backgrounds/         # 14 صورة خلفية (jpg/png/webp)
├── tools/                      # 15 سكربت مساعد
│   ├── quran_split.py          # تقطيع صوت إلى آيات/أشطر
│   ├── recut_ayahs.py          # إعادة تقطيع آيات محددة
│   ├── send_webhook.py         # إرسال metadata + video_url إلى webhook
│   ├── render_video.py         # بناء Short 9:16 من مقاطع + خلفية
│   ├── add_surah.py            # إضافة سورة/أنشودة جديدة
│   ├── pick_best.py            # اختيار أفضل Short لإعادة الرفع
│   ├── verify_repo.py          # التحقق من سلامة الريبو
│   ├── build_site.py           # بناء موقع ثابت (قديم)
│   ├── process_parallel.py     # مساعد معالجة متوازية
│   ├── arabic_norm.py          # تطبيع النص العربي
│   ├── surah_meta.json         # metadata سور
│   ├── manifest.json           # قائمة ملفات
│   ├── quran_text.json         # نص القرآن
│   ├── quran_norm_index.json   # فهرس مطبع
│   └── README.md               # توثيق الأدوات
├── available.json              # metadata الأناشيد/السور disponibles
├── links.json                  # روابط ومعلومات القارئ
└── README.md                   # هذا الملف
```

---

## 🎵 الأناشيد

### 115: النفس تبكي على الدنيا
- **النوع:** اناشيد
- **الأشطر:** 13 مقطع
- **المدة:** ~141 ثانية
- **تم توليده ب:** Groq Whisper large-v3
- **المقاطع:** `115/000.mp3` … `115/012.mp3`
- **البيانات:** `115/iden.json`

### 116: قصيدة ليس الغريب
- **النوع:** اناشيد
- **الأشطر:** 71 مقطع
- **المدة:** ~956 ثانية (15.9 دقيقة)
- **تم توليده ب:** Groq Whisper large-v3
- **المقاطع:** `116/000.mp3` … `116/070.mp3`
- **البيانات:** `116/iden.json`

---

## 🔄 Workflows

### 1. Video Autopost (`video-autopost.yml`)
- **التشغيل:** كل 30 دقيقة (cron) + يدوي
- **الخطوات:**
  1. اختيار 1-6 مقاطع عشوائياً من الأناشيد disponibles
  2. ربط المقاطع صوتياً (ffmpeg concat)
  3. اختيار صورة خلفية عشوائياً
  4. render Short 9:16 (1080×1920, H.264 + AAC)
  5. رفع الفيديو إلى GitHub Release (`latest-short`)
  6. إرسال metadata + video_url إلى webhook (n8n/sokt.io)
- **الناتج:** Short video + webhook payload

### 2. Video Cleanup (`video-cleanup.yml`)
- **التشغيل:** بعد اكتمال Video Autopost
- **الخطوات:** انتظار 5 دقائق → حذف asset `latest-short`

### 3. Video Re-upload (`video-reupload.yml`)
- **التشغيل:** يومياً 18:15 UTC + يدوي
- **الخطوات:** اختيار أفضل Short → إعادة رفع لزيادة الوصول

---

## 🛠️ الأدوات

| الأداة | الغرض |
|--------|-------|
| `quran_split.py` | تقطيع صوت إلى آيات/أشطر (Whisper + forced alignment) |
| `recut_ayahs.py` | إعادة تقطيع آيات محددة حسب النطاق الزمني |
| `send_webhook.py` | إرسال metadata + video_url إلى webhook (n8n) |
| `render_video.py` | بناء Short 9:16 من مقاطع + خلفية |
| `add_surah.py` | إضافة سورة/أنشودة جديدة (مجلد + iden.json) |
| `pick_best.py` | اختيار أفضل Short لإعادة الرفع |
| `verify_repo.py` | التحقق من سلامة الريبو (ملفات، JSON، صوت) |
| `build_site.py` | بناء موقع ثابت (قديم، غير مستخدم) |
| `process_parallel.py` | مساعد معالجة متوازية |
| `arabic_norm.py` | تطبيع النص العربي |
| `surah_meta.json` | metadata سور (من الريبو الأصلي) |
| `manifest.json` | قائمة ملفات |
| `quran_text.json` | نص القرآن |
| `quran_norm_index.json` | فهرس مطبع |
| `README.md` | توثيق الأدوات |

---

## 📋 مخطط iden.json

### للأناشيد (type: "اناشيد"):
```json
{
  "type": "اناشيد",
  "name": "قصيدة ليس الغريب",
  "verses": 71,
  "category": "أنشيدة",
  "generated_by": "groq_whisper",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 11.22,
      "text": "ليس الغريب غريب الشام واليمن"
    }
  ]
}
```

### للقرآن (type: "قرآن"):
```json
{
  "type": "قرآن",
  "surah": "044",
  "name": "الدخان",
  "ayahs": 59,
  "complete": true,
  "recording": "001.mp3",
  "category": "قرآن",
  "generated_by": "auto-split"
}
```


---

## 🚀 إضافة أنشودة جديدة

1. **تحضير ملف صوتي** (mp3/wav)
2. **تفريغ بـ Groq Whisper large-v3** → segments مع أوقات
3. **تقطيع الصوت** بـ `tools/quran_split.py` أو ffmpeg يدوياً:
   ```bash
   ffmpeg -ss START -to END -i input.wav -c:a libmp3lame -q:a 2 output.mp3
   ```
4. **إنشاء مجلد** (مثلاً `117/`)
5. **إنشاء `iden.json`** مع metadata المقاطع
6. **تحديث `available.json`** و `links.json`
7. **Commit + Push**

---

## 📊 خط أنابيب معالجة الصوت

```
ملف صوتي (mp3/wav)
    ↓
Groq Whisper large-v3 (STT)
    ↓
Segments مع أوقات (start, end, text)
    ↓
فلترة الفارغة/no-speech (no_speech_prob > 0.3)
    ↓
تقطيع صوت لكل segment (ffmpeg)
    ↓
حفظ كـ 000.mp3, 001.mp3, ... في مجلد مرقم
    ↓
إنشاء iden.json مع metadata
    ↓
تحديث available.json + links.json
    ↓
Commit + Push
    ↓
Workflow يختار مقاطع عشوائياً → بناء Short → webhook
```

---

## 🔧 اختبار محلي

### اختبار تقطيع:
```bash
cd Ammar-Records-Two
python tools/quran_split.py  # أو ffmpeg يدوياً
```

### اختبار render video:
```bash
# إنشاء pick.txt
echo -e "116\nقصيدة ليس الغريب\n1\n5" > pick.txt
python tools/render_video.py
# الناتج: build/video.mp4
```

### اختبار webhook:
```bash
python tools/send_webhook.py "https://flow.sokt.io/func/scri445wtgHf"
```

---

## 📝 ملاحظات

- **ملفات الصوت** مخزنة مباشرة في الريبو (ليس LFS) للملفات الصغيرة (<50MB لكل ملف)
- **الملفات الكبيرة** (>50MB) يجب استخدام Git LFS
- **المقاطع** مرقمة 000-NNN (0-indexed)
- **الأناشيد** تبدأ من 115 (بعد 114 سورة قرآنية)
- **المقاطع الفارغة/no-speech** يتم فلترتها (no_speech_prob > 0.3)
- **Whisper STT** يقسم "حسب الصمت"، ليس "حسب الشطر" — قد يجمع plusieurs أشطر في segment واحد

---

## 🤝 المساهمة

1. Fork الريبو
2. إضافة أنشودة/سورة جديدة (اتبع خط الأنابيب أعلاه)
3. تحديث `available.json` + `links.json`
4. اختبار محلي
5. Submit PR

---

## 📜 الترخيص

هذا المشروع للاستخدام الشخصي. تلاوات القرآن ملك عام. الأناشيد أعمال أصلية لعمار الخطيب.

---

**آخر تحديث:** 30 أكتوبر 2026
**الريبو:** https://github.com/AmmarBasha2011/Ammar-Records-Two
**القناة:** INEX Team (YouTube)
**القارئ:** عمار الخطيب (Ammar Al-Khateeb)
