#!/usr/bin/env python3
"""
run_automation.py — stub ที่ชี้ไปยังฉบับจริงเดียว (single source of truth) ที่
qa-pipeline-skills/_shared/run_automation.py

เหตุผล: ตอนแรก run_automation.py มีอยู่แค่ที่ qa-automation-script (Skill 06a) แต่พอสร้าง qa-retest
(Skill 10) ขึ้นมา ก็ต้องใช้ runner ตัวเดียวกัน (รัน automation/<TC-ID>.py ทีละไฟล์ด้วย Playwright จริง
เหมือนกันเป๊ะ ต่างแค่ --tc filter) ถ้าก็อปโค้ดแยกไว้ 2 ชุดจะเกิดปัญหาเดียวกับที่เคยเจอกับ qa_workbook.py
คือแก้ logic ที่ไฟล์เดียวแล้วลืมอีกไฟล์ ทำให้พฤติกรรมสองฝั่งไม่ตรงกัน (drift) จึงย้ายไปไว้ที่ _shared/
ที่เดียว ให้ทั้ง 2 Skill เรียกผ่าน stub นี้แทน

**ถ้าต้องแก้ logic ของ runner (เช่น วิธีถ่ายภาพ, วิธี assert, การจัดการ Accessibility scan) ให้แก้ที่
_shared/run_automation.py เท่านั้น ห้ามแก้ไฟล์ stub นี้** (stub มีหน้าที่แค่ส่งต่อการรันเฉยๆ)
"""
import runpy
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared" / "run_automation.py"

if not _SHARED.exists():
    sys.exit(f"[run_automation.py stub] ไม่พบฉบับจริงที่ {_SHARED} — เช็คว่าโฟลเดอร์ _shared/ ยังอยู่ครบไหม")

runpy.run_path(str(_SHARED), run_name="__main__")
