#!/usr/bin/env python3
"""
check_redmine_status.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/check_redmine_status.py

Skill นี้ (qa-retest-closure / Skill 10a) ใช้คำสั่ง `check` ของสคริปต์นี้เพื่อกรอง Ticket ที่ปิดไปแล้ว
ออกจาก Scope ก่อนแสดง Preview ให้ผู้ใช้ Recheck (ดู SKILL.md ขั้นตอนที่ 2) — เป็นสคริปต์ตัวเดียวกับที่
qa-retest (Skill 10) ใช้เช็คว่า Dev แจ้งแก้เสร็จหรือยัง ต่างกันแค่ `--resolved-statuses` ที่ส่งเข้าไป
(Skill 10 ส่งชื่อ Status ที่แปลว่า "แก้เสร็จแล้ว" / Skill 10a ส่งชื่อ Status ที่แปลว่า "ปิดแล้ว")

**ถ้าต้องแก้ logic ให้แก้ที่ _shared/check_redmine_status.py เท่านั้น ห้ามแก้ไฟล์ stub นี้**

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/check_redmine_status.py):
  python3 scripts/check_redmine_status.py check --tc-issue-map "<path>.json" --resolved-statuses "Closed,Resolved" --out "<result>.json"
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "check_redmine_status.py"

if not _SHARED.exists():
    sys.exit(f"[check_redmine_status.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
