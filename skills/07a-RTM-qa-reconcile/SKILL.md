---
name: qa-reconcile
description: ตรวจสอบ Traceability ของทั้งสาย QA Pipeline สำหรับ 1 Feature ว่า Business Rule/User Flow ทุกข้อเชื่อมโยงไปถึง Test Case จริง และ Test Case ทุกตัวเชื่อมโยงกลับไปหา Requirement ได้ สร้าง Requirement Traceability Matrix (RTM) เป็นไฟล์ Excel เป็นขั้นตอน RTM ที่บังคับของ QA Pipeline นี้ (อยู่ระหว่าง Skill 07 และ 08) ให้ใช้ Skill นี้ทันทีเมื่อผู้ใช้พูดถึง Traceability Matrix, RTM, การตรวจสอบว่า Requirement ครอบคลุมครบ, หรือ reconcile ผลทั้งสาย pipeline ของ Feature หนึ่งๆ แม้จะไม่ได้เอ่ยชื่อ Skill ตรงๆ
---

# qa-reconcile (RTM)

Skill นี้เป็น**ขั้นตอน RTM ที่บังคับ** ของ QA Pipeline อยู่ระหว่าง `result-analysis` (07) และ `qa-report-generator` (08) หน้าที่คือตรวจสอบว่าทุกอย่างที่ผ่านมาตลอดทั้งสาย **"เชื่อมโยงกันจริง"** หรือไม่ — ไม่ใช่แค่เช็คว่าแต่ละ Skill ทำงานของตัวเองเสร็จ แต่เช็คว่าผลลัพธ์ของ Skill ต่างๆ ยัง"สอดคล้องกัน"อยู่จริงในภาพรวม เช่น Business Rule ทุกข้อมี Test Case รองรับจริงไหม, Test Case ทุกตัวมีที่มาจาก Requirement/Flow จริงไหม, ประเด็นที่เคย Deferred ไว้ตอน `coverage-review` (04) ถูกจัดการหรือถูกลืมไปแล้ว

**หลักการสำคัญที่สุดของ Skill นี้ — Source of Truth**: **ห้ามเชื่อชีต "Requirement Matrix" ที่มีอยู่แล้วใน Test Case Workbook ทั้งหมด** เพราะชีตนั้นถูกเขียนไว้ตอน `test-case-generator` (03) สร้าง Workbook ครั้งแรก และอาจไม่ได้ถูกอัปเดตให้ตรงกับสถานะล่าสุดเสมอไป (เช่น Test Case ที่เพิ่มเข้ามาทีหลังจาก `coverage-review` อาจไม่ถูกใส่กลับเข้าชีตนี้) **ต้องคำนวณ Traceability ใหม่สดๆ ทุกครั้ง** โดยเทียบข้อมูลจริงจาก 3 แหล่ง: (1) `01-requirement-review.md` (Business Rules ต้นทาง), (2) `02-e2e-flow.md` (User Flow และ Related Business Rules ที่แต่ละ Flow อ้างถึง), (3) Test Case Workbook ชีต "Test Case" ที่อ่านสดจากไฟล์จริง — ใช้หลักการเดียวกับที่ `coverage-review` (04) ใช้ตอนตรวจ Coverage

## ขั้นตอนที่ 1 — ระบุ Feature และตรวจสอบขั้นตอนก่อนหน้า

1. หาโฟลเดอร์ Project Root และโฟลเดอร์ Feature เหมือน Skill อื่นๆ ในสาย
2. อ่านไฟล์ `_pipeline-manifest.md`
3. **เช็ค Gate**: ต้องรันต่อจาก `result-analysis` (07) เสมอ — ตรวจสอบสถานะ Stage `07 result-analysis` (ถ้าไม่มี manifest เลยก็ถือว่ายังไม่เสร็จเช่นกัน ต้องถามผู้ใช้เสมอ ห้ามสรุปเอาเอง):
   - **ถ้า `Complete`**: ไปต่อขั้นตอนที่ 2
   - **ถ้ายังไม่ `Complete`**: หยุดและถามผู้ใช้ว่า (a) ต้องการไปรัน `result-analysis` ให้เสร็จก่อนไหม (แนะนำ) หรือ (b) ต้องการใช้ Skill นี้แบบ standalone — ถ้าเลือก (b) ให้ขอไฟล์ `01-requirement-review.md`, `02-e2e-flow.md`, และ Test Case Workbook มาจากผู้ใช้โดยตรง

## ขั้นตอนที่ 2 — รวบรวมข้อมูลต้นทางทั้งหมด

1. อ่าน `01-requirement-review.md` — ดึงรายการ Business Rules ทุกข้อ (พร้อมเลขข้อ/ID อ้างอิงเดียวกับที่ `test-case-generator` (03) ใช้ตอนสร้างชีต Requirement Matrix ครั้งแรก เช่น `BR-1`, `BR-2`)
2. อ่าน `02-e2e-flow.md` — ดึงรายการ User Flow ทุก Flow พร้อม "Related Business Rules" ที่แต่ละ Flow ระบุไว้
3. อ่าน `04-coverage-review.md` — ดึงรายการ**ประเด็นที่เคยถูก Defer ไว้** (ยังไม่ Fix ตอนนั้น) เพื่อตรวจสอบภายหลังว่าปัจจุบันถูกจัดการหรือยัง
4. อ่าน Test Case Workbook ชีต "Test Case" **สดจากไฟล์จริง** ด้วย `python3 scripts/read_workbook.py read-cases --path "<path>"` (ห้ามใช้ชีต Requirement Matrix ที่มีอยู่แล้วเป็นข้อมูลหลัก — ใช้ได้แค่เป็นข้อมูลอ้างอิงเปรียบเทียบเท่านั้นว่าตรงกับที่คำนวณใหม่หรือไม่)

## ขั้นตอนที่ 3 — คำนวณ Traceability ใหม่และหาจุดที่ขาดการเชื่อมโยง

สร้างการจับคู่ (mapping) ระหว่าง Business Rule/Flow กับ Test Case โดยอ่านเนื้อหาจริงของแต่ละ Test Case (Test Scenario, Test Step, Expected Result) เทียบกับ Business Rule/Flow แต่ละข้อ แล้วตรวจหาจุดต่อไปนี้ทั้งหมด:

1. **Orphan Requirement**: Business Rule หรือ Flow ที่ไม่มี Test Case ใดอ้างอิงถึงเลย
2. **Orphan Test Case**: Test Case ที่ไม่สามารถโยงกลับไปหา Business Rule/Flow ข้อใดได้เลย (ไม่ได้แปลว่าผิดเสมอไป — อาจเป็น edge case ที่ตั้งใจเพิ่มเอง แต่ต้องถูก**รายงานให้เห็น**เพื่อให้ผู้ใช้ตัดสินใจ ไม่ใช่ปล่อยผ่านเงียบๆ)
3. **Deferred ที่ยังไม่ถูกจัดการ**: ประเด็นจาก `04-coverage-review.md` ที่ระบุว่า Deferred แต่ปัจจุบันยังไม่มี Test Case มารองรับ (เทียบจากขั้นตอนที่ 2.3)
4. **Requirement Matrix เดิมไม่ตรงกับความเป็นจริง**: ถ้าชีต Requirement Matrix เดิมในไฟล์ระบุว่า Business Rule ข้อหนึ่ง Covered แต่จากการคำนวณใหม่พบว่าไม่จริง (เช่น Test Case ที่เคยอ้างอิงถูกลบไปแล้ว) ให้รายงานความไม่ตรงกันนี้ไว้ด้วย — นี่คือเหตุผลที่ห้ามเชื่อชีตเดิมเพียงอย่างเดียว
5. **Business Rule ที่ยังมี Assumption ค้างอยู่**: Business Rule ที่ `01-requirement-review.md` ระบุว่ายังไม่นิ่ง/ยังไม่ยืนยัน (เช่น ค่าที่ยังไม่ confirm) ให้ทำเครื่องหมายไว้ใน RTM ว่า "มีความเสี่ยงเรื่อง Requirement ยังไม่นิ่ง" แม้จะมี Test Case รองรับแล้วก็ตาม เพื่อให้ `qa-report-generator` (08) เห็นความเสี่ยงนี้ตอนสรุป Go/No-Go — สถานะ Traceability ของแถวนี้ให้ใช้ค่า `Linked - มี Assumption ค้าง` (ไม่ใช่แค่ `Linked` เฉยๆ) เพื่อสื่อว่ามี Test Case รองรับแล้วจริง แต่ยังมีความเสี่ยงด้าน Requirement คู่กันอยู่ — ไม่ใช่ orphan และไม่ใช่ linked แบบไม่มีเงื่อนไขเช่นกัน

## ขั้นตอนที่ 4 — จัดการจุดที่พบ (ต้องถามผู้ใช้ ห้ามตัดสินใจเอง)

Skill นี้**ไม่มีสิทธิ์แก้ไข Test Case Workbook เด็ดขาด** (การแก้ไข Test Case เป็นหน้าที่ของ `test-case-generator`/`coverage-review` เท่านั้น) เมื่อพบจุดที่ขาดการเชื่อมโยงในขั้นตอนที่ 3 ให้รายงานทุกจุดให้ผู้ใช้เห็นก่อนเสมอ แล้วถามทีละจุดว่าจะ:

- **(a) ไปแก้ที่ต้นทาง**: กลับไปที่ `test-case-generator` (03) หรือ `coverage-review` (04) เพื่อเพิ่ม/แก้ Test Case ก่อน — ถ้าเลือกทางนี้ Skill นี้ยังไม่ปิดจบ ต้องรอให้ผู้ใช้กลับมาเมื่อแก้เสร็จแล้ว
- **(b) ยอมรับเป็นความเสี่ยงที่รู้อยู่แล้ว (Accepted Gap)**: บันทึกเหตุผลที่ผู้ใช้ให้ไว้ลงในชีต "Findings" ของ RTM โดยตรง (ไม่แตะ Workbook) แล้วดำเนินการต่อ

## ขั้นตอนที่ 5 — สร้าง RTM (`RTM-traceability-matrix.xlsx`)

ใช้สคริปต์ที่ bundle มาด้วย (`scripts/build_rtm.py`) สร้างไฟล์ Excel ที่มี 2 ชีต:

1. **ชีต "RTM"**: ตาราง Traceability เต็มรูปแบบ คอลัมน์ — Requirement/Flow ID | รายละเอียด | Test Case ID ที่ครอบคลุม | Status ปัจจุบันของแต่ละ Test Case | Priority | สถานะ Traceability (`Linked` / `Orphan Requirement` / `Requirement มี Assumption ค้าง`)
2. **ชีต "Findings"**: รายการจุดที่พบในขั้นตอนที่ 3 ทั้งหมด พร้อมผลการตัดสินใจจากขั้นตอนที่ 4 (Fix ที่ต้นทาง / Accepted Gap พร้อมเหตุผล) — คอลัมน์: Finding Type | รายละเอียด | การตัดสินใจ | เหตุผล (ถ้ามี) | วันที่

## ขั้นตอนที่ 6 — อัปเดต Manifest และรายงานสรุป

1. อัปเดต `_pipeline-manifest.md`: ตั้งค่า Stage `RTM qa-reconcile` เป็น `Complete` **เฉพาะเมื่อทุกจุดที่พบในขั้นตอนที่ 3 ถูกตัดสินใจแล้ว** (ไม่ว่าจะเป็น Fix หรือ Accepted Gap) — ถ้ายังมีจุดที่รอผู้ใช้ไปแก้ที่ต้นทางอยู่ (เลือก (a) แล้วยังไม่กลับมา) ให้ตั้งเป็น `In Progress`
2. แจ้งผู้ใช้สรุปสั้นๆ: จำนวน Orphan Requirement/Test Case ที่พบ, จำนวน Accepted Gap, Business Rule ที่ยังมี Assumption ค้าง แล้วแนะนำให้ไปต่อ `qa-report-generator` (08)

## ข้อควรระวัง

- ห้ามใช้ชีต Requirement Matrix เดิมในการสรุปผลโดยตรง — ใช้ได้แค่เปรียบเทียบเพื่อหาความไม่ตรงกัน (ดูขั้นตอนที่ 3.4)
- Orphan Test Case ไม่ใช่ปัญหาเสมอไป (อาจเป็น edge case ที่ตั้งใจเพิ่ม) — ห้ามฟันธงว่าเป็น "บั๊ก" หรือ "ผิด" ให้แค่รายงานไว้ให้ผู้ใช้ตัดสินใจเท่านั้น
- Skill นี้**ห้ามแก้ไข Test Case Workbook เด็ดขาด** ไม่ว่ากรณีใด
