# Redmine Bug Logging — Newsletter Email Subscription

Stage: `09 redmine-logging` | วันที่รัน: 2026-09-19 | Redmine/Planio Instance: `qapipeline.plan.io` (Project: `qa-pipeline-example-newsletter-email-subscription`)

> **หมายเหตุเรื่องวิธีสร้าง Ticket จริงรอบนี้**: cloud sandbox และเครื่องของผู้ใช้ (ผ่าน device bridge) ทั้งคู่เชื่อมต่อ
> `qapipeline.plan.io` ไม่ได้ (เจอ `403 Forbidden — blocked-by-allowlist` จาก network proxy กลางของระบบ ไม่ใช่ปัญหาจาก
> Redmine/Planio หรือ credential ผิด) เป็น network egress allowlist ระดับ Organization ที่จำกัดโดเมนที่ Claude
> เข้าถึงได้โดยตรง — ผู้ใช้จึงสร้าง Ticket เองผ่านหน้าเว็บ Planio โดยใช้ Subject/Description ที่เตรียมไว้ให้ตาม Format
> มาตรฐานของ Skill นี้ทุกประการ (Markdown, เรียง field ตามลำดับที่กำหนด) ผลลัพธ์จึงเทียบเท่ากับที่สคริปต์
> `create_redmine_issues.py create` จะสร้างให้ทุกประการ เพียงแค่เปลี่ยนจาก "Claude ยิง API เอง" เป็น "ผู้ใช้กดสร้างเอง
> ตามเนื้อหาที่ Claude เตรียมให้"

## ✅ เปิด Ticket สำเร็จ (1 เคส)

| Test Case ID | Priority | Ticket | วันที่เปิด |
|---|---|---|---|
| TC-005 | P1 | [#9 — qapipeline.plan.io/issues/9](https://qapipeline.plan.io/issues/9) | 2026-09-19 |

**Subject**: `[P1] TC-005: สมัครซ้ำด้วยอีเมลเดิมแต่ตัวพิมพ์เล็ก-ใหญ่ต่างกัน`

**สรุปบั๊ก**: ระบบยอมให้สมัครรับข่าวสารซ้ำได้ด้วยอีเมลที่ต่างแค่ตัวพิมพ์เล็ก-ใหญ่ (`Dup02@Example.com` ซ้ำกับ
`dup02@example.com` ที่สมัครไปแล้ว) แทนที่จะแสดง error ตามที่คาดหวัง — Root Cause คือระบบเช็คอีเมลซ้ำแบบ
exact-match (case-sensitive) ตาม BR-002 ปัจจุบัน (อ้างอิง RISK-001 High จาก `01-requirement-review.md`)

**หลักฐาน**: `../evidence/06a-automation/TC-005.png` (ดูรูปเต็มใน `07-photo-evidence.docx` หน้า TC-005) — วงกลมสีแดง
รอบข้อความ "สมัครรับข่าวสารสำเร็จ" ที่ไม่ควรขึ้น

**สกรีนช็อตหน้า Ticket จริงที่เปิดสำเร็จ** (เก็บถาวรไว้ในโฟลเดอร์ `../evidence/09-redmine-ticket/` เพื่อเป็นหลักฐาน
ที่ไม่ขึ้นกับว่า Planio instance นี้ยังใช้งานได้อยู่ไหมในอนาคต เช่นกรณี free trial หมดอายุ):

| ไฟล์ | เนื้อหา |
|---|---|
| [`01-ticket-header.png`](../evidence/09-redmine-ticket/01-ticket-header.png) | หัว Ticket #9 — Subject, สถานะ Open, Priority ปกติ, วันที่เพิ่ม |
| [`02-ticket-description.png`](../evidence/09-redmine-ticket/02-ticket-description.png) | เนื้อหา Description ที่ render จาก Markdown จริง (Priority/Test Case ID/Module/Environment/Steps/Test Data/Expected/Actual/Root Cause) |
| [`03-ticket-attached-screenshot.png`](../evidence/09-redmine-ticket/03-ticket-attached-screenshot.png) | ภาพหลักฐาน TC-005.png ที่แนบไว้ใน Ticket — เห็นวงกลมแดงรอบข้อความ "สมัครรับข่าวสารสำเร็จ" ที่ไม่ควรขึ้น |
| [`04-ticket-attachments-list.png`](../evidence/09-redmine-ticket/04-ticket-attachments-list.png) | รายการไฟล์แนบ + ลิงก์อ้างอิงกลับ Workbook ท้าย Ticket |

## ⏭ ข้าม (0 เคส)

ไม่มี Test Case ใดที่มีค่าในคอลัมน์ "Issue link" อยู่แล้วก่อนรอบนี้

## ❌ Failed (0 เคส)

ไม่มี — Ticket ที่ต้องเปิดตามรอบนี้ (Test Case ที่ Status = Fail) มีแค่ 1 เคส (TC-005) และเปิดสำเร็จครบ

## Workbook

บันทึกลิงก์ Ticket กลับเข้า `../workbook/03-test-case-workbook.xlsx` คอลัมน์ "Issue link" ของ TC-005 แล้ว ผ่าน
`qa_workbook.py update-fields-batch` (Document Control Version History อัปเดตเป็น **Version 5**, Editor:
`redmine-logging`)

## Email แจ้งเตือน Developer

ผู้ใช้เปลี่ยนใจภายหลังขอให้ส่งอีเมลแจ้งเตือนจริง — ประกอบเนื้อหา (Subject + Body) ผ่าน
`send_email_notification.py build-body` สำเร็จตาม Format มาตรฐานของ Skill นี้ แต่ **ส่งผ่าน SMTP อัตโนมัติไม่สำเร็จ**
ทั้งจาก cloud sandbox (raw TCP connect timeout ไปที่ `smtp.gmail.com:587`) และจากเครื่องผู้ใช้ผ่าน device bridge
(`Temporary failure in name resolution`) — ยืนยันแล้วว่าเป็นข้อจำกัด network egress ของ environment ทั้งสองฝั่ง
(อนุญาตแค่ HTTP(S) ผ่าน proxy ไม่รองรับ raw TCP/SMTP เลย) **ไม่ใช่ปัญหา credential ผิด** ตรงตามที่ SKILL.md เตือนไว้
ล่วงหน้า

**ผลลัพธ์**: ผู้ใช้ส่งอีเมลนี้เองโดยตรงจาก Gmail ของตนเองแทน โดยใช้เนื้อหาที่เตรียมไว้ให้ทุกประการ (Subject:
`[QA] Bug Report Summary — 1 Ticket(s) Opened`, To: `jiramonthon.j@gmail.com`) — ส่งสำเร็จแล้ว ยืนยันด้วย
สกรีนช็อตอีเมลจริงที่ส่งถึง `jiramonthon.j@gmail.com`:
[`05-dev-notification-email-sent.png`](../evidence/09-redmine-ticket/05-dev-notification-email-sent.png)
