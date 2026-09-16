#!/usr/bin/env python3
"""
run_automation.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/run_automation.py

Runner ตัวเดียวกับที่ `qa-automation-script` (Skill 06a) ใช้รัน `automation/<TC-ID>.py` จริงด้วย
Playwright — ใช้ `--tc TC-xxx TC-yyy` เพื่อรันเฉพาะเคสที่ผ่าน Gate ของขั้นตอนที่ 2-4 ใน SKILL.md
(ไม่ต้องรันทั้ง Feature ซ้ำ) **ห้ามแก้ logic ที่ไฟล์นี้** — ให้ไปแก้ที่
`qa-pipeline-skills/_shared/run_automation.py` ที่เดียวเท่านั้น (เหตุผลเดียวกับ qa_workbook.py)
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "run_automation.py"

if not _SHARED.exists():
    sys.exit(f"[run_automation.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
