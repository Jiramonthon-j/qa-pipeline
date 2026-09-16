#!/usr/bin/env python3
"""
qa_workbook.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/qa_workbook.py

Skill นี้ (redmine-logging) ใช้ไฟล์จริงตัวเดียวกันนี้ร่วมกับอีก 5 Skill ในสาย (test-case-generator,
qa-automation-script, coverage-review, test-data-generator, risk-analysis) — ดูเหตุผลเต็มที่
_shared/qa_workbook.py

**ไฟล์นี้ไม่มี logic ของตัวเองเลย ห้ามแก้ logic ที่ไฟล์นี้** — ให้ไปแก้ที่
`qa-pipeline-skills/_shared/qa_workbook.py` ที่เดียวเท่านั้น

คำสั่งใช้งานเหมือนเดิมทุกอย่าง (ดู docstring เต็มที่ _shared/qa_workbook.py):
  python3 scripts/qa_workbook.py read-cases --path "<path>.xlsx"
  python3 scripts/qa_workbook.py update-fields-batch --path "<path>.xlsx" --updates-json "<path>.json" --editor "<ชื่อ skill>" --note "<...>"
  python3 scripts/qa_workbook.py finalize-layout --path "<path>.xlsx"
"""
import runpy
import sys
from pathlib import Path

# qa-pipeline-skills/<skill-name>/scripts/qa_workbook.py -> parents[2] = qa-pipeline-skills/
_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "qa_workbook.py"

if not _SHARED.exists():
    sys.exit(
        f"[qa_workbook.py stub] ไม่พบฉบับจริงที่ {_SHARED} — ไฟล์นี้เป็นแค่ตัวโหลดไปรันฉบับจริง "
        f"ไม่มี logic อยู่ในตัวเอง ตรวจสอบว่าโฟลเดอร์ qa-pipeline-skills/_shared/ ยังอยู่ครบและอยู่ในตำแหน่งที่ถูกต้อง"
    )

runpy.run_path(str(_SHARED), run_name="__main__")
