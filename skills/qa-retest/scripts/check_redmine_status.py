#!/usr/bin/env python3
"""
check_redmine_status.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/check_redmine_status.py

เหตุผล: ตอนแรกสคริปต์นี้มีอยู่แค่ที่ qa-retest (Skill 10) แต่พอสร้าง qa-retest-closure (Skill 10a) ขึ้นมา
ก็ต้องใช้ตัวเดียวกัน (Skill 10a ใช้คำสั่ง `check` เพื่อกรอง Ticket ที่ปิดไปแล้วออกจาก Scope ก่อนแสดง
Preview — ดู SKILL.md ของ qa-retest-closure ขั้นตอนที่ 2) ถ้าก็อปแยกไว้ 2 ชุดจะเกิดปัญหาเดียวกับที่เคยเจอ
กับ qa_workbook.py และ run_automation.py คือแก้ logic ที่ไฟล์เดียวแล้วลืมอีกไฟล์ ทำให้พฤติกรรมสองฝั่งไม่ตรง
กัน (drift) จึงย้ายไปไว้ที่ _shared/ ที่เดียว ให้ทั้ง 2 Skill เรียกผ่าน stub นี้แทน

**ถ้าต้องแก้ logic (เช่น field ที่ดึงจาก journal, วิธีจับคู่ issue_id) ให้แก้ที่
_shared/check_redmine_status.py เท่านั้น ห้ามแก้ไฟล์ stub นี้**

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/check_redmine_status.py):
  python3 scripts/check_redmine_status.py check --tc-issue-map "<path>.json" --resolved-statuses "Resolved,Fixed" --out "<result>.json"
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "check_redmine_status.py"

if not _SHARED.exists():
    sys.exit(f"[check_redmine_status.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
