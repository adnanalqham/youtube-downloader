# برنامج تنزيل فيديوهات يوتيوب

تطبيق سطح مكتب لنظام Windows لتنزيل الفيديوهات باستخدام Python وCustomTkinter وyt-dlp.

## ✨ المميزات

- واجهة رسومية سهلة الاستخدام.
- فحص رابط الفيديو وعرض معلوماته.
- عرض دقات الفيديو التي تم اكتشافها.
- عرض حجم الملف التقريبي عند توفر المعلومات.
- متابعة تقدم التنزيل والسرعة والوقت المتبقي.
- اختيار مجلد حفظ الفيديوهات.
- دعم FFmpeg لدمج الفيديو والصوت عند الحاجة.

## 🧰 التقنيات المستخدمة

- **Python** — لغة البرمجة الأساسية.
- **CustomTkinter** — إنشاء الواجهة الرسومية.
- **yt-dlp** — استخراج معلومات الفيديو وتنزيله.
- **FFmpeg** — دمج ومعالجة ملفات الفيديو والصوت.
- **PyInstaller** — إنشاء نسخة تنفيذية لنظام Windows.

## 📋 المتطلبات

- Windows 10 أو Windows 11.
- Python 3.12 أو أحدث.
- FFmpeg.
- اتصال بالإنترنت.

## 🚀 التثبيت والتشغيل من المصدر

### 1. تنزيل المشروع

```powershell
git clone https://github.com/adnanalqham/youtube-downloader.git
cd youtube-downloader
```

### 2. إنشاء بيئة افتراضية

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. تثبيت المكتبات

```powershell
python -m pip install -r requirements.txt
```

### 4. إعداد FFmpeg

ضع الملفين `ffmpeg.exe` و`ffprobe.exe` داخل مجلد المشروع في المسار التالي:

```text
ffmpeg/bin/
```

### 5. تشغيل الواجهة الرسومية

```powershell
python app.py
```

لتشغيل واجهة Terminal:

```powershell
python downloader.py
```

## 📦 إنشاء نسخة تنفيذية EXE

ثبّت PyInstaller:

```powershell
python -m pip install pyinstaller
```

ثم نفّذ أمر البناء من مجلد المشروع:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onedir --name YouTubeDownloader --add-data "ffmpeg;ffmpeg" app.py
```

ستجد ملفات التطبيق الناتجة داخل:

```text
dist/YouTubeDownloader/
```

احتفظ بمجلد التطبيق كاملًا، بما فيه الملفات التابعة له. اختبر النسخة التنفيذية على الجهاز المستهدف قبل توزيعها.

## 📥 طريقة الاستخدام

1. افتح التطبيق.
2. الصق رابط الفيديو.
3. اضغط **Check Video** لفحص الفيديو والدقات المتاحة.
4. اختر الدقة المطلوبة من القائمة.
5. راجع حجم الملف التقريبي إذا كان متاحًا.
6. اختر مجلد الحفظ باستخدام **Browse** أو اترك مجلد التنزيلات الافتراضي.
7. اضغط **Download Video** وانتظر اكتمال التنزيل.

## ℹ️ ملاحظات

- قد يكون حجم الملف المعروض تقديريًا أو غير متاح لبعض الصيغ.
- الدقات والصيغ المتاحة تختلف من فيديو لآخر.
- قد يحتاج yt-dlp إلى تحديث عند تغيّر آلية عمل يوتيوب.
- يحتاج التطبيق إلى FFmpeg في المسار المتوقع لدمج الصوت والفيديو عند الضرورة.

## ⚖️ الاستخدام المسؤول

استخدم البرنامج لتنزيل المحتوى الذي تملكه أو لديك إذن بتنزيله فقط، والتزم بالقوانين المعمول بها وشروط خدمة يوتيوب.

## 🔗 المستودع

[adnanalqham/youtube-downloader](https://github.com/adnanalqham/youtube-downloader)
