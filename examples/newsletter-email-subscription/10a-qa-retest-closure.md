# QA Retest Closure — Newsletter Email Subscription

Stage: `10a qa-retest-closure` | วันที่รัน: 2026-09-19/20 | Redmine/Planio Instance: `qapipeline.plan.io` (Project: `qa-pipeline-example-newsletter-email-subscription`)

## ขั้นตอนที่ 1 — Scope

Gate ผ่าน (Stage `10 qa-retest` = Complete, มีผล Retest จริงแล้ว 1 เคส) อ่าน Workbook สดแล้วกรองเฉพาะ
เคสที่คอลัมน์ "Issue link" ไม่ว่างเปล่า พบ **1 เคส**: TC-005 (Ticket [#9](https://qapipeline.plan.io/issues/9), Status ปัจจุบันใน Workbook = `Pass`)

## ขั้นตอนที่ 2 — เช็คว่า Ticket ปิดไปแล้วหรือยัง

ผู้ใช้ระบุ Status ที่แปลว่า "ปิดแล้ว" = `Closed` — พยายามเช็คผ่าน `check_redmine_status.py` แต่เจอ network
block แบบเดียวกับ Skill 09/10 (`403 Forbidden — blocked-by-allowlist`) จึงอาศัยข้อมูลที่ทราบอยู่แล้วจากรอบ
ก่อนหน้า (Ticket #9 เป็น `Resolved` ไม่ใช่ `Closed`) สรุปได้ว่ายังไม่เคยถูกปิดมาก่อน → TC-005 อยู่ใน Scope
ที่ต้องทำในรอบนี้

## ขั้นตอนที่ 3 — Preview + Recheck

แสดง `list-preview` ให้ผู้ใช้ตรวจ Actual Result ของ TC-005 ก่อนเสมอ (ตามจุดประสงค์หลักที่แยก Skill นี้ออกมา
จาก Skill 10 — ให้มีคน Recheck ก่อนคอมเมนต์/ปิด Ticket จริงซึ่งย้อนกลับเองไม่ได้ง่ายๆ):

```
✅ Retest ผ่านแล้ว (จะคอมเมนต์ Verified + ปิด Ticket): 1 เคส
❌ Retest ยังไม่ผ่าน: 0 เคส
[✅ PASS] TC-005 · สมัครซ้ำด้วยอีเมลเดิมแต่ตัวพิมพ์เล็ก-ใหญ่ต่างกัน (Priority: P1)
```

ผู้ใช้ยืนยัน **"ยืนยันทำทั้งหมด"**

## ขั้นตอนที่ 4 — คอมเมนต์ + ปิด Ticket จริง

Text formatting = Markdown (ค่าเดิมที่ยืนยันไว้ตั้งแต่ Skill 09 ของ instance นี้) พยายามยิง
`close_redmine_issues.py apply --close-status "Closed" --syntax markdown` แต่เจอ network block เดียวกัน
(403 ตอนค้นหา Status ID ผ่าน `/issue_statuses.json`) จึงให้ผู้ใช้ทำเองผ่านหน้าเว็บ Planio โดยใช้เนื้อหาที่
เตรียมตาม Format ที่ยืนยันแล้ว (ดู `mockup-retest-closure-format.md` Format ที่ 1 — กรณี Pass):

> ✅ Retest → Pass
>
> เรื่องที่แก้ไข: TC-005 — สมัครซ้ำด้วยอีเมลเดิมแต่ตัวพิมพ์เล็ก-ใหญ่ต่างกัน
>
> **ผลการ Retest:** Pass — พฤติกรรมของระบบตรงตาม Expected Result แล้ว
> **วันที่ Retest:** 19 Sep 2026
> **ผู้ทดสอบ/ระบบ:** QA Automation Assistant
>
> 📎 แนบไฟล์ภาพผลการ Retest (Pass) ประกอบคอมเมนต์นี้

พร้อมแนบไฟล์ภาพผล Retest จริง (`screenshots/Chromium/TC-005.png`) เป็น Attachment และเปลี่ยน Status เป็น
`Closed` (แสดงเป็น "จบ" ในหน้า UI ภาษาไทยของ instance นี้ — Status ตัวเดียวกับที่ตั้งค่าไว้)

**สกรีนช็อตหน้า Ticket จริงหลังปิดสำเร็จ** (เก็บถาวรไว้ที่ `10-qa-retest-screenshots/`):

| ไฟล์ | เนื้อหา |
|---|---|
| [`02-ticket-closed-header.png`](./10-qa-retest-screenshots/02-ticket-closed-header.png) | หัว Ticket #9 — สถานะ "จบ" (Closed) |
| [`03-ticket-closed-comment-attachment.png`](./10-qa-retest-screenshots/03-ticket-closed-comment-attachment.png) | คอมเมนต์ "Retest → Pass" ตาม Format ที่ยืนยัน พร้อมไฟล์ภาพแนบ และ log "สถานะ changed from Resolved to จบ" |

**ผลลัพธ์**: `closed` = 1 เคส (TC-005), `commented` = 0 เคส, `failed` (ทาง API) = 1 เคส (เหตุ network block —
แก้ไขด้วยการทำผ่านเว็บเองแล้วสำเร็จ)

## ขั้นตอนที่ 5 — แจ้ง Dev ซ้ำทางอีเมล

**ข้าม** — ทุกเคสในรอบนี้เป็น Pass ล้วน (`commented` = 0 เคส) ไม่มีเคส Fail ที่ต้องแจ้ง Dev ซ้ำ

## ขั้นตอนที่ 6 — สรุป

- **ปิด Ticket สำเร็จ**: 1 ใบ (Ticket #9 / TC-005 — บั๊กแก้จริงแล้ว จบวงจร QA↔Dev)
- **คอมเมนต์แจ้ง Dev ซ้ำ**: 0 ใบ
- **ทำไม่สำเร็จ**: 0 ใบ (เคสเดียวที่ทำผ่าน API ไม่ได้ ทำผ่านเว็บเองสำเร็จแทน)

ไม่มีเคสไหนเหลือใน Scope ของ Skill 10/10a อีกในรอบนี้ — ถ้ามี Ticket ใหม่จาก `redmine-logging` (09) ในอนาคต
วงจร Skill 10 ↔ 10a จะกลับมาทำงานได้อีกตามปกติ (ทั้งสอง Skill idempotent อยู่แล้ว)
