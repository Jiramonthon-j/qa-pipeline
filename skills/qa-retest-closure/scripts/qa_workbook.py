#!/usr/bin/env python3
"""
qa_workbook.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/qa_workbook.py

**ไฟล์นี้ไม่มี logic ของตัวเองแล้ว ห้ามแก้ logic ที่ไฟล์นี้** — ให้ไปแก้ที่
`qa-pipeline-skills/_shared/qa_workbook.py` ที่เดียวเท่านั้น (เหตุผลเดียวกับอีกหลาย Skill ในสายที่ใช้ stub
แบบนี้อยู่แล้ว — กันปัญหาแก้ไฟล์เดียวแล้วอีกหลายสำเนาไม่ sync ตาม)

Skill นี้ (qa-retest-closure / Skill 10a) ใช้แค่คำสั่ง `read-cases` เพื่ออ่าน Workbook สดๆ มาเตรียม
cases-json — **ไม่มีขั้นตอนไหนที่ต้องเขียนกลับ Workbook เลย** (ไม่แตะคอลัมน์ Issue link หรือ Status ใดๆ
เพราะ Skill 10 เขียนผลไปแล้ว และ Skill 10a แค่จัดการฝั่ง Redmine เท่านั้น) แต่เก็บ stub นี้ไว้เผื่ออนาคต
ต้องใช้คำสั่งอื่นของ qa_workbook.py เพิ่ม

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/qa_workbook.py):
  python3 scripts/qa_workbook.py read-cases --path "<path>.xlsx"
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "qa_workbook.py"

if not _SHARED.exists():
    sys.exit(f"[qa_workbook.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
