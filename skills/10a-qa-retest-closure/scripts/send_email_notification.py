#!/usr/bin/env python3
"""
send_email_notification.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/send_email_notification.py

Skill นี้ (qa-retest-closure / Skill 10a) ใช้คำสั่ง `build-retest-failed-body` (Format "RETEST FAILED
REPORT" — คนละ Format กับ `build-body` ของ redmine-logging (09)) แล้วใช้ `send` ตัวเดียวกันส่งอีเมลจริง

**ถ้าต้องแก้ logic ให้แก้ที่ _shared/send_email_notification.py เท่านั้น ห้ามแก้ไฟล์ stub นี้**

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/send_email_notification.py):
  python3 scripts/send_email_notification.py print-success --result-json "<result>.json"
  python3 scripts/send_email_notification.py build-retest-failed-body --cases-json "<path>.json" --result-json "<result>.json" --run-date "<date>" --environment "<env>" --out "<body>.txt"
  python3 scripts/send_email_notification.py send --to "<email>" --subject "<subject>" --body-file "<body>.txt"
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "send_email_notification.py"

if not _SHARED.exists():
    sys.exit(f"[send_email_notification.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
