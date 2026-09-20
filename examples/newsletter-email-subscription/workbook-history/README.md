# ประวัติ Test Case Workbook แยกไฟล์ตาม Skill

โฟลเดอร์นี้เก็บ **สำเนาของ `03-test-case-workbook.xlsx` ณ จุดต่างๆ ในสาย Pipeline** เพื่อให้เปิดไฟล์
เทียบกัน (ก่อน/หลังแต่ละ Skill) ได้ตรงๆ โดยไม่ต้องคำนวณเอง — ไฟล์หลักที่ Pipeline ใช้งานจริงต่อเนื่องอยู่
ที่ `../03-test-case-workbook.xlsx` (ไฟล์ live ที่ทุก Skill อ่าน/เขียนจริง) ไฟล์ในนี้เป็น**สำเนานิ่ง**สำหรับ
ดูย้อนหลังเท่านั้น ไม่ถูกแก้ไขต่อ

| ไฟล์ | สร้างขึ้นหลัง Skill | สิ่งที่เปลี่ยนจากไฟล์ก่อนหน้า |
|---|---|---|
| `v1-after-03-create.xlsx` | `test-case-generator` (03) — ขั้นตอน `create` | สร้าง Workbook เปล่า มีแค่โครงชีตทั้ง 7 ชีต ยังไม่มี Test Case เลย |
| `v2-after-03-test-case-generator.xlsx` | `test-case-generator` (03) — ขั้นตอน `add-cases` | เพิ่ม Test Case ครบ 11 เคส (TC-001–TC-011) — คอลัมน์ Priority ยังว่างอยู่ (ยังไม่ถึงคิว `risk-analysis`), Status ทุกแถวเป็น `not start` |
| `v2-after-04-coverage-review-no-change.xlsx` | `coverage-review` (04) | **เหมือน v2 ทุกไบต์** — Skill 04 ตรวจพบ 2 ประเด็น (ดู `../04-coverage-review.md`) แต่ผู้ใช้เลือก Defer/Keep-as-is ทั้งคู่ จึงไม่มีการแก้ Workbook จริงรอบนี้ (พิสูจน์ได้ด้วยการ diff กับ v2 แล้วจะไม่ต่างกันเลย) |
| `v3-after-05-risk-analysis.xlsx` | `risk-analysis` (05) | เติมคอลัมน์ **Priority** ให้ครบทั้ง 11 เคส (P0–P3) — คอลัมน์อื่นเหมือน v2 ทุกอย่าง |
| `v3-after-06-test-data-generator-no-change.xlsx` | `test-data-generator` (06) | **เหมือน v3 ทุกไบต์** — Skill 06 ผลิตแผน Mock Data เป็นไฟล์แยก (`../06-test-data.md`) เท่านั้น ไม่แตะ Workbook เลยตามการออกแบบ (ค่าจริงจะถูกใส่กลับตอน 06a) |
| `v4-after-06a-qa-automation-script.xlsx` | `qa-automation-script` (06a) | รัน Playwright Automation จริง — เติม **Status, Actual Result, Test Data (ค่าจริงที่ใช้รัน), Remarks (เพิ่มผลจริง), Execution Date, Test By, Test Photo** ครบทุกเคส — TC-005 ได้ผล **Fail** จริงตาม RISK-001, ที่เหลือ Pass — ไฟล์นี้เหมือนกับ `../03-test-case-workbook.xlsx` (ไฟล์ live) ณ ตอนที่ copy มา |
| `v5-after-09-redmine-logging.xlsx` | `redmine-logging` (09) | เติมคอลัมน์ **Issue link** ของ TC-005 เป็น `https://qapipeline.plan.io/issues/9` (Ticket จริงที่เปิดใน Planio) — คอลัมน์อื่นเหมือน v4 ทุกอย่าง รวมถึงยังมีรูป TC-005 (Fail) ฝังอยู่ในคอลัมน์ Test Photo เหมือนเดิม |
| `v6-after-10-qa-retest.xlsx` | `qa-retest` (10) | Retest TC-005 จริงด้วย Playwright หลัง Dev แก้บั๊ก — **Status เปลี่ยนจาก Fail เป็น Pass**, อัปเดต Actual Result/Remarks/Execution Date ใหม่ และ**ลบรูปออกจากคอลัมน์ Test Photo** (กฎของ Skill นี้: ใส่รูปเฉพาะเคสที่ยัง Fail อยู่เท่านั้น) สังเกตได้ว่าไฟล์นี้เล็กลงกว่า v5 ชัดเจนเพราะไม่มีรูปฝังแล้ว — คอลัมน์ Issue link ไม่ถูกแตะ (Skill 10 ไม่ยุ่งกับคอลัมน์นี้) |

## วิธีดูความต่างเร็วๆ

เปิด 2 ไฟล์เทียบกันในคนละหน้าต่าง Excel แล้วดูชีต **"Test Case"** เป็นหลัก (คอลัมน์ที่เปลี่ยนจะสังเกต
ง่ายเพราะสีพื้นหลัง Priority/Status เปลี่ยนไปตามค่า) หรือถ้าอยากดูสรุปเป็นข้อความ ให้เปิดชีต
**"Document Control"** ของไฟล์ปลายทาง (`../03-test-case-workbook.xlsx`) — มีตาราง Version History
บอกครบว่า Version ไหนแก้โดย Skill ไหน เปลี่ยนอะไรบ้าง

ไฟล์ที่ต่อท้ายด้วย `-no-change` ตั้งใจให้เหมือนไฟล์ก่อนหน้าทุกไบต์ — เป็นหลักฐานว่า Skill นั้น**ถูกใช้งาน
จริง** (มีการตรวจสอบ/ประมวลผลเกิดขึ้นจริง อ่านรายละเอียดได้ในไฟล์ผลลัพธ์ของ Skill นั้นๆ) แต่ผลลัพธ์ของรอบ
นี้ตัดสินใจว่าไม่ต้องแก้ Workbook — ไม่ใช่ไฟล์ที่ลืมอัปเดต
