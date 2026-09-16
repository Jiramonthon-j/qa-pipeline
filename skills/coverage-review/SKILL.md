---
name: coverage-review
description: ตรวจสอบว่า Test Case Workbook ของ 1 Feature ครอบคลุม Requirement และ E2E Flow ครบถ้วนหรือไม่ — หาจุดที่ตกหล่น/ซ้ำซ้อน/ขัดแย้งกัน แล้วเสนอผู้ใช้ว่าจะเพิ่ม/แก้ไข Test Case ให้เลยหรือไม่ (ไม่แก้เองแบบเงียบๆ) เป็น Skill 04 ที่บังคับของ QA Pipeline นี้ วนคู่กับ test-case-generator (Skill 03) จนกว่าผู้ใช้จะพอใจ ให้ใช้ Skill นี้ทันทีเมื่อผู้ใช้พูดถึงการตรวจสอบความครอบคลุมของ Test Case, coverage, หรือถามว่า Test Case ที่มีครบหรือยัง แม้จะไม่ได้เอ่ยชื่อ Skill ตรงๆ
---

# coverage-review

Skill นี้เป็น**ขั้นตอนที่ 4 ที่บังคับ** ของ QA Pipeline หน้าที่คือตรวจสอบว่า Test Case Workbook ที่มีอยู่ (ไม่ว่าจะสร้างจาก `test-case-generator` หรือถูกผู้ใช้แก้ไขเองด้วยมือในภายหลัง) ครอบคลุม Requirement และ E2E Flow ครบถ้วนหรือไม่ Skill นี้กับ `test-case-generator` (03) เป็นคู่ loop กัน — วนไป-กลับได้ไม่จำกัดจำนวนครั้งจนกว่าผู้ใช้จะพอใจกับความครอบคลุมของ Test Case

**สำคัญ**: คำสั่งในไฟล์นี้เขียนขึ้นให้ใช้ได้กับทั้ง Claude และ Gemini 3.6 — ห้ามอ้างอิงชื่อ tool เฉพาะของแพลตฟอร์มใดแพลตฟอร์มหนึ่ง Skill นี้ต้องใช้ environment ที่รันสคริปต์ Python ได้เพื่ออ่าน/แก้ Workbook (.xlsx) เหมือน `test-case-generator`

## ขั้นตอนที่ 1 — ระบุ Feature และตรวจสอบขั้นตอนก่อนหน้า

1. หาโฟลเดอร์รากของโปรเจค (Project Root) และโฟลเดอร์ Feature เหมือน Skill อื่นๆ ในสาย
2. อ่านไฟล์ `_pipeline-manifest.md` ของ Feature นั้น
3. **เช็ค Gate**: Skill นี้ต้องรันต่อจาก `test-case-generator` (Skill 03) เสมอ — ตรวจสอบสถานะ Stage `03 test-case-generator` (ถ้าไม่มี manifest เลยก็ถือว่ายังไม่เสร็จเช่นกัน — ต้องถามผู้ใช้เสมอ ห้ามสรุปเอาเอง):
   - **ถ้า `Complete`**: ไปต่อขั้นตอนที่ 2
   - **ถ้ายังไม่ `Complete`**: หยุดและถามผู้ใช้ว่า (a) ต้องการไปรัน `test-case-generator` ให้เสร็จก่อนไหม (แนะนำ) หรือ (b) ต้องการใช้ Skill นี้แบบ standalone — ถ้าเลือก (b) ให้ขอไฟล์ Requirement, E2E Flow, และ Test Case Workbook ที่มีอยู่แล้วมาจากผู้ใช้โดยตรงทั้งหมด (Skill นี้ต้องใช้ทั้ง 3 อย่างเพื่อเทียบกัน)
4. Test Case Workbook ของ Feature นี้เป็น Excel (.xlsx) เสมอ (`test-case-generator` ไม่รองรับ Google Sheet) ใช้ `scripts/qa_workbook.py` อ่าน/แก้ไขได้เลยไม่ต้องเช็ครูปแบบ (**หมายเหตุโครงสร้าง**: `scripts/qa_workbook.py` ของ Skill นี้เป็น stub ที่โหลดฉบับจริงจาก `qa-pipeline-skills/_shared/qa_workbook.py` มาใช้ร่วมกับอีก 4 Skill ในสาย ถ้าต้องแก้ logic ให้แก้ที่ `_shared/` ที่เดียว ห้ามแก้ stub นี้)

## ขั้นตอนที่ 2 — อ่านข้อมูลทั้งหมดที่ต้องใช้เปรียบเทียบ

**หลักการสำคัญที่สุดของ Skill นี้ — Source of Truth**: การเปรียบเทียบความครอบคลุมต้องยึด **Requirement (`01-requirement-review.md`) และ E2E Flow (`02-e2e-flow.md`) เป็นต้นทางเสมอ** ไม่ใช่ยึด Test Case ที่มีอยู่เป็นหลัก เพราะ Test Case อาจถูกผู้ใช้เพิ่ม/ลบ/แก้ไขเองด้วยมือไปแล้วหลังจาก `test-case-generator` ทำงานครั้งล่าสุด

1. อ่าน `01-requirement-review.md` และ `02-e2e-flow.md` ให้ครบทุก Business Rule และทุก Flow (รวม Alternate/Error Path)
2. อ่าน Test Case Workbook **ฉบับล่าสุดจริงๆ** ด้วยคำสั่ง (กรณี Excel):
   ```
   python3 scripts/qa_workbook.py read-cases --path "<path Workbook>"
   ```
   **ห้ามใช้ Test Case ที่ Skill `test-case-generator` เพิ่งสร้าง/แก้ไปในรอบก่อนหน้าจากความจำ** ต้องอ่านไฟล์จริงใหม่ทุกครั้ง เพราะผู้ใช้อาจแก้ไขไปแล้วระหว่างนั้น
3. อ่านชีต "Requirement Matrix" ในไฟล์เดียวกันด้วย (เปิดไฟล์ผ่าน openpyxl โดยตรงเพื่ออ่านชีตนี้ เนื่องจากสคริปต์ `read-cases` อ่านเฉพาะชีต Test Case) เพื่อดูว่าคอลัมน์ "Coverage Status" ที่บันทึกไว้ล่าสุดเป็นอย่างไร

## ขั้นตอนที่ 3 — วิเคราะห์ความครอบคลุม

ตรวจสอบทีละประเด็น:

1. **Requirement/Flow ที่ยังไม่มี Test Case รองรับเลย**: ไล่ทุก Business Rule ใน 01 และทุก Flow (รวม Alternate/Error Path) ใน 02 แล้วเช็คว่ามี Test Case อย่างน้อย 1 รายการอ้างอิงถึงหรือไม่
2. **Test Case ที่ซ้ำซ้อนกัน**: มี Test Case มากกว่า 1 รายการที่ทดสอบสถานการณ์เดียวกันทุกประการ (Pre-condition, Step, Expected Result เหมือนกันโดยไม่มีมูลค่าเพิ่ม) หรือไม่
3. **Test Case ที่ขัดแย้งกับ Requirement/Flow**: มี Test Case ใดที่ Expected Result เขียนไว้ไม่ตรงกับที่ Requirement/E2E Flow ระบุหรือไม่ (เช่น สมมติฐานที่เคยตั้งไว้ตอนสร้าง Test Case ผิดพลาด)
4. **Test Case ที่อ้างอิง Open Question ที่ตอนนี้มีคำตอบแล้ว**: ถ้า `01`/`02` มีการอัปเดต Open Question ให้มีคำตอบชัดเจนแล้วหลังจากที่ Test Case ถูกสร้างด้วยสมมติฐาน ให้สังเกตว่า Test Case นั้นควรถูกปรับปรุงคำตอบที่คาดหวัง (Expected Result) ให้ตรงกับคำตอบจริงหรือไม่

## ขั้นตอนที่ 4 — รายงานผลและถามผู้ใช้ก่อนแก้ไข

**ห้ามแก้ไข Test Case Workbook เองแบบเงียบๆ** ให้สรุปสิ่งที่พบทั้งหมดให้ผู้ใช้เห็นก่อนเสมอ (จุดที่ตกหล่น/ซ้ำซ้อน/ขัดแย้ง แต่ละจุดพร้อมเหตุผลสั้นๆ) แล้วถามผู้ใช้ทีละจุดหรือรวมเป็นชุดก็ได้ว่า:
- ต้องการให้เพิ่ม Test Case ที่ขาดหายไปเลยไหม (ถ้าใช่ Skill นี้จะออกแบบ Test Case เพิ่มด้วยหลักการเดียวกับ `test-case-generator` ขั้นตอนที่ 3 แล้วเพิ่มเข้า Workbook)
- ต้องการให้ลบ/รวม Test Case ที่ซ้ำซ้อนกันไหม
- ต้องการให้แก้ไข Test Case ที่ขัดแย้งกับ Requirement/Flow ไหม
- หรือจุดใดที่ผู้ใช้ตั้งใจปล่อยไว้แบบนั้น (Deferred/Rejected) ไม่ต้องแก้ตอนนี้

## ขั้นตอนที่ 5 — แก้ไข Workbook ตามที่ผู้ใช้ยืนยัน

สำหรับทุกจุดที่ผู้ใช้ยืนยันให้แก้ (กรณี Excel):
- **เพิ่ม Test Case ใหม่**: เตรียมไฟล์ JSON แล้วรัน `python3 scripts/qa_workbook.py add-cases --path "<path>" --cases-json "<path .json>" --editor "coverage-review" --note "<สรุปว่าเพิ่มอะไรและทำไม>"` — ใช้ Test Case ID ต่อจากตัวสุดท้ายที่มีอยู่จริง (จากขั้นตอนที่ 2)
- **แก้ไขค่าของ Test Case ที่มีอยู่ (เช่น Expected Result)**: รัน `python3 scripts/qa_workbook.py update-field --path "<path>" --tc-id "<ID>" --field "<ชื่อคอลัมน์>" --value "<ค่าใหม่>" --editor "coverage-review" --note "<เหตุผล>"`
- **ลบ Test Case ที่ซ้ำซ้อน**: สคริปต์ยังไม่มีคำสั่งลบแถวโดยตรง ให้แจ้งผู้ใช้และลบแถวออกจากไฟล์ Excel ด้วยตนเอง (เปิดไฟล์ผ่าน openpyxl โดยตรง) แล้ว**ต้อง bump version ด้วยคำสั่ง `python3 scripts/qa_workbook.py bump --path "<path>" --editor "coverage-review" --note "<สรุปว่าลบ Test Case ID อะไรและทำไม>"` เองด้วย** เพราะการลบแถวไม่ผ่านคำสั่ง `add-cases`/`update-field` ที่ bump ให้อัตโนมัติ — **ข้อควรระวังสำคัญ**: `ws.delete_rows()` ของ openpyxl ย้ายค่าในเซลล์ขึ้นมาให้ถูกต้อง แต่**ไม่ย้ายความสูงแถว** (`row_dimensions`) ตามไปด้วย ทำให้แถวที่เลื่อนขึ้นมาแทนที่อาจสืบทอดความสูงเก่าที่ผิดของแถวเดิมที่เคยอยู่ตรงนั้นมาแบบเงียบๆ (ข้อความอาจโดนตัดในโปรแกรม Excel จริงโดยที่ผู้ใช้ไม่รู้ตัว)

ทุกครั้งที่แก้ไข Workbook ให้อัปเดตคอลัมน์ "Coverage Status" ในชีต Requirement Matrix ให้ตรงกับสถานะล่าสุดด้วย (Covered / Partial / Not Covered)

**หลังแก้ไขเซลล์ด้วยมือผ่าน openpyxl ตรงๆ ในขั้นตอนนี้ไม่ว่ากรณีไหนก็ตาม** (อัปเดต Coverage Status, ลบแถวซ้ำซ้อน, หรือแก้ไขอื่นใดที่ไม่ผ่านคำสั่ง `add-cases`/`update-field`/`update-fields-batch` ของสคริปต์) **ต้องรันคำสั่งนี้เป็นขั้นตอนสุดท้ายเสมอ** ก่อนไปขั้นตอนที่ 6:
```
python3 scripts/qa_workbook.py finalize-layout --path "<path Workbook>"
```
เพื่อจัดกรอบ/wrap/ความสูงแถวให้ถูกต้องใหม่ทั้งไฟล์ (คำสั่ง `add-cases`/`update-field`/`update-fields-batch` เรียกให้อัตโนมัติอยู่แล้ว จึงไม่ต้องเรียกซ้ำหลังใช้คำสั่งเหล่านั้น — เรียกเองเฉพาะตอนแก้เซลล์ตรงๆ แบบนี้เท่านั้น) ถ้าข้ามขั้นตอนนี้ไป แถวที่เพิ่งแก้/ลบจะดูไม่สม่ำเสมอกับแถวอื่นในไฟล์ (ไม่มีกรอบ, ความสูงไม่ตรงกับเนื้อหาจริง) ซึ่งมักมองไม่เห็นตอนดูผ่าน PDF/LibreOffice preview แต่เห็นชัดเวลาเปิดใน Excel จริง

## ขั้นตอนที่ 6 — เขียนรายงานและอัปเดต Manifest

สร้างไฟล์ `<โฟลเดอร์ Feature>/04-coverage-review.md` สรุปทุกจุดที่ตรวจพบในขั้นตอนที่ 3 พร้อมสถานะการตัดสินใจของผู้ใช้ต่อแต่ละจุด (Fixed / Deferred / Rejected) ตามโครงสร้าง:

```
# Coverage Review — <ชื่อ Feature>

Created: <วันที่>
Test Case Workbook เวอร์ชันที่ตรวจ: <Version จาก Document Control ตอนเริ่มตรวจ>

## จุดที่ตรวจพบ
### 1. <หัวข้อจุดที่พบ>
รายละเอียด: ...
สถานะ: Fixed / Deferred / Rejected
<ถ้า Fixed ระบุ Test Case ID ที่เพิ่ม/แก้ไป>

### 2. ...

## สรุป Coverage
<สรุปว่า Requirement/Flow ทั้งหมดกี่ข้อ ครอบคลุมแล้วกี่ข้อ (Covered/Partial/Not Covered)>

## คำแนะนำ
<แนะนำผู้ใช้ว่าพร้อมไปต่อ risk-analysis (05) ได้เลย หรือควรวนกลับไป test-case-generator (03) อีกรอบก่อน>
```

อัปเดต `_pipeline-manifest.md`: ตั้งค่า Stage `04 coverage-review` เป็น `Complete`, ใส่ path ของไฟล์ output, ใส่วันที่เสร็จ — **หมายเหตุ**: ถ้าผู้ใช้ยังไม่พอใจและต้องการวนกลับไป `test-case-generator` อีกรอบ ให้ตั้งสถานะ `03 test-case-generator` และ `04 coverage-review` กลับเป็น `In Progress` แทน จนกว่าผู้ใช้จะยืนยันว่าพอใจแล้วในรอบสุดท้ายจึงตั้งเป็น `Complete` ทั้งคู่

## ข้อควรระวัง

- ห้ามแก้ไข Test Case Workbook เองโดยไม่ถามผู้ใช้ก่อนเด็ดขาด แม้จะมั่นใจว่าจุดที่พบเป็นปัญหาจริงก็ตาม
- ถ้า manifest ระบุว่า `test-case-generator` สถานะ `In Progress` ห้ามอ่านไฟล์มาใช้ทันทีเหมือนเป็นข้อมูลสมบูรณ์ ให้เตือนผู้ใช้ก่อนเหมือน Skill ก่อนหน้า
- Loop กับ `test-case-generator` ไม่ได้ถูกจำกัดจำนวนรอบ — วนไปเรื่อยๆ จนกว่าผู้ใช้จะพอใจ ห้ามเร่งรัดหรือสรุปว่า "ครอบคลุมพอแล้ว" แทนผู้ใช้เอง
- เครื่องหมายคำพูดในข้อความที่เขียนเข้า Workbook (เช่นตอนอัปเดต Expected Result หรือ Coverage Status) เขียนตามธรรมชาติได้เลย ไม่ต้องกังวลเรื่อง `'` เดี่ยว vs `"` คู่ — `add-cases`/`update-field`/`finalize-layout` normalize ให้เป็น `"` คู่ทั้งหมดอัตโนมัติอยู่แล้ว (ยกเว้นในสูตร Excel ที่อ้างอิงชื่อชีต ซึ่งสคริปต์แยกแยะให้แล้ว)
