#!/usr/bin/env python3
"""
qa_workbook.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/qa_workbook.py

เดิมไฟล์นี้เป็นสำเนาโค้ดเต็มของตัวเอง แยกไว้ต่างหากซ้ำกันใน 5 Skill (test-case-generator,
qa-automation-script, coverage-review, test-data-generator, risk-analysis) — เคยทำให้เกิดบั๊กจริง
มาแล้วครั้งหนึ่ง: แก้ไข Document Control ที่สำเนาเดียว แล้วอีก 4 สำเนาไม่ได้ sync ตาม ทำให้บั๊กเดิม
กลับมาแบบเงียบๆ ตอน Skill อื่นเรียกใช้สำเนาเก่าที่ยังไม่ได้แก้ — รวมเป็นฉบับเดียวไว้ที่ _shared/ แล้ว
เพื่อไม่ให้เกิดปัญหานี้ซ้ำอีก

**ไฟล์นี้ไม่มี logic ของตัวเองแล้ว ห้ามแก้ logic ที่ไฟล์นี้** — ให้ไปแก้ที่
`qa-pipeline-skills/_shared/qa_workbook.py` ที่เดียวเท่านั้น ทุก Skill จะเห็นผลตรงกันทันทีโดย
อัตโนมัติ ไม่ต้อง sync มือหลายที่อีกต่อไป

คำสั่งใช้งานเหมือนเดิมทุกอย่าง ไม่มีอะไรเปลี่ยนจากมุมมองของคนเรียกใช้ (ดู docstring เต็มที่
_shared/qa_workbook.py):
  python3 scripts/qa_workbook.py create --feature "<ชื่อ Feature>" --out "<path>.xlsx"
  python3 scripts/qa_workbook.py add-cases --path "<path>.xlsx" --cases-json "<path>.json" --editor "<ชื่อ skill>" --note "<...>"
  python3 scripts/qa_workbook.py bump --path "<path>.xlsx" --editor "<ชื่อ skill>" --note "<...>"
  python3 scripts/qa_workbook.py read-cases --path "<path>.xlsx"
  python3 scripts/qa_workbook.py update-field --path "<path>.xlsx" --tc-id "TC-001" --field "Priority" --value "P0" --editor "<ชื่อ skill>" --note "<...>"
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

# รันไฟล์จริงในโหมด __main__ เหมือนถูกเรียกตรงๆ — ใช้ sys.argv ของโปรเซสปัจจุบัน ทำให้ argparse/CLI
# ของฉบับจริงทำงานเหมือนเดิมทุกประการ ไม่ต้องมี logic เพิ่มเติมที่นี่
runpy.run_path(str(_SHARED), run_name="__main__")
