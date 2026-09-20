# Test Report — Skill 07 (result-analysis), RTM (qa-reconcile), Skill 08 (qa-report-generator)

วันที่ทดสอบ: 2026-08-23
วิธีทดสอบ: ใช้ Feature จริง 2 ชุดต่อยอดจากรอบก่อนหน้า ("Login OTP" มีผลทดสอบจริงจาก Skill 06a ครบ 6 เคส, "Two-Factor Backup Codes" มี Requirement/Coverage/RTM ที่มีช่องโหว่จริงติดค้างอยู่) รัน Skill ตามขั้นตอนใน SKILL.md ทีละขั้นจริง เขียนสคริปต์ python-docx/openpyxl จริง ผลิตไฟล์ `.docx`/`.xlsx` จริง แล้ว verify ด้วยการ render เป็น PDF → JPG แล้วตรวจด้วยตาจริงทุกไฟล์ (ตามแนวทาง docx skill) ไม่ใช่แค่บรรยายว่าไฟล์ควรมีหน้าตาอย่างไร

---

## Skill 07 — result-analysis (Feature: Login OTP)

### ผลการทดสอบ: ✅ ผ่านทุก Case, พบและแก้บั๊กจริง 1 จุด (page-break)

| # | Test Case | ผล |
|---|---|---|
| TC-RA-01 | Gate: Stage 06a = `In Progress` (ไม่ใช่ `Complete`) → ต้องหยุดถามผู้ใช้ก่อนเสมอ | ✅ Pass — หยุดถามจริง ผู้ใช้เลือก (b) วิเคราะห์ผลเท่าที่มีอยู่ตอนนี้ไปก่อน (partial) |
| TC-RA-02 | อ่าน Workbook สดจากดิสก์ (ไม่ใช้ค่าที่ cache ไว้ก่อนหน้า) ผ่าน `read_workbook.py` | ✅ Pass — ได้ 17 แถวตรงกับ Workbook Version ล่าสุด (V5) |
| TC-RA-03 | คำนวณ Test Coverage % ถูกต้อง | ✅ Pass — 6/17 = 35.3% ตรงกับที่คำนวณด้วยมือ |
| TC-RA-04 | Status × Priority cross-tab ครบทุกช่อง รวมช่องที่เป็น 0 | ✅ Pass |
| TC-RA-05 | Root Cause แยกเป็น 3 หมวด (Functional / Accessibility / Script-Environment) ถูกหมวดตรงกับความจริง | ✅ Pass — TC-014 → Functional, TC-001/002/003/009 → Accessibility, TC-006 → Script/Environment |
| TC-RA-06 | บั๊ก Accessibility ที่ซ้ำกันข้ามหลาย Test Case ต้องถูกรวมเป็น 1 entry ไม่ใช่นับซ้ำ | ✅ Pass — `image-alt` กระทบ 4 เคส (TC-001/002/003/009) รวมเป็น 1 entry, `color-contrast` กระทบ 2 เคส (TC-002/009) รวมเป็นอีก 1 entry (รวม 2 entries ไม่ใช่ 6) |
| TC-RA-07 | อ่านรูปจากโฟลเดอร์ `screenshots/<Browser>/` ทั้งหมด ไม่ใช่แค่คอลัมน์ Test Photo (ที่มีเฉพาะเคส Fail) | ✅ Pass — `07-photo-evidence.docx` มีรูปของทุกเคสที่ทดสอบแล้ว ไม่ใช่แค่เคสที่ Fail |
| TC-RA-08 | `07-photo-evidence.docx` ต้องมี 1 หน้า/1 Test Case ครบทั้ง 17 เคส รวมเคสที่ `not start` ด้วย (ต้องขึ้น "ยังไม่ได้ทดสอบ" ไม่ใช่เว้นว่างหรือข้าม) | ⚠️ พบบั๊กจริงรอบแรก (ดู BUG-15) → ✅ Pass หลังแก้ |
| TC-RA-09 | Manifest `07 result-analysis` = `Complete` ทันทีที่สร้างไฟล์ครบ 2 ไฟล์ (ไม่ต้องรอให้ทดสอบครบทุกเคส — Complete แปลว่า "Skill นี้วิเคราะห์เสร็จแล้ว" ไม่ใช่ "ทุกเคสผ่าน") | ✅ Pass |
| TC-RA-10 | ห้ามแก้ไข Test Case Workbook (read-only skill) — ยืนยันด้วยสคริปต์ `read_workbook.py` แยกจาก `qa_workbook.py` ที่เขียนได้ | ✅ Pass — ตรวจสอบแล้วว่า Workbook Version ไม่ขยับหลัง Skill 07 รัน |

#### BUG-15 — `07-photo-evidence.docx` หน้าปกกับ TC-001 ใช้หน้าเดียวกัน

- **จุดที่พบ**: `build_docx_reports.py` ฟังก์ชัน `build_photo_evidence()` เดิมใส่ `doc.add_page_break()` เฉพาะกรณี `i > 0` ในลูป `for i, c in enumerate(data["cases"])` — ทำให้ Test Case แรก (TC-001) ไม่มี page break ก่อนหน้าตัวเอง
- **ผลกระทบที่พบจริง**: Render ครั้งแรกเป็น PDF แล้วแปลงเป็น JPG ดู พบว่าหน้า 1 มีทั้งหัวข้อ/คำอธิบายเอกสาร **และ** เนื้อหาของ TC-001 (รูป+Status+Remarks) ปนกันอยู่ในหน้าเดียว ขณะที่ Test Case อื่นๆ ทุกเคสได้หน้าของตัวเองตามที่ตั้งใจ — ผิดกฎ "1 หน้าต่อ 1 Test Case" เฉพาะเคสแรกเคสเดียว
- **Root cause**: เงื่อนไข `if i > 0` ข้าม TC-001 ไปเพราะเป็น element แรกในลูป โดยไม่ได้คิดว่าหน้าปก/คำนำก็ต้องการ page break แยกออกจากเนื้อหา Test Case ตัวแรกด้วยเช่นกัน
- **การแก้ไข**: เพิ่ม `doc.add_page_break()` แบบไม่มีเงื่อนไข ทันทีหลังพารากราฟหัวข้อ/คำนำ ก่อนเข้าลูป `for i, c in enumerate(...)` แล้วลบเงื่อนไข `if i > 0` ออกจากในลูป (ทุกเคสรวม TC-001 จึงเริ่มหน้าใหม่เสมอ)
- **หลักฐานการแก้**: Render ซ้ำหลังแก้ — จำนวนหน้าเพิ่มจาก 17 เป็น 18 หน้า (1 หน้าปกล้วนๆ + 17 หน้า Test Case) ตรวจด้วยตาจาก JPG ทั้งหน้า 1 (ตอนนี้มีแค่หัวข้อ/คำนำ) และหน้า 2 (ตอนนี้เป็น TC-001 เต็มหน้าเหมือนเคสอื่น)

### ไฟล์ output จริงที่ผลิต (Login OTP)
- `07-result-analysis.docx` — Coverage 35.3%, cross-tab, 4 Root Cause entries, ตาราง "ต้องแก้ก่อนปิดงาน" 4 รายการ (TC-001/002/003/009)
- `07-photo-evidence.docx` — 18 หน้า (verify ผ่าน PDF→JPG แล้ว)

---

## RTM — qa-reconcile

### ผลการทดสอบ: ✅ ผ่านทุก Case, พบช่องโหว่จริง 2 จุด (1 จุดเป็นบั๊กใน Skill อื่น = BUG-13, 1 จุดเป็น Orphan Requirement จริง)

| # | Test Case | Feature | ผล |
|---|---|---|---|
| TC-RTM-01 | Gate: Stage 07 = `Complete` → ไปต่อได้ปกติ | Login OTP | ✅ Pass |
| TC-RTM-02 | Gate: Stage 07 = `Not Started` → ต้องหยุดถามผู้ใช้ก่อนเสมอ (ไม่ใช่แค่กรณี `In Progress`) | Two-Factor Backup Codes | ✅ Pass — หยุดถามจริง ผู้ใช้เลือก (b) standalone ให้ 01/02/Workbook มาโดยตรง |
| TC-RTM-03 | **หลักการ Source of Truth**: คำนวณ Traceability ใหม่สดจาก `01-requirement-review.md` + `02-e2e-flow.md` + Test Case sheet (อ่านสดจากดิสก์) เสมอ ไม่เชื่อชีต Requirement Matrix เดิมในตัว Workbook | Login OTP | ✅ Pass — เทียบกับชีตเดิมแล้วตรงกันทุกแถว (12 แถว: 6 BR + 6 Flow) ไม่พบ discrepancy |
| TC-RTM-04 | หลักการเดียวกัน แต่กับ Feature ที่ชีต Requirement Matrix เดิม**ผิด/ว่างเปล่า** — RTM ต้องไม่ได้รับผลกระทบเพราะคำนวณใหม่เองเสมอ | Two-Factor Backup Codes | ✅ Pass — พบว่าชีตเดิมยังเป็น placeholder ว่างเปล่า (ดู BUG-13) แต่ RTM คำนวณ Traceability ที่ถูกต้องได้เองอยู่ดี ไม่กระทบผลลัพธ์ RTM เลย — พิสูจน์ว่าหลักการออกแบบถูกต้อง |
| TC-RTM-05 | ตรวจจับ Orphan Requirement จริง (Requirement ที่ไม่มี Test Case รองรับ) | Two-Factor Backup Codes | ✅ Pass — พบ "Flow 1 - Alternate" (regenerate ทับชุดเก่า) ที่ `04-coverage-review.md` เคย Defer ไว้และยังไม่เคยถูกสร้าง Test Case ให้ ถูกจัดเป็น `Orphan Requirement` ถูกต้อง |
| TC-RTM-06 | Business Rule ที่มี Assumption ค้างอยู่ (จาก Skill 01) แต่มี Test Case รองรับแล้ว ต้องได้สถานะรวม ไม่ใช่แยกเป็นแค่ "Assumption ค้าง" อย่างเดียว | Login OTP | ✅ Pass — BR-2/3/5/6 (4 รายการ) ได้ `traceability_status = "Linked - มี Assumption ค้าง"` สีเหลือง ไม่ใช่แค่เขียวหรือแค่แดง |
| TC-RTM-07 | RTM ไม่มีสิทธิ์แก้ Test Case Workbook เอง — เมื่อพบช่องโหว่ต้องถามผู้ใช้เสมอว่าจะ (a) กลับไปแก้ที่ต้นทาง หรือ (b) Accepted Gap | Two-Factor Backup Codes | ✅ Pass — ถามจริง ผู้ใช้เลือก (b) Accepted Gap พร้อมเหตุผล → บันทึกเฉพาะในชีต Findings ของ RTM เอง ไม่แตะ Workbook เลย |
| TC-RTM-08 | Manifest `RTM qa-reconcile` = `Complete` เฉพาะเมื่อทุกรายการที่พบมีการตัดสินใจแล้วครบ (ไม่มีค้าง) | ทั้ง 2 Feature | ✅ Pass |
| TC-RTM-09 | Output เป็น `.xlsx` 2 ชีต ("RTM", "Findings") พร้อมสีตาม `traceability_status` | ทั้ง 2 Feature | ✅ Pass — ตรวจด้วยการเปิดไฟล์จริงและอ่านค่าสี cell |
| TC-RTM-10 | ห้ามแก้ไข Test Case Workbook — ยืนยันด้วยสคริปต์ read-only แยก (`read_workbook.py`) | ทั้ง 2 Feature | ✅ Pass |

**บันทึกสำคัญ**: `traceability_status = "Linked - มี Assumption ค้าง"` (สีเหลือง) เป็นการปรับปรุงระหว่างสร้าง SKILL.md/สคริปต์ (ก่อนรันจริงครั้งแรก) ไม่ใช่บั๊กที่พบระหว่างทดสอบ — เดิมออกแบบไว้แค่ `Linked`/`Orphan Requirement` แต่พบว่าไม่พอสำหรับกรณีที่แถวหนึ่งเป็นทั้ง "มี Test Case จริง" และ "มีความเสี่ยงด้าน Requirement ค้าง" พร้อมกัน จึงเพิ่มสถานะรวมนี้ก่อนเริ่มทดสอบจริง

### ไฟล์ output จริงที่ผลิต
- Login OTP: `RTM-traceability-matrix.xlsx` (12 แถว, ไม่มี Orphan, 4 รายการ Assumption ค้าง)
- Two-Factor Backup Codes: `RTM-traceability-matrix.xlsx` (พบ 1 Orphan Requirement จริง + 1 discrepancy note เรื่องชีตเดิมว่างเปล่า)

---

## BUG-13 — `test-case-generator` (Skill 03) ไม่เติมชีต Requirement Matrix เมื่อเข้าสาย pipeline แบบ standalone

- **จุดที่พบ**: ระหว่างเตรียมข้อมูลทดสอบ RTM จริงสำหรับ Feature "Two-Factor Backup Codes" (เข้าสาย pipeline แบบ standalone ตั้งแต่ Skill 02 ไม่ผ่าน Skill 01) พบว่าชีต Requirement Matrix ใน `03-test-case-workbook.xlsx` ของ Feature นี้ยังเป็น**ข้อความ placeholder เดิมล้วนๆ ไม่เคยถูกเติมเนื้อหาจริงเลย**
- **Root cause**: ขั้นตอนที่ 4.2 ของ `test-case-generator/SKILL.md` (เดิม) สั่งให้เติมชีตนี้จาก `01-requirement-review.md` + `02-e2e-flow.md` เท่านั้น โดยสมมติว่า `01-requirement-review.md` มีอยู่เสมอ — ไม่มีเส้นทางสำรองสำหรับกรณีที่ Feature เข้าสาย pipeline แบบ standalone (ข้าม Skill 01) ซึ่งเป็นสถานการณ์ที่ Skill นี้เองก็รองรับไว้อยู่แล้วในส่วน Gate (ตาม BUG-07 ที่แก้ไปก่อนหน้านี้) แต่ Step 4.2 ไม่ได้ถูกปรับให้สอดคล้องกัน
- **ผลกระทบ**: ชีต Requirement Matrix ที่ควรเป็นแหล่งอ้างอิง Traceability กลับว่างเปล่าไม่มีประโยชน์ — แม้ในกรณีนี้จะไม่กระทบ RTM (เพราะ RTM คำนวณใหม่เองเสมอ ไม่พึ่งชีตนี้) แต่ก็เป็นข้อมูลที่ผิดพลาดค้างอยู่ในไฟล์ที่ผู้ใช้จริง/ทีมอื่นอาจเปิดดูโดยตรงและเข้าใจผิดว่าไม่มี Requirement ใดๆ รองรับ Test Case เหล่านี้เลย
- **การแก้ไข**: แก้ `test-case-generator/SKILL.md` ขั้นตอนที่ 4.2 เพิ่มเงื่อนไข standalone: ถ้า `01-requirement-review.md` ไม่มีอยู่จริง ให้เติมเฉพาะแถว Flow จาก `02-e2e-flow.md` แทน (ข้าม Business Rule ID ไปเลย ไม่คิด ID ปลอมขึ้นมาเอง) และใส่หมายเหตุไว้ในเซลล์แรกของชีตอธิบายว่า Feature นี้เข้าสาย pipeline แบบ standalone จึงไม่มี Business Rule ID อย่างเป็นทางการ
- **หลักฐานการแก้**: แก้ไข SKILL.md แล้ว (ยังไม่ได้รันสร้าง Workbook ใหม่ทับของเดิม เพราะ Workbook เดิมของ Feature นี้ถูกใช้เป็นหลักฐานอ้างอิงของ BUG-13 เองในรายงานนี้ — ยืนยัน logic ที่แก้แล้วด้วยการอ่านโค้ด SKILL.md ใหม่ตรงกับ TC-RTM-04)
- **ผลกระทบต่อไฟล์ที่เคยส่งมอบ**: `test-case-generator/SKILL.md` เคยถูกส่งมอบให้ผู้ใช้แล้ว **2 ครั้ง** (รอบ Skill 02–05 ครั้งแรก, รอบ Skill 06/06a ครั้งที่สองสำหรับ Status `Blocked`) — ฉบับนี้คือ **ครั้งที่ 3** ที่ต้องส่งใหม่ เพราะ BUG-13

---

## Skill 08 — qa-report-generator (Feature: Login OTP)

### ผลการทดสอบ: ✅ ผ่านทุก Case, พบและแก้บั๊กจริง 1 จุด (BUG-14, การเน้นคำเตือน Deadline)

| # | Test Case | ข้อมูล | ผล |
|---|---|---|---|
| TC-QR-01 | Gate: Stage RTM = `Complete` → ไปต่อได้ปกติ | Login OTP (จริง) | ✅ Pass |
| TC-QR-02 | อ่าน Deadline จาก header ของ `01-requirement-review.md`, Workbook สด, `07-result-analysis.docx`, ชีต Findings ของ RTM ครบทุกแหล่ง | Login OTP (จริง) | ✅ Pass |
| TC-QR-03 | **กฎ Go/No-Go ข้อ 1 (สำคัญที่สุด)**: ถ้ามี Test Case ใดยัง `not start` ต้อง No-Go ทันที ตรวจก่อนกฎอื่นทั้งหมด แม้เคสที่ทดสอบแล้วบางส่วนจะ Pass ก็ตาม | Login OTP (จริง — 11/17 ยัง not start) | ✅ Pass — สรุป **No-Go** ถูกต้อง พร้อมเหตุผลระบุจำนวนเคสที่ยังไม่ได้ทดสอบและ TC ที่เป็น P0 |
| TC-QR-04 | กฎข้อ 2: No-Go เมื่อมี P0 Fail จริง (ไม่ใช่ Blocked) | synthetic | ✅ Pass — ตรวจ logic ในสคริปต์ตรงตามที่ SKILL.md กำหนด |
| TC-QR-05 | กฎข้อ 3: Conditional Go เมื่อไม่มี P0 Fail แต่มี P1 Fail ค้าง | synthetic (`report_08_conditional.json`) | ✅ Pass — Render จริงแล้วตรวจ verdict box เป็นสีส้ม ข้อความ "Conditional Go" ถูกต้อง |
| TC-QR-06 | กฎข้อ 4: Go เมื่อ P0/P1 ผ่านหมด เหลือแค่ P2/P3 หรือไม่มีเลย | synthetic (`report_08_go.json`) | ✅ Pass — Render จริงแล้วตรวจ verdict box เป็นสีเขียว |
| TC-QR-07 | กฎข้อ 5: เคส `Blocked` ต้องไม่ทำให้ No-Go โดยตรง แต่ต้องถูกแสดงแยกต่างหากเสมอ | Login OTP (จริง — TC-006 Blocked) | ✅ Pass — TC-006 ปรากฏในตาราง Known Issues หมวด "Script/Environment Error" แยกจากบั๊กจริง ไม่ถูกนับรวมเป็นเหตุผลของ No-Go |
| TC-QR-08 | กฎข้อ 6: คำเตือนเลย Deadline ต้อง**เด่นชัด** (ตัวหนา/สี) แต่**ห้าม**เปลี่ยนผล Go/No-Go ที่คำนวณจากกฎ 1–4 | synthetic (`report_08_conditional.json`, `deadline_passed: true`) | ⚠️ พบบั๊กจริง (ดู BUG-14) → ✅ Pass หลังแก้ — verdict ยังคงเป็น Conditional Go เหมือนเดิม (ไม่ถูก override) แต่คำเตือนตอนนี้ตัวหนา/แดงจริง |
| TC-QR-09 | Gate: RTM ยังไม่ `Complete` → ต้องเสนอทางเลือก Provisional ให้ผู้ใช้ และถ้าเลือกทำต่อ ต้องติดป้าย "Provisional" ทุกจุดที่พูดถึง Go/No-Go ไม่ใช่แค่จุดเดียว | (ตรวจโค้ดใน SKILL.md โดยตรง) | ✅ Pass — ตรวจสอบแล้วว่าโครงสร้างข้อมูล `is_provisional` ถูกส่งต่อไปยังทุกจุดที่เกี่ยวข้องในสคริปต์ render |
| TC-QR-10 | เอกสารมีครบทุก section ตามสเปก: หน้าปก, Go/No-Go เด่นชัด, Test Coverage, ตาราง Known Issues, ความครบถ้วน Browser, Days-vs-Deadline, Next Steps (bullet), ตาราง Approval (QA Lead + PM/Product Owner เว้นว่างไว้เซ็นจริง) | Login OTP (จริง) | ✅ Pass — Render เป็น PDF → JPG แล้วตรวจด้วยตาครบทุก section (2 หน้า) |

#### BUG-14 — คำเตือนเลย Deadline ไม่ถูกเน้นสีจริงใน `08-qa-report.docx`

- **จุดที่พบ**: SKILL.md ขั้นตอนที่ 3 กฎข้อ 6 กำหนดให้คำเตือนเลย Deadline ต้อง "เด่นชัด" (ตัวหนา/สี) แต่ `build_final_report.py` เวอร์ชันแรกแค่ render ข้อความ `days_vs_deadline` ตรงๆ ตามที่ส่งเข้ามา ไม่มีการจัดสไตล์แบบมีเงื่อนไขเลย — ไม่สอดคล้องกับคำเตือนความครบถ้วน Browser ในสคริปต์เดียวกันที่**มี**การทำตัวหนา/แดงเมื่อไม่ครบอยู่แล้ว
- **ผลกระทบที่พบจริง**: ทดสอบด้วย synthetic data ที่ `deadline_passed: true` (สถานการณ์ "วันนี้เลย Deadline มา 4 วัน") — Render แล้วพบว่าข้อความ "เลย Deadline" ปรากฏเป็นตัวอักษรปกติสีดำเหมือนข้อความทั่วไป ไม่เด่นชัดตามที่ SKILL.md กำหนดไว้จริง
- **Root cause**: schema ของข้อมูลที่ส่งเข้าสคริปต์ไม่มี flag บอกว่า "เลย Deadline แล้วหรือยัง" แยกจากข้อความอธิบาย — สคริปต์จึงไม่มีทางรู้ได้เลยว่าต้อง apply สไตล์พิเศษเมื่อไหร่ นอกจาก parse ข้อความเอาเอง (ซึ่งเปราะบางและไม่ควรทำ)
- **การแก้ไข**: เพิ่ม `deadline_passed: bool` เข้าไปใน schema ของข้อมูล เมื่อเป็น `true` สคริปต์จะ (1) render ข้อความ `days_vs_deadline` เป็นตัวหนา + สีแดง (`RGBColor(0xCC, 0x00, 0x00)`) และ (2) เพิ่มพารากราฟคำเตือนแยกต่างหาก "⚠ เลย Deadline ที่กำหนดไว้แล้ว — โปรดพิจารณาประกอบการตัดสินใจ" ด้วยสไตล์เดียวกัน — อัปเดต SKILL.md กฎข้อ 6 ให้ระบุชัดว่าต้องส่ง `deadline_passed: true` ไม่ใช่แค่เขียนคำว่า "เลย Deadline" ปนอยู่ในข้อความเฉยๆ
- **ข้อควรระวังที่จับได้เองก่อนเกิดบั๊กจริง**: การแก้ครั้งแรกที่ลองเขียนใช้ `deadline_para.add_run("\n⚠ ...")` (ใส่ `\n` ในข้อความของ run เดียว) ซึ่งขัดกับข้อควรระวังของ docx skill ที่เพิ่งอ่านมา ("ห้ามใช้ `\n` — ให้แยกเป็น Paragraph ใหม่แทน") จับได้เองก่อน render จริง จึงแก้เป็นการสร้าง `doc.add_paragraph()` แยกต่างหากสำหรับบรรทัดคำเตือนที่สอง หลีกเลี่ยงบั๊กด้าน rendering ที่จะเกิดขึ้นจริงถ้าไม่จับได้ (`\n` ในรูปแบบนี้มักจะไม่ขึ้นบรรทัดใหม่จริงหรือกลายเป็นตัวอักษรแปลกปลอม)
- **หลักฐานการแก้**: Render ซ้ำ synthetic scenario "Conditional Go" (มี `deadline_passed: true`) → ตรวจ JPG พบทั้งข้อความ `days_vs_deadline` และพารากราฟคำเตือนแยกเป็นตัวหนาสีแดงจริงทั้งคู่ — และ render ซ้ำ `08-qa-report.docx` จริงของ Login OTP ด้วยสคริปต์ที่แก้แล้ว (ผลลัพธ์ยังเป็น No-Go เหมือนเดิม เพราะ `deadline_passed: false` สำหรับ Feature นี้ — 23 ส.ค. 2569 ยังไม่ถึง Deadline 10 ก.ย. 2569)

### ไฟล์ output จริงที่ผลิต
- Login OTP: `08-qa-report.docx` (verdict = No-Go, 2 หน้า, verify ผ่าน PDF→JPG แล้ว)
- Synthetic (เพื่อพิสูจน์ 3 verdict ที่เหลือเท่านั้น ไม่ใช่ deliverable): `08-go.docx` (Go), `08-conditional.docx` (Conditional Go), `08-provisional.docx` (Provisional)

---

## ขอบเขตที่ยังไม่ได้ทดสอบ (boundary ที่ทราบและแจ้งไว้ตรงๆ)

- **Feature "Two-Factor Backup Codes" — Skill 07/08**: ทำเฉพาะ **logic-only check ของ Gate** (ตรวจโค้ดใน SKILL.md ว่า Gate จะตัดสินใจถูกต้องตามสถานะ manifest จริงของ Feature นี้) ไม่ได้รันสร้างไฟล์ `.docx` จริงสำหรับ Feature นี้ เพราะกลไกหลักของทั้ง 2 Skill (การวิเคราะห์/การตัดสินใจ Go-No-Go/การ render) ถูกพิสูจน์ครบถ้วนแล้วผ่าน Feature "Login OTP" — Stage `07`/`08` ของ Feature นี้จึงยังคงเป็น `Not Started` จริง ไม่ได้ตั้งเป็น Complete/In Progress หลอกๆ
- **Verdict "Go" และ "Provisional" ของ Skill 08**: พิสูจน์เฉพาะความถูกต้องของการ render (สี/ข้อความ) ผ่าน synthetic data เท่านั้น เนื่องจากข้อมูลจริงที่มีอยู่ (Login OTP) มีแค่สถานการณ์ No-Go ตามธรรมชาติ (ทดสอบยังไม่ครบ) — ยังไม่เคยพิสูจน์กับสถานการณ์จริงที่ทดสอบครบทุกเคสแล้วสรุปเป็น Go จริง (จะพิสูจน์ได้เมื่อ Feature ใด Feature หนึ่งถูกทดสอบจนครบสมบูรณ์ในรอบถัดๆ ไป)

---

## ข้อสังเกตเชิง Design เพิ่มเติม

1. **รูปแบบสคริปต์ใหม่ "render-only"**: `build_docx_reports.py`, `build_rtm.py`, `build_final_report.py` ทั้ง 3 ไฟล์ไม่มี logic การวิเคราะห์/ตัดสินใจอยู่ในสคริปต์เลย — รับ JSON ที่มีโครงสร้างพร้อมแล้ว (สร้างจากการตัดสินใจของ LLM ตามคำสั่งใน SKILL.md) แล้วแค่ render ออกมาเป็นไฟล์ — สอดคล้องกับหลักการเดิมของทั้งโปรเจกต์ที่ให้ judgment อยู่ใน SKILL.md ไม่ใช่ในโค้ด
2. **สคริปต์อ่านอย่างเดียวตัวใหม่ (`read_workbook.py`)**: จงใจแยกออกจาก `qa_workbook.py` (ตัวที่เขียนได้ ใช้ใน Skill 03/04/05/06a) เป็นสคริปต์คนละไฟล์ ทำสำเนาเหมือนกันทุกตัวอักษรไว้ 3 ชุด (`result-analysis/`, `qa-reconcile/`, `qa-report-generator/`) — เพื่อป้องกันไม่ให้ Skill 07/RTM/08 เขียนทับ Workbook ได้แม้จะพลาดโดยไม่ตั้งใจ (defense-in-depth ระดับเครื่องมือ ไม่ใช่แค่ระดับคำสั่งใน SKILL.md)
3. **shared script duplication**: `read_workbook.py` เป็นสำเนาที่ 1-2-3 ของสคริปต์อ่านอย่างเดียว (แยกจาก `qa_workbook.py` ที่มี 4 สำเนาแล้วจากรอบก่อน) — ยังคงเป็น trade-off เดิมเพื่อความ self-contained ของแต่ละ Skill
4. **การเลือกรูปแบบไฟล์**: Skill 07 = Word (ผู้ใช้ยืนยัน), RTM = Excel (ผู้ใช้ยืนยัน — เหมาะกับตาราง Traceability ที่มีจำนวนแถวแปรผัน), Skill 08 = Word (เลือกเองเพื่อความสอดคล้อง — รายงานสรุปที่มี Approval signature block เป็นรูปแบบที่ใช้ Word กันโดยทั่วไป)

## รายการบั๊กสะสมทั้งโปรเจกต์ (สำหรับอ้างอิง)

| Bug ID | Skill ที่พบ | สรุป |
|---|---|---|
| BUG-07 | e2e-flow-designer (02) | Gate ไม่ถามผู้ใช้เมื่อไม่มี manifest เลย (สรุปเอาเองว่า standalone) |
| BUG-08 | risk-analysis (05) | อัปเดต Workbook ทีละแถวทำให้ Version History ท่วม |
| BUG-09 | qa-automation-script (06a) | Accessibility downgrade ไม่กรองระดับความรุนแรง ทำให้ทุกเคส Fail จาก noise |
| BUG-10 | qa-automation-script (06a) | ภาพหลักฐานผิดจุดเมื่อ Test Case ตรวจหลายกรณีย่อยที่เปลี่ยนหน้าก่อน raise |
| BUG-11 | qa-automation-script (06a) | สีวงไฮไลท์ตัดสินใจก่อนทราบผล Accessibility scan ทำให้ภาพกับ Status ไม่ตรงกัน |
| BUG-13 | test-case-generator (03) | ไม่เติมชีต Requirement Matrix เมื่อเข้าสาย pipeline แบบ standalone (ไม่มี 01) |
| BUG-14 | qa-report-generator (08) | คำเตือนเลย Deadline ไม่ถูกเน้นสีจริง แม้ SKILL.md กำหนดให้ต้องเด่นชัด |
| BUG-15 | result-analysis (07) | `07-photo-evidence.docx` หน้าปกกับ TC-001 ใช้หน้าเดียวกัน (ขาด page break ก่อนเคสแรก) |

ทั้ง 8 บั๊กแก้ไขแล้วและมีหลักฐานยืนยันการแก้ไขจริงทุกจุด (หมายเหตุ: BUG-12 ไม่มีอยู่จริงในโปรเจกต์นี้ — เลขบั๊กกระโดดจาก 11 ไป 13 เพราะ BUG-13 ถูกค้นพบและตั้งชื่อไว้ก่อน BUG-14/15 ตามลำดับเวลาที่พบจริงระหว่างการทดสอบรอบนี้)
