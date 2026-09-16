#!/usr/bin/env python3
"""
send_email_notification.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/send_email_notification.py

เหตุผล: ตอนแรกสคริปต์นี้มีอยู่แค่ที่ redmine-logging (Skill 09) แต่พอสร้าง qa-retest-closure (Skill 10a)
ขึ้นมา ก็ต้องใช้กลไก SMTP เดียวกัน (คำสั่ง `print-success`/`send` ใช้ร่วมกันตรงๆ ส่วน `build-body` ของ 09
กับ `build-retest-failed-body` ของ 10a เป็นคนละ Format กัน) ถ้าก็อปแยกไว้ 2 ชุดจะเกิดปัญหาเดียวกับที่เคยเจอ
กับ qa_workbook.py และ run_automation.py คือแก้ logic ที่ไฟล์เดียวแล้วลืมอีกไฟล์ จึงย้ายไปไว้ที่ _shared/
ที่เดียว ให้ทั้ง 2 Skill เรียกผ่าน stub นี้แทน

**ถ้าต้องแก้ logic ให้แก้ที่ _shared/send_email_notification.py เท่านั้น ห้ามแก้ไฟล์ stub นี้**

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/send_email_notification.py):
  python3 scripts/send_email_notification.py print-success --result-json "<result>.json"
  python3 scripts/send_email_notification.py build-body --cases-json "<path>.json" --result-json "<result>.json" --run-date "<date>" --environment "<env>" --out "<body>.txt"
  python3 scripts/send_email_notification.py send --to "<email>" --subject "<subject>" --body-file "<body>.txt"
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "send_email_notification.py"

if not _SHARED.exists():
    sys.exit(f"[send_email_notification.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
