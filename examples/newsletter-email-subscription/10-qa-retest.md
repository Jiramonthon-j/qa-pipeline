# QA Retest — Newsletter Email Subscription

Stage: `10 qa-retest` | วันที่รัน: 2026-09-19 | Redmine/Planio Instance: `qapipeline.plan.io` (Project: `qa-pipeline-example-newsletter-email-subscription`)

## ขั้นตอนที่ 1 — Scope

Gate ผ่าน (Stage `09 redmine-logging` = Complete) อ่าน Test Case Workbook สดแล้วกรองด้วยเงื่อนไข
`Status = "Fail"` และ "Issue link" ไม่ว่างเปล่า พบ **1 เคส**: TC-005 (P1, Ticket
[#9](https://qapipeline.plan.io/issues/9))

## ขั้นตอนที่ 2 — เช็ค Status/Comment จาก Redmine จริง

ผู้ใช้ยืนยัน Redmine Status ที่นับว่า "แก้เสร็จแล้ว พร้อม Retest" = `Resolved`

พยายามเช็คผ่าน `check_redmine_status.py check` ด้วย API แต่เจอ network block แบบเดียวกับ Skill 09
(`403 Forbidden — blocked-by-allowlist` จาก network proxy กลางของ environment ไม่ใช่ปัญหา
credential/Redmine) ทั้งก่อนและหลังผู้ใช้อัปเดต Ticket — จึงให้ผู้ใช้ยืนยัน Status/Comment จริงที่เห็นใน
เบราว์เซอร์แทน (ตามที่แจ้งไว้ล่วงหน้าตั้งแต่ก่อนเริ่ม Skill นี้)

**ผลจริงที่ผู้ใช้ยืนยัน**: Ticket #9 เปลี่ยนจาก `Open` → **`Resolved`** พร้อมคอมเมนต์จาก Dev (เตรียม
เนื้อหาให้ผู้ใช้นำไปโพสต์เองใน Planio เพื่อให้ audit trail เป็นข้อมูลจริงใน Redmine ไม่ใช่ mock):

> แก้ไขแล้วครับ
>
> Root Cause: ฟังก์ชันเช็คอีเมลซ้ำ (BR-002) เดิมเทียบแบบ exact-match (case-sensitive) เลยทำให้
> "Dup02@Example.com" สมัครซ้ำกับ "dup02@example.com" ที่มีอยู่แล้วได้
>
> Fix: เปลี่ยนมาเทียบอีเมลแบบ case-insensitive (.lower() ทั้งสองฝั่งก่อนเทียบ) ในฟังก์ชันตรวจสอบอีเมลซ้ำ
> ก่อนบันทึกลง subscriber list ไม่กระทบ Business Rule อื่น (ยังเก็บอีเมลตามที่ผู้ใช้กรอกจริงไว้เหมือนเดิม)
>
> Test Data เดิม (dup02@example.com / Dup02@Example.com) ยังใช้ทดสอบซ้ำได้เลย ไม่ต้องเปลี่ยนค่าใหม่
> รบกวน QA ช่วย Retest ให้หน่อยครับ

**สกรีนช็อตหน้า Ticket จริงหลังอัปเดต** (เก็บถาวรไว้ที่ `10-qa-retest-screenshots/` เพื่อเป็นหลักฐานที่ไม่
ขึ้นกับว่า Planio instance นี้ยังใช้งานได้อยู่ไหมในอนาคต เช่นกรณี free trial หมดอายุ — เหตุผลเดียวกับที่ทำใน
Skill 09):

| ไฟล์ | เนื้อหา |
|---|---|
| [`01-ticket-resolved-dev-comment.png`](./10-qa-retest-screenshots/01-ticket-resolved-dev-comment.png) | Ticket #9 หลังอัปเดตจริง — สถานะเปลี่ยนจาก `Open` เป็น `Resolved` พร้อมคอมเมนต์ Dev (Root Cause/Fix/Test Data) ตามเนื้อหาด้านบนเป๊ะๆ |

→ TC-005 จัดอยู่ในกลุ่ม `ready`

## ขั้นตอนที่ 3 — วิเคราะห์ Comment ของ Dev

Comment ของ Dev ระบุชัดเจนว่าแก้ที่ Logic โค้ด (case-insensitive comparison) เท่านั้น ไม่ได้เปลี่ยน
เงื่อนไข/ค่าที่ Test Case ต้องใช้ทดสอบ และ Dev เองก็ยืนยันตรงๆ ว่า Test Data เดิมยังใช้ได้

**Decision**: TC-005 = **(A) same_data** — ใช้ Test Data เดิม (`seed=dup02@example.com`,
กรอกทดสอบ=`Dup02@Example.com`) ไม่ต้องแก้ทั้ง Workbook และ `automation/TC-005.py`

## ขั้นตอนที่ 4 — ปรับ Test Data

ไม่มีเคสกรณี (B) ในรอบนี้ — ข้ามขั้นตอนนี้ทั้งหมดตามกฎของ Skill (TC-005 เป็นกรณี A)

เพื่อให้ Automation รันกับระบบที่ "แก้ไขแล้วจริง" (ไม่ใช่แค่ mock ผลลัพธ์) จึงแก้บั๊กจริงใน
`demo-app/server.py` ให้ตรงกับที่ Dev อธิบายในคอมเมนต์ — ฟังก์ชัน `subscribe()` เปลี่ยนจากเทียบอีเมล
ซ้ำแบบ exact-match เป็น case-insensitive (`cleaned.lower() == existing.lower()`) เพื่อให้ Playwright
รันเจอผล Pass/Fail จริงจากระบบจริงเหมือนทุก Stage ที่ผ่านมา ไม่ใช่ hardcode ผลไว้ล่วงหน้า

## ขั้นตอนที่ 5 — Retest ด้วย Playwright จริง

- **Browser**: รันเฉพาะ **Chromium** เท่านั้น (environment นี้ยังไม่มี Safari/Firefox/Edge ติดตั้งอยู่ ข้อจำกัด
  เดียวกับ Stage 06a/07 — ยังไม่ปิด OQ-03)
- เก็บ Screenshot เดิม (ผล Fail ก่อน Retest) ไว้ที่
  [`screenshots/Chromium/_history/TC-005_2026-09-19-pre-retest.png`](./screenshots/Chromium/_history/TC-005_2026-09-19-pre-retest.png)
  ก่อนรันทับ
- รันด้วย runner กลางตัวเดียวกับ Skill 06a (`run_automation.py --tc TC-005 --browser chromium`)

**ผลลัพธ์**: `Pass` — ระบบแสดง error `"อีเมลนี้สมัครรับข่าวสารไปแล้ว"` แบบ inline ถูกต้องเมื่อกรอก
`Dup02@Example.com` ซ้ำกับ `dup02@example.com` ที่สมัครไปแล้ว (ดูภาพ
[`screenshots/Chromium/TC-005.png`](./screenshots/Chromium/TC-005.png) — วงเขียวรอบข้อความ error ที่ถูกต้องแล้ว)

## ขั้นตอนที่ 6 — บันทึกผลกลับ Workbook

อัปเดต `03-test-case-workbook.xlsx` ด้วย `qa_workbook.py update-fields-batch` ครั้งเดียว (Document
Control Version History เป็น **Version 6**, Editor: `qa-retest`):

| คอลัมน์ | ค่าเดิม | ค่าใหม่ |
|---|---|---|
| Status | Fail | **Pass** |
| Actual Result | (ผล Fail จาก 06a) | ผล Pass พร้อมอ้างอิง Ticket #9 |
| Remarks | — | Retest ผ่านหลัง Dev แก้ไข Ticket #9 (Resolved) — same_data |
| Execution Date | 2026-09-19 (06a) | 2026-09-19 (Retest) |
| Test Photo | `screenshots/Chromium/TC-005.png` (ตอน Fail) | ว่างเปล่า (ไม่ชี้ภาพเก่าที่ไม่ตรงผลปัจจุบันแล้ว ตามกฎ Skill นี้) |

**ไม่แตะคอลัมน์ "Issue link"** ตามกฎของ Skill นี้ — ยังคงชี้ไปที่ Ticket #9 เหมือนเดิม (การคอมเมนต์กลับ/
ปิด Ticket เป็นหน้าที่ของ `qa-retest-closure` (10a) ต่อไป)

## สรุป

- **Pass แล้ว**: 1 เคส (TC-005 — บั๊กถูกแก้จริงตาม RISK-001)
- **ยัง Fail**: 0 เคส
- **ยังรอ Dev**: 0 เคส
- **รอผู้ใช้ตัดสินใจ (Comment กำกวม)**: 0 เคส

Retest ครบทุกเคสใน `ready` แล้ว → Stage `10 qa-retest` = **Complete**

ขั้นตอนถัดไป: ไปที่ `qa-retest-closure` (Skill 10a) เพื่อ Recheck ผลนี้แล้วคอมเมนต์กลับ/ปิด Ticket #9 ใน
Redmine จริงต่อไป (Skill นี้ไม่แตะ Redmine เลยตามการออกแบบ)
