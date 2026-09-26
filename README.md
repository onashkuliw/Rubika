# یار رسانه — ربات روبیکا کلاس دهم

پروژه عمداً بدون فولدر و ساب‌فولدر ساخته شده است.

## فایل‌ها

- `main.py` هسته ربات
- `database.py` دیتابیس SQLite
- `config.py` تنظیمات
- `questions.py` سؤال‌های اولیه
- `requirements.txt` وابستگی
- `Procfile` اجرای Railway
- `railway.json` تنظیم Railway
- `.gitignore` فایل‌های محرمانه/دیتابیس

## Environment Variables در Railway

```text
BOT_TOKEN=توکن ربات روبیکا
ADMIN_ID=آیدی روبیکای مالک
DATABASE_PATH=/data/bot.db
DEFAULT_SCORE=3
BOT_NAME=یار رسانه
```

برای ماندگاری SQLite، در Railway یک Volume بساز و آن را روی `/data` mount کن.

## ثبت دانش‌آموز

```text
/addstudent USER_ID NAME
```

مثال:

```text
/addstudent u123456 علی رضایی
```

## انتخاب درس فعال

```text
/setlesson 2 5
```

## سؤال

در گروه:

```text
سوال
سوال 1
امتیاز من
جدول
ربات
```

یا:

```text
/question
/question 1
/score
/leaderboard
```

## افزودن سؤال

```text
/addq CHAPTER LESSON SCORE PAGE CORRECT | QUESTION | A | B | C | D | EXPLANATION
```

مثال:

```text
/addq 1 2 3 19 a | متن در پیام رسانه‌ای به چه بخشی نزدیک‌تر است؟ | بخش آشکار پیام | نظر مخاطب | تبلیغ | دستگاه پخش | متن بخش آشکار پیام است.
```

## نکته

سؤال‌های داخل `questions.py` تألیفی‌اند و متن کتاب را عیناً بازنشر نمی‌کنند. برای تولید بانک کامل‌تر، سؤال‌های بیشتری را می‌توان از محتوای کتاب استخراج و به همین ساختار اضافه کرد.
