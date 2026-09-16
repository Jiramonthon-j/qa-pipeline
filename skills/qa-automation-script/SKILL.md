---
name: qa-automation-script
description: เขียนและ**รัน** Test Automation Script จริงด้วย Playwright ให้ 1 Feature ตาม Test Case ที่ผ่าน risk-analysis และ Test Data ที่เตรียมไว้ พร้อมสแกน Accessibility คู่กันทุกหน้า แล้วอัปเดตผล Pass/Fail/Blocked กลับเข้า Test Case Workbook จริง เป็น Skill 06a ที่บังคับของ QA Pipeline นี้ ให้ใช้ Skill นี้ทันทีเมื่อผู้ใช้พูดถึงการรัน Test อัตโนมัติ, Automation Script, Playwright, หรือการทดสอบจริงของ Feature หนึ่งๆ แม้จะไม่ได้เอ่ยชื่อ Skill ตรงๆ
---

# qa-automation-script

Skill นี้เป็น**ขั้นตอนที่ 6a ที่บังคับ** ของ QA Pipeline และเป็นขั้นตอนแรกในสายที่**ทดสอบจริง** (ไม่ใช่แค่ออกแบบ/เตรียมข้อมูลเหมือน Skill ก่อนหน้า) หน้าที่คือเขียน Playwright Script ตาม Test Case แต่ละรายการ รันจริงกับ Environment ที่ระบุไว้ใน Env & Config สแกน Accessibility คู่กันทุกหน้า แล้วอัปเดตผลกลับเข้า Test Case Workbook

**สำคัญ**: คำสั่งในไฟล์นี้เขียนขึ้นให้ใช้ได้กับทั้ง Claude และ Gemini 3.6 ก็จริง แต่ Skill นี้ต้องการ environment ที่รันโค้ด Python ได้จริง (ทั้งรัน Playwright browser และรันสคริปต์แก้ Workbook) — เป็น Skill ที่พึ่งพา code execution มากที่สุดในสาย Pipeline ถ้า environment ที่ใช้งานอยู่รันโค้ดไม่ได้ ให้เตรียม Script เป็นไฟล์ไว้ก่อนแล้วแจ้งผู้ใช้ว่าต้องไปรันในเครื่อง/environment ที่มี Python + Playwright ติดตั้งอยู่

## ขั้นตอนที่ 1 — ระบุ Feature และตรวจสอบขั้นตอนก่อนหน้า

1. หาโฟลเดอร์รากของโปรเจค (Project Root) และโฟลเดอร์ Feature เหมือน Skill อื่นๆ ในสาย
2. อ่านไฟล์ `_pipeline-manifest.md` ของ Feature นั้น
3. **เช็ค Gate**: Skill นี้ต้องรันต่อจาก `test-data-generator` (Skill 06) เสมอ — ตรวจสอบสถานะ Stage `06 test-data-generator` (ถ้าไม่มี manifest เลยก็ถือว่ายังไม่เสร็จเช่นกัน — ต้องถามผู้ใช้เสมอ ห้ามสรุปเอาเอง):
   - **ถ้า `Complete`**: ไปต่อขั้นตอนที่ 2
   - **ถ้ายังไม่ `Complete`**: หยุดและถามผู้ใช้ว่า (a) ต้องการไปรัน `test-data-generator` ให้เสร็จก่อนไหม (แนะนำ) หรือ (b) ต้องการใช้ Skill นี้แบบ standalone — ถ้าเลือก (b) ให้ขอ Test Case Workbook และ Mock Data ที่มีอยู่แล้วมาจากผู้ใช้โดยตรง
4. อ่านชีต "Env & Config" ในไฟล์เดียวกัน เพื่อรู้ URL, Account, Browser/Device ที่ต้องเทส

## ขั้นตอนที่ 2 — เตรียม environment สำหรับรัน

1. ตรวจสอบว่ามี Python, Playwright (พร้อม browser ที่ต้องใช้), และ `axe-playwright-python` (สำหรับ Accessibility scan) ติดตั้งพร้อมใช้งานหรือยัง ถ้ายังให้ติดตั้งก่อน
2. อ่าน Test Case Workbook **ฉบับล่าสุดจริงๆ** ด้วย `python3 scripts/qa_workbook.py read-cases --path "<path>"` และอ่านไฟล์ `06-test-data.md` (**หมายเหตุโครงสร้าง**: `scripts/qa_workbook.py` ของ Skill นี้เป็น stub ที่โหลดฉบับจริงจาก `qa-pipeline-skills/_shared/qa_workbook.py` มาใช้ร่วมกับอีก 4 Skill ในสาย — ถ้าต้องแก้ logic ให้แก้ที่ `_shared/` ที่เดียว ห้ามแก้ stub นี้)
3. ถามผู้ใช้ว่าต้องการรันทุก Test Case หรือเลือกเฉพาะบางรายการ (เช่น เฉพาะที่ยัง `not start`, หรือเฉพาะ Priority P0/P1 ก่อน)

## ขั้นตอนที่ 3 — เขียน Playwright Script (1 ไฟล์ต่อ 1 Test Case)

**หลักการจัดระเบียบไฟล์ — CONFIRMED**: เขียน Script แยกเป็น**1 ไฟล์ต่อ 1 Test Case** เก็บไว้ที่ `<โฟลเดอร์ Feature>/automation/<Test Case ID>.py` (เช่น `automation/TC-001.py`) เหตุผล: ทำให้ `qa-retest` (Skill 10) รันซ้ำเฉพาะเคสที่ Fail ได้ง่ายๆ โดยเรียกไฟล์เดียว และการทำ Regression (รันทุกเคสของ Feature) ก็ทำได้ง่ายด้วยการรันทุกไฟล์ในโฟลเดอร์ — ไม่ต้องพึ่ง orchestration พิเศษ

**หมายเหตุโครงสร้าง**: `scripts/run_automation.py` ของ Skill นี้เป็น stub ที่โหลดฉบับจริงจาก `qa-pipeline-skills/_shared/run_automation.py` มาใช้ร่วมกับ `qa-retest` (Skill 10) ซึ่งต้องใช้ runner ตัวเดียวกันเป๊ะๆ (ต่างแค่ `--tc` filter) — ถ้าต้องแก้ logic ของ runner ให้แก้ที่ `_shared/` ที่เดียว ห้ามแก้ stub นี้ (เหตุผลเดียวกับ `qa_workbook.py` ที่รวมไว้ก่อนหน้านี้)

แต่ละไฟล์ต้อง export ฟังก์ชัน `run(page)` ที่รับ Playwright `page` object แล้ว:
1. ทำตาม Test Step ของ Test Case นั้น (ใช้ Test Data จาก `06-test-data.md` — ถ้าเป็นค่า Dynamic ต้องเขียนโค้ดดึงค่าจริงตามที่ระบุไว้ ไม่ hardcode)
2. Assert ผลลัพธ์เทียบกับ Expected Result — ถ้าไม่ตรง ให้ raise `AssertionError` พร้อมข้อความอธิบายจุดที่ผิด (ถือเป็น **Test Case Fail จริง**) **ถ้ามี element ที่ชี้จุดผิดได้ชัดเจน (เช่น ข้อความ error ที่ผิด, ปุ่ม/ฟิลด์ที่พฤติกรรมไม่ตรง) ให้ raise เป็น `AssertionError(ข้อความ, selector)` (2 argument)** เพื่อให้ runner ยังวาดวงกลมไฮไลท์รอบจุดนั้นได้แม้ Test Case จะ Fail (ไม่ใส่ selector ก็ได้ถ้าไม่มีจุดเดียวที่ชี้ชัด — แค่จะไม่มีวงไฮไลท์ในภาพ)
   - **ถ้า Test Case หนึ่งต้องตรวจหลายกรณีย่อยที่เปลี่ยนสถานะหน้าเว็บระหว่างทาง** (เช่น ทดสอบ boundary หลายค่าในสคริปต์เดียว โดยมีการ reload/navigate คั่นระหว่างกรณี) **ให้ raise ทันทีหลังตรวจพบความผิดพลาดของกรณีนั้นๆ (fail-fast) ห้ามเก็บผลไว้เช็ครวมตอนท้าย** เพราะ runner จะถ่ายภาพหน้าจอ ณ ตอน raise เท่านั้น — ถ้า raise ตอนท้ายหลังเปลี่ยนหน้าไปทดสอบกรณีถัดไปแล้ว ภาพหลักฐานจะกลายเป็นภาพของกรณีที่ไม่เกี่ยวข้อง ไม่ใช่ภาพของกรณีที่ Fail จริง (พบบั๊กนี้จริงระหว่างทดสอบ Skill — ดู BUG-10 ใน Test Report)
3. ถ้าผ่านทุก Assert ให้ return `dict` ที่มี key อย่างน้อย: `passed: bool` (ควรเป็น `True` เสมอในกรณีนี้เพราะยังไม่ raise), `highlight_selector: str | None` (selector ของ element ที่ควรวงล้อมไฮไลท์ในภาพตอน Pass)

**แยกแยะ Error 2 ประเภทให้ชัดเจนเสมอ (สำคัญมาก)**:
- **Test Case Fail จริง** (บั๊กจริง): เกิดจาก `AssertionError` ที่โค้ดจงใจ raise เพราะพฤติกรรมจริงของระบบไม่ตรงกับ Expected Result — ตั้ง Status เป็น `Fail`
- **Script/Environment Error** (ไม่ใช่บั๊ก แค่รันไม่สำเร็จ): เกิดจาก exception ประเภทอื่น เช่น หา element ไม่เจอ (selector ผิด/หน้าเปลี่ยนไป), timeout, เชื่อมต่อ environment ไม่ได้ — ตั้ง Status เป็น **`Blocked`** (ค่าใหม่ที่เพิ่มเข้า Schema ของ Skill 03 ตอนสร้าง Skill นี้ — ดูหมายเหตุท้ายไฟล์) **ห้ามตั้งเป็น `Fail`** เพราะจะทำให้ข้อมูลบั๊กที่ส่งต่อไป `redmine-logging` (09) ผิดเพี้ยน (เปิด Ticket แจ้ง Dev ทั้งที่ไม่ใช่บั๊กจริง)

## ขั้นตอนที่ 4 — รัน Script จริงและเก็บภาพ

ใช้ runner กลาง (เขียนเป็นสคริปต์แยกได้ เช่น `scripts/run_automation.py` ที่ import ทีละไฟล์ `automation/<TC ID>.py` มารันด้วย Playwright จริง) โดยทำตามลำดับนี้สำหรับทุก Test Case ที่จะรัน และ**ทำซ้ำสำหรับทุก Browser ที่ระบุไว้ใน Env & Config** (ไม่จำกัดแค่ Browser เดียว):

1. เปิด Browser/Context ใหม่ตาม Browser ที่กำลังทดสอบ
2. เรียก `run(page)` ของ Test Case นั้น
3. **ถ่ายภาพหน้าจอเก็บไว้เสมอ ไม่ว่าผลจะเป็นอะไร** (Pass/Fail/Blocked) ที่โฟลเดอร์ `<โฟลเดอร์ Feature>/screenshots/<Browser>/<Test Case ID>.png`
4. ถ้ามี `highlight_selector` ให้วาดวงกลม/กรอบไฮไลท์รอบ element นั้นบนภาพที่ถ่ายไว้ (ใช้พิกัด bounding box ของ element จาก Playwright แล้ววาดด้วยไลบรารีประมวลผลภาพ เช่น Pillow) — ใช้สีต่างกันชัดเจนระหว่างจุดที่ Pass (เช่น เขียว) กับจุดที่ Fail (เช่น แดง)
5. **รัน Accessibility scan (axe-core) บนหน้าปัจจุบันทันทีหลัง Assert เสร็จ** — แทรกคู่ไปกับ flow เดิม ไม่ต้องเปิด session แยก axe-core แต่ละ violation จะมีระดับ `impact` กำกับมาด้วยเสมอ (`critical` / `serious` / `moderate` / `minor`) **ต้องดูระดับนี้ก่อนตัดสินใจ**:
   - **`critical` หรือ `serious`** (เช่น รูปไม่มี alt text, contrast ต่ำมาก, ใช้ keyboard ไม่ได้เลย) ถือว่ากระทบผู้ใช้จริงเทียบเท่าบั๊ก functional — ถ้า Test Case เดิม Pass อยู่แล้วแต่เจอปัญหาระดับนี้ ให้เปลี่ยนผลเป็น `Fail` พร้อมระบุรายละเอียดไว้ใน Remarks (ห้ามละเลยแค่เพราะ functional ผ่านแล้ว)
   - **`moderate` หรือ `minor`** (เช่น ไม่มี landmark `<main>`, โครงสร้างหน้าที่ไม่เป็นไปตาม best practice แต่ไม่ได้กันผู้ใช้จากการทำงาน) **ห้ามเปลี่ยนผลจาก Pass เป็น Fail** — ให้บันทึกไว้ใน Remarks เป็นข้อสังเกตเสริม (เช่น "พบข้อสังเกต Accessibility ระดับ moderate: ...") เพื่อให้ `result-analysis` เห็นไว้ แต่ไม่กระทบ Status
   - เหตุผลของกฎนี้: หน้าเว็บทั่วไปแทบทุกหน้ามักมี finding ระดับ moderate/minor ติดมาเสมอ (เช่น landmark, region) แม้ไม่มีบั๊กอะไรเกี่ยวกับ Test Case นั้นเลย ถ้าไม่กรองระดับ impact จะทำให้แทบทุก Test Case ถูกเปลี่ยนเป็น Fail โดยไม่สื่อความหมาย สัญญาณจริงจะจมไปกับ noise (พบจริงระหว่างทดสอบ Skill นี้ — ดู BUG-09 ใน Test Report)
6. เก็บผลลัพธ์ (`Status`, `Actual Result`, `Remarks`, path ของภาพ) ไว้รวมกันเป็นรายการ ยังไม่ต้องเขียนกลับ Workbook ทีละรายการ

## ขั้นตอนที่ 5 — เขียนผลกลับ Workbook และบันทึกไฟล์รูป

1. **ห้ามอัปเดต Workbook ทีละ Test Case** (จะทำให้ Document Control History ท่วมเหมือน BUG-08 ที่เคยพบตอนสร้าง Skill 05) ให้รวบรวมผลของ**ทุก Test Case ที่รันในรอบนี้**เป็นไฟล์ JSON เดียว แล้วอัปเดตครั้งเดียวด้วย `python3 scripts/qa_workbook.py update-fields-batch --path "<path>" --updates-json "<path .json>" --editor "qa-automation-script" --note "รัน Automation Script รอบนี้ <จำนวน> เคส (Pass=.. Fail=.. Blocked=..)"` — ต้องอัปเดตทั้ง `Status`, `Actual Result`, `Test Data`, และ `Remarks` (ถ้ามี) ของแต่ละ Test Case ในไฟล์ JSON เดียวกัน (ทำได้ในคำสั่งเดียวเพราะ `update-fields-batch` รับหลาย field/หลาย Test Case พร้อมกัน)
2. **กฎรวมผลข้าม Browser เป็น 1 Status ต่อ 1 Test Case (CONFIRMED)**: Workbook มีคอลัมน์ `Status` เดียวต่อ Test Case แต่ขั้นตอนที่ 4 รันซ้ำทุก Browser ที่ระบุใน Env & Config — ต้องสรุปผลทุก Browser ของ Test Case เดียวกันให้เหลือ Status เดียวตามลำดับความสำคัญนี้เสมอ (Fail > Blocked > Pass):
   - **Fail** ถ้ามีอย่างน้อย 1 Browser ที่ผลเป็น Fail (ต่อให้ Browser อื่น Pass ก็ตาม — บั๊กที่เจอใน Browser เดียวก็ถือว่าเป็นบั๊กจริงที่ต้องแจ้ง Dev)
   - **Blocked** ถ้าไม่มี Browser ไหน Fail แต่มีอย่างน้อย 1 Browser ที่ผลเป็น Blocked
   - **Pass** ก็ต่อเมื่อ**ทุก Browser** ที่ทดสอบผลเป็น Pass ทั้งหมด
   - **คอลัมน์ Actual Result**: ถ้าทุก Browser ให้ผลตรงกัน ใส่ข้อความเดียวได้ตามปกติ แต่ถ้าผลต่างกันข้าม Browser (เช่น Fail เฉพาะ Firefox) ต้องระบุชื่อ Browser กำกับให้ชัดเจนว่าใครเจออะไร เช่น `[Chromium] Pass — ทำงานถูกต้อง / [Firefox] Fail — ปุ่มกดไม่ได้เพราะ... ` เพื่อให้อ่านแล้วรู้ทันทีว่าเจอปัญหาที่ Browser ไหน (ข้อมูลนี้จะถูกใช้ต่อโดย `redmine-logging` (09) ตอนเขียน Description ของ Ticket และโดย `qa-retest-closure` (10a) ตอนสรุปสาเหตุที่ยังไม่ผ่านให้ Dev ด้วย)
   - **คอลัมน์ Test Photo**: ถ้า Fail มากกว่า 1 Browser ให้ใส่ path ของทุก Browser ที่ Fail คั่นด้วย `;` เช่น `screenshots/Chromium/TC-017.png; screenshots/Firefox/TC-017.png` ไม่ใช่แค่ Browser แรกที่เจอ
3. **คอลัมน์ Execution Date**: ใส่วันที่รันจริงด้วยในชุดอัปเดตเดียวกัน
4. **คอลัมน์ Test Data — อัปเดตเป็นค่าจริงที่ใช้ทดสอบรอบนี้เสมอ (ไม่ใช่แค่คำอธิบายเดิมจาก Skill 03)**: หลังรันเสร็จ ให้แทนที่ข้อความคำอธิบายเดิมในคอลัมน์นี้ด้วยค่า Mock Data จริงที่ script ใช้ (อ่านมาจาก `06-test-data.md` หรือจาก script ของ Test Case นั้นโดยตรง) เพื่อให้ Workbook เป็น audit trail ที่ครบในตัวเอง ดูค่าที่ใช้ทดสอบจริงได้ทันทีโดยไม่ต้องเปิดไฟล์อื่นประกอบ — แบ่ง 2 กรณี:
   - **ค่าที่กำหนดไว้ล่วงหน้าได้ (Static)**: ใส่ค่าจริงที่ใช้ตรงๆ (เช่น `email=qa-newmail-001@example.com, current_password=<รหัสผ่านจริงของบัญชีทดสอบ>`)
   - **ค่าที่ระบบ generate เองตอนรัน (Dynamic เช่น OTP/Token)**: ใส่ **ค่าจริงที่จับได้ระหว่างรันรอบนี้จริงๆ** พร้อมวงเล็บกำกับว่าเป็นค่า Dynamic (เช่น `otp=483920 (Dynamic — ค่าจริงที่ระบบสร้างตอนรันรอบนี้ ไม่ใช่ค่าคงที่ที่ใช้ซ้ำได้)`) เพื่อไม่ให้ผู้อ่านย้อนหลังเข้าใจผิดว่าเป็นค่าคงที่ที่จะได้ผลเดิมทุกครั้งถ้าเอาไปรันซ้ำ — ถ้า Test Case ใด Fail/Blocked ก่อนจะไปถึงจุดที่ต้องใช้ค่า Dynamic นั้น ให้คงคำอธิบายเดิมจาก Skill 03 ไว้ (ยังไม่มีค่าจริงให้ใส่)
   - ไฟล์ `06-test-data.md` จาก Skill 06 ยังคงเก็บไว้เหมือนเดิมไม่ต้องลบ ถือเป็น "แผนก่อนรัน" ส่วนคอลัมน์ Test Data ใน Workbook หลังขั้นตอนนี้จะกลายเป็น "ค่าที่ใช้จริงหลังรัน" แทน
5. **คอลัมน์ Test Photo**: ใส่เฉพาะ path รูปของ Test Case ที่ผล **Fail** เท่านั้น (ตามกฎที่ระบุไว้ตั้งแต่ตอน spec — ดูข้อ 2 ด้านบนเรื่องหลาย Browser) — ภาพของ Pass/Blocked ทั้งหมดยังคงถูกเก็บไว้ในโฟลเดอร์ `screenshots/` ตามขั้นตอนที่ 4 เพื่อให้ `result-analysis` (Skill 07) ใช้ต่อ แต่ไม่ต้องใส่ path ในคอลัมน์นี้ถ้าไม่ใช่ Fail

## ขั้นตอนที่ 6 — อัปเดต Manifest และรายงานสรุป

อัปเดต `_pipeline-manifest.md`: ตั้งค่า Stage `06a qa-automation-script` เป็น `Complete` **เฉพาะเมื่อรันครบทุก Test Case ที่เลือกไว้ และครบทุก Browser ที่ระบุใน Env & Config แล้วเท่านั้น** — ถ้ารันแค่บางส่วน (บาง Test Case ยังไม่รัน, หรือรันได้แค่บาง Browser เพราะ environment ที่ใช้อยู่ไม่มี Browser ครบตามที่ Env & Config ระบุ) ให้ตั้งเป็น `In Progress` พร้อมระบุเหตุผลตรงๆ ใน Notes ว่าขาดอะไรไป (เช่น "รันได้แค่ Chromium เพราะ environment นี้ไม่มี Safari/Webkit ติดตั้ง") ใส่ path ของโฟลเดอร์ `automation/` และ `screenshots/`, ใส่วันที่รันล่าสุด

แจ้งผู้ใช้สรุปผลการรัน: จำนวน Pass / Fail / Blocked แยกตาม Priority (เน้น P0/P1 ที่ Fail ให้เห็นชัด) และปัญหา Accessibility ที่พบ (ถ้ามี) แล้วแนะนำให้ไปต่อ `result-analysis` (Skill 07) — **ถ้าปัญหา Accessibility เดียวกัน (เช่น element เดิม, `id` เดิม) ปรากฏซ้ำในหลาย Test Case** (เช่น เกิดจาก component ที่ใช้ร่วมกันทุกหน้า) ให้ระบุไว้ในสรุปด้วยว่าเป็นปัญหาเดียวกันที่กระทบหลายเคส ไม่ใช่บั๊กแยกกันหลายจุด เพื่อให้ผู้ใช้และ `result-analysis` (07) ไม่เข้าใจผิดว่ามีบั๊ก accessibility หลายจุดทั้งที่จริงคือ root cause เดียว

## ข้อควรระวัง

- ห้ามปะปน Test Case Fail จริงกับ Script/Environment Error เด็ดขาด (ดูขั้นตอนที่ 3) — ถ้าไม่แน่ใจว่า error ที่เจอเป็นแบบไหน ให้ถือเป็น `Blocked` ไว้ก่อนแล้วถามผู้ใช้ยืนยัน ไม่ใช่เดาว่าเป็น `Fail`
- Test Case ที่มี Test Data เป็นค่า Dynamic ที่ Skill `test-data-generator` (06) ระบุไว้ว่า environment ปัจจุบันจำลองไม่ได้ (เช่น TC ที่ต้องจำลอง SMS/Email ล้มเหลวทั้งระบบ) ให้ตั้งเป็น `Blocked` พร้อมเหตุผลตรงๆ แทนการฝืนรันจนได้ผลลัพธ์ที่ไม่น่าเชื่อถือ
- ห้ามรันสคริปต์กับ environment ที่ไม่ใช่ตัวที่ระบุไว้ใน Env & Config (เช่น Production) โดยเด็ดขาด
- **หมายเหตุ**: Skill นี้เพิ่มค่า Status `Blocked` เข้าไปใน Dropdown ของคอลัมน์ Status ที่ Skill 03 (`test-case-generator`) เป็นผู้กำหนด Schema ไว้ (เดิมมีแค่ `not start`/`Pass`/`Fail`/`Rejected / Not a Bug`) — เป็นการเปลี่ยนแปลง Schema ย้อนหลัง ผู้ใช้ยืนยันแล้วผ่าน AskUserQuestion ตอนสร้าง Skill นี้ ถ้า Workbook เดิมถูกสร้างไว้ก่อนหน้านี้ (ก่อน Schema เปลี่ยน) ให้แจ้งผู้ใช้ว่า Dropdown ของไฟล์เดิมอาจต้องสร้างใหม่/รีเฟรชเพื่อให้เห็นตัวเลือก `Blocked` ใน Excel (ข้อมูลที่เขียนเข้าไปจะถูกต้องอยู่แล้วแม้ Dropdown จะยังไม่อัปเดต)
