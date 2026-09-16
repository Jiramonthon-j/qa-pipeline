#!/usr/bin/env python3
"""
qa_workbook.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/qa_workbook.py

**ไฟล์นี้ไม่มี logic ของตัวเองแล้ว ห้ามแก้ logic ที่ไฟล์นี้** — ให้ไปแก้ที่
`qa-pipeline-skills/_shared/qa_workbook.py` ที่เดียวเท่านั้น (เหตุผลเดียวกับอีก 6 Skill ในสายที่ใช้ stub
แบบนี้อยู่แล้ว — กันปัญหาแก้ไฟล์เดียวแล้วอีกหลายสำเนาไม่ sync ตาม)

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/qa_workbook.py):
  python3 scripts/qa_workbook.py read-cases --path "<path>.xlsx"
  python3 scripts/qa_workbook.py update-fields-batch --path "<path>.xlsx" --updates-json "<path>.json" --editor "<ชื่อ skill>" --note "<...>"
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "qa_workbook.py"

if not _SHARED.exists():
    sys.exit(f"[qa_workbook.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
