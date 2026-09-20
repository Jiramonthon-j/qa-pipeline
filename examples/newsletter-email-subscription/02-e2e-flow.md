# FLOW-20260919-001: Newsletter Email Subscription

## 1. สรุปสำหรับ QA

| หัวข้อ | รายละเอียด |
|---|---|
| จำนวน Flow | 2 (1 Main, 1 Supporting) — ไม่มี Flow แยกสำหรับ Error เพราะ Error Path ทั้งหมดเป็นเส้นทางแยกจาก Decision Point ภายใน FLOW-001 เดียวกัน |
| จำนวน Decision Point | 2 (DP-001, DP-002) |
| Coverage REQ-F/REQ-NF/AC | REQ-F ครบ 5/5, REQ-NF ครบ 4/4 (2 ข้อเป็น cross-cutting ⚠️), AC ครบ 5/5 |
| จำนวน Open Questions | 4 (3 carried-forward จาก Requirement Review, 1 ข้อสังเกตใหม่ที่เจอตอนแตก Flow) |
| จุดที่ควรอ่านก่อนเป็นพิเศษ | DP-002 — จุดเดียวที่ RISK-001 (ระดับ High จาก Requirement Review) ส่งผลกระทบโดยตรงต่อพฤติกรรมจริงของระบบ |
| ต้นทาง | `01-requirement-review.md` (Complete) |
| Test Plan | มี — `testplans/TP-20260919-001-newsletter-email-subscription.md` (Pending Review) |

## 2. ภาพรวม Flow ทั้งหมด

| Flow ID | ชื่อ | ประเภท | ครอบคลุม REQ-F/AC |
|---|---|---|---|
| FLOW-001 | สมัครรับข่าวสารทางอีเมล | Main (รวม Error Path ผ่าน Decision Point) | REQ-F-001, REQ-F-002, REQ-F-003, REQ-F-004 / AC-001, AC-002, AC-003, AC-004 |
| FLOW-002 | ป้องกันกดปุ่มสมัครซ้ำระหว่างประมวลผล | Supporting | REQ-F-005 / AC-005 |

## FLOW-001: สมัครรับข่าวสารทางอีเมล

**ประเภท: Main**

ครอบคลุม: REQ-F-001, REQ-F-002, REQ-F-003, REQ-F-004, BR-001, BR-002, BR-003, AC-001, AC-002, AC-003, AC-004

> รวม Happy Path และ Error Path ทั้งหมดไว้ใน Flow เดียว เพราะทุกเส้นทางมี Actor/Trigger/Pre-condition เดียวกัน (ผู้ใช้กดปุ่ม "สมัครรับข่าวสาร" จาก Footer) ต่างกันแค่ผลของ Decision Point ระหว่างทาง จึงไม่แยกเป็นคนละ Flow

**Actor**: ผู้เข้าชมเว็บไซต์ทั่วไป (ไม่ต้อง Login)

**Trigger**: ผู้ใช้กดปุ่ม "สมัครรับข่าวสาร" ใน Footer

**Pre-conditions**: หน้าเว็บที่มี Footer widget โหลดสำเร็จ และช่อง input "อีเมลของคุณ" อยู่ในสถานะพร้อมใช้งาน (ไม่ได้ถูก disable จาก FLOW-002)

**แผนผัง Flow**
1. ผู้ใช้กรอกอีเมลในช่อง input
2. ผู้ใช้กดปุ่ม "สมัครรับข่าวสาร"
3. DP-001: อีเมลอยู่ในรูปแบบมาตรฐานหรือไม่ → **No** ไป Error Path A (ขั้นที่ 4A) / **Yes** ไปขั้นที่ 4
4. DP-002: อีเมลนี้เคยสมัครไปแล้วหรือไม่ (เช็คแบบ exact match ตาม BR-002) → **Yes** ไป Error Path B (ขั้นที่ 4B) / **No** ไปขั้นที่ 5
5. ระบบบันทึกอีเมลลง subscriber และแสดงข้อความสำเร็จ

**ตาราง Step**

| Step | Actor | การกระทำ/ผลลัพธ์ของระบบ | System/API Touchpoint | อ้างอิง (REQ-F/BR/AC) |
|---|---|---|---|---|
| 1 | ผู้ใช้ | กรอกอีเมลในช่อง input "อีเมลของคุณ" | Client-side form | REQ-F-001 |
| 2 | ผู้ใช้ | กดปุ่ม "สมัครรับข่าวสาร" | Client-side form submit | REQ-F-001 |
| 3 (DP-001) | ระบบ | ตรวจรูปแบบอีเมล (มี `@` และโดเมน) | Client/Server-side validation | REQ-F-002, BR-001 |
| 4 (DP-002) | ระบบ | ถ้ารูปแบบถูกต้อง ตรวจว่าอีเมลนี้เคยอยู่ใน subscriber แล้วหรือไม่ (exact match) | Subscriber database lookup | REQ-F-003, BR-002 |
| 5 | ระบบ | ถ้ายังไม่เคยสมัคร บันทึกอีเมลใหม่ลง subscriber | Subscriber database write | REQ-F-004, BR-003 |
| 6 | ระบบ | แสดงข้อความ "สมัครรับข่าวสารสำเร็จ ขอบคุณที่ติดตามเรา" แบบ inline ใต้ปุ่ม | Client-side UI | REQ-F-004, REQ-NF-001, AC-004 |

**ตาราง Step (เส้นทางย่อย A — รูปแบบอีเมลไม่ถูกต้อง)**

| Step | Actor | การกระทำ/ผลลัพธ์ของระบบ | System/API Touchpoint | อ้างอิง (REQ-F/BR/AC) |
|---|---|---|---|---|
| 4A | ระบบ | ตรวจพบว่ารูปแบบอีเมลไม่ถูกต้อง (DP-001 = No) | Client/Server-side validation | REQ-F-002, BR-001 |
| 5A | ระบบ | แสดง error "กรุณากรอกอีเมลให้ถูกต้อง" แบบ inline ใต้ปุ่ม ไม่บันทึกข้อมูล | Client-side UI | REQ-F-002, REQ-NF-001, AC-002 |

**ตาราง Step (เส้นทางย่อย B — อีเมลสมัครซ้ำ)**

| Step | Actor | การกระทำ/ผลลัพธ์ของระบบ | System/API Touchpoint | อ้างอิง (REQ-F/BR/AC) |
|---|---|---|---|---|
| 4B | ระบบ | ตรวจพบว่าอีเมลนี้ตรงกับ subscriber ที่มีอยู่แล้วแบบ exact match (DP-002 = Yes) | Subscriber database lookup | REQ-F-003, BR-002 |
| 5B | ระบบ | แสดง error "อีเมลนี้สมัครรับข่าวสารไปแล้ว" แบบ inline ใต้ปุ่ม ไม่บันทึกซ้ำ | Client-side UI | REQ-F-003, REQ-NF-001, AC-003 |

**Post-condition / End State**: เส้นทางหลัก (Step 6) จบที่อีเมลถูกบันทึกใน subscriber และผู้ใช้เห็นข้อความสำเร็จ — เส้นทางย่อย A และ B จบที่ subscriber ไม่มีการเปลี่ยนแปลงใดๆ และผู้ใช้เห็น error ที่ตรงกับสาเหตุ

**Alternate / Error Paths**: เส้นทางย่อย A (รูปแบบผิด) และ B (สมัครซ้ำแบบตรงตัวอักษรทุกตัว) ตามตาราง Step ด้านบน — ดู "ข้อสังเกตใหม่" ท้ายไฟล์นี้สำหรับกรณี error ที่ระบบหลังบ้านล้มเหลว (ไม่ใช่ error จาก input ผู้ใช้) ซึ่งยังไม่มีการกำหนดพฤติกรรมไว้เลย

**Related REQ-F / BR / AC**: REQ-F-001 ถึง REQ-F-004, BR-001 ถึง BR-003, AC-001 ถึง AC-004

**Decision Point**: DP-001, DP-002 (รายละเอียดในตาราง Decision Points ด้านล่าง)

**Carried-forward Open Questions**:
- **OQ-02 (Requirement Review, RISK-001 ระดับ High)** — เช็คอีเมลซ้ำแบบ case-sensitive ที่ DP-002 เป็นการตัดสินใจชั่วคราว ยังไม่ได้รับการยืนยันจากทีม Marketing กระทบ **DP-002 และ Step 4/4B โดยตรง**: ถ้าผู้ใช้กรอกอีเมลเดิมด้วยตัวพิมพ์ต่างกัน (เช่นเคยสมัคร `test@mail.com` แล้วมากรอก `Test@Mail.com`) DP-002 จะตอบ **No** (ไม่ถือว่าซ้ำ) ทำให้เข้า Step 5 และสมัครสำเร็จซ้ำได้ ซึ่งขัดกับความคาดหวังทั่วไปของผู้ใช้เรื่องอีเมล — นี่คือพฤติกรรมจริงของระบบตามที่ implement ไว้ตอนนี้ ไม่ใช่ข้อบกพร่องของ Flow ที่เขียนในไฟล์นี้
- **RISK-002 (Requirement Review, Compliance)** — ไม่มีข้อมูลเรื่อง PDPA/consent กระทบ **Step 5/6** (จุดที่บันทึกอีเมลลง subscriber) แม้ไม่กระทบ Flow ทางเทคนิคของรอบทดสอบนี้
- **RISK-003 (Requirement Review, Process)** — ยังไม่มี QA Lead ชัดเจน ไม่กระทบ Flow นี้โดยตรงแต่กระทบกระบวนการ Sign-off ในภาพรวม

## FLOW-002: ป้องกันกดปุ่มสมัครซ้ำระหว่างประมวลผล

**ประเภท: Supporting**

ครอบคลุม: REQ-F-005, BR-004, AC-005

**Actor**: ผู้เข้าชมเว็บไซต์ทั่วไป

**Trigger**: ผู้ใช้กดปุ่ม "สมัครรับข่าวสาร" ขณะที่คำขอก่อนหน้ายังประมวลผลไม่เสร็จ

**Pre-conditions**: มีคำขอสมัคร (จาก FLOW-001) ที่ส่งไปแล้วและระบบยังไม่ตอบกลับ

**แผนผัง Flow**
1. ผู้ใช้กดปุ่ม "สมัครรับข่าวสาร" ครั้งแรก (เริ่ม FLOW-001)
2. ระบบตั้งสถานะปุ่มเป็น disable ทันทีระหว่างรอผลลัพธ์
3. ผู้ใช้พยายามกดปุ่มซ้ำ → ปุ่มอยู่ในสถานะ disable จึงไม่ส่งคำขอซ้ำ
4. เมื่อ FLOW-001 ตอบกลับ (สำเร็จหรือ error) ปุ่มกลับมาใช้งานได้ตามปกติ

**ตาราง Step**

| Step | Actor | การกระทำ/ผลลัพธ์ของระบบ | System/API Touchpoint | อ้างอิง (REQ-F/BR/AC) |
|---|---|---|---|---|
| 1 | ระบบ | ตั้งสถานะปุ่ม "สมัครรับข่าวสาร" เป็น disable ทันทีที่ผู้ใช้กดครั้งแรก | Client-side UI state | REQ-F-005, BR-004 |
| 2 | ผู้ใช้ | พยายามกดปุ่มซ้ำระหว่างรอผล | Client-side UI | REQ-F-005 |
| 3 | ระบบ | ไม่รับ action จากปุ่มที่ disable อยู่ ไม่ส่งคำขอซ้ำ | Client-side UI | REQ-F-005, BR-004, AC-005 |
| 4 | ระบบ | เมื่อได้ผลลัพธ์จาก FLOW-001 แล้ว (สำเร็จหรือ error) เปลี่ยนปุ่มกลับเป็นใช้งานได้ | Client-side UI state | REQ-F-005 |

**Post-condition / End State**: ปุ่มกลับมาใช้งานได้ตามปกติหลังได้ผลลัพธ์ ไม่มีคำขอซ้ำถูกส่งออกไประหว่างที่ disable

**Alternate / Error Paths**: ไม่มี — Flow นี้มีจุดประสงค์เดียวคือป้องกัน ไม่มีเส้นทาง error ของตัวเอง

**Related REQ-F / BR / AC**: REQ-F-005, BR-004, AC-005

**Decision Point**: ไม่มี

**Carried-forward Open Questions**: ไม่มีข้อที่กระทบ Flow นี้โดยตรงจาก Requirement Review

## Decision Points

| ID | เงื่อนไข | อ้างอิง (BR/REQ-F) | ทางออก: Yes | ทางออก: No |
|---|---|---|---|---|
| DP-001 | อีเมลอยู่ในรูปแบบมาตรฐานหรือไม่ | BR-001, REQ-F-002 | ไปต่อ DP-002 | เข้าเส้นทางย่อย A (Step 4A–5A) — แสดง error รูปแบบผิด |
| DP-002 | อีเมลนี้ตรงกับ subscriber ที่มีอยู่แล้วแบบ exact match หรือไม่ | BR-002, REQ-F-003 | เข้าเส้นทางย่อย B (Step 4B–5B) — แสดง error สมัครซ้ำ | ไปต่อ Step 5 — บันทึกอีเมลใหม่ |

## ตรวจสอบ Coverage

| REQ-F/REQ-NF/AC | ครอบคลุมโดย (Flow + Step) | สถานะ |
|---|---|---|
| REQ-F-001 | FLOW-001 Step 1–2 | ✅ |
| REQ-F-002 | FLOW-001 Step 3, 4A–5A | ✅ |
| REQ-F-003 | FLOW-001 Step 4, 4B–5B | ✅ |
| REQ-F-004 | FLOW-001 Step 5–6 | ✅ |
| REQ-F-005 | FLOW-002 Step 1–4 | ✅ |
| REQ-NF-001 (Usability — inline message) | FLOW-001 Step 5A, 5B, 6 | ✅ |
| REQ-NF-002 (Compatibility — สมมติฐานชั่วคราว) | ไม่มี Flow เฉพาะ — ใช้กับทุก Flow ที่มี UI | ⚠️ Cross-cutting: เป็นสมมติฐานชั่วคราวจาก Requirement Review ยังไม่มีรายชื่อ Browser ยืนยันจริง ต้องออกแบบ Test Case แยกเพื่อทดสอบข้าม Browser เมื่อมีคำตอบ |
| REQ-NF-003 (Compliance/Legal) | ไม่มี Flow เฉพาะ | ⚠️ Cross-cutting: ยังไม่มีข้อมูลเรื่อง PDPA/consent ไม่กระทบ Flow ทางเทคนิคของรอบทดสอบนี้ แต่ต้องติดตามก่อนปล่อย Production จริง |
| REQ-NF-004 (Performance) | ไม่มี Flow เฉพาะ | ⚠️ Cross-cutting: ไม่มีข้อมูลเป้าหมายด้าน Performance ในเอกสารต้นทางเลย |
| AC-001 | FLOW-001 Step 1–2 | ✅ |
| AC-002 | FLOW-001 Step 4A–5A | ✅ |
| AC-003 | FLOW-001 Step 4B–5B | ✅ |
| AC-004 | FLOW-001 Step 5–6 | ✅ |
| AC-005 | FLOW-002 Step 1–4 | ✅ |

สรุป: ครอบคลุม 10 จาก 10 ข้อ REQ-F/AC (✅ ทั้งหมด) และ 3 ข้อ REQ-NF เป็น cross-cutting (⚠️ ทั้งหมด ตามที่คาดไว้เพราะเป็นข้อกำหนดข้ามทั้งฟีเจอร์ ไม่ผูก Flow เดียว)

## Open Questions

1. **(Carried-forward, RISK-001 ระดับ High)** เช็คอีเมลซ้ำแบบ case-sensitive ที่ DP-002 — กระทบ FLOW-001 โดยตรงที่ Step 4/4B และ DP-002 ยังไม่มีคำตอบสุดท้ายจากทีม Marketing (ดูรายละเอียดที่ "Carried-forward Open Questions" ของ FLOW-001)
2. **(Carried-forward)** ยังไม่มีรายชื่อ Browser/Device ที่ต้องรองรับอย่างเป็นทางการ (OQ-03 จาก Requirement Review) — กระทบ REQ-NF-002 แบบ cross-cutting ทุก Flow ที่มี UI
3. **(Carried-forward)** ยังไม่มีข้อมูลเรื่อง PDPA/consent (RISK-002) — กระทบ Step 5/6 ของ FLOW-001 แม้ไม่บล็อกรอบทดสอบนี้
4. **(ข้อสังเกตใหม่ — เจอตอนแตก FLOW-001)** Requirement ต้นทางไม่ได้ระบุพฤติกรรมของระบบถ้าการบันทึกอีเมลลง subscriber ล้มเหลวจากสาเหตุฝั่งระบบเอง (เช่น database ไม่ตอบสนอง) — ไม่มี error message หรือพฤติกรรมกำหนดไว้สำหรับกรณีนี้เลย ต่างจาก Error Path A/B ที่เป็น error จาก input ผู้ใช้ ควรสอบถามทีมก่อนเริ่ม Skill 03 ว่าจะให้ Test Case ครอบคลุมกรณีนี้ไหม หรือถือว่าอยู่นอกขอบเขตของรอบทดสอบนี้เพราะเป็น Infrastructure-level failure

## Revision History

| Version | วันที่ | แก้ไขโดย | สรุปการเปลี่ยนแปลง |
|---|---|---|---|
| 1.0 | 2026-09-19 | AI (Claude) | แตก E2E Flow ครั้งแรกจาก Requirement Review v1.0 |

## QA Review & Sign-off

☐ Flow ทั้งหมดครอบคลุม Main/Alternate/Error path ที่ทีมคาดหวังจริง ไม่มี Flow สำคัญตกหล่น

☐ Decision Point ทั้งสองข้อ (DP-001, DP-002) ตรงกับพฤติกรรมที่ต้องการจริง

☐ ตาราง Coverage ครอบคลุมครบและข้อ cross-cutting (⚠️) เป็นที่รับทราบแล้ว

☐ Open Questions (โดยเฉพาะข้อ 1 และข้อสังเกตใหม่ข้อ 4) รับทราบแล้ว และตัดสินใจแล้วว่าจะรอคำตอบหรือไปต่อโดยรับความเสี่ยงไว้

☐ ยอมรับว่าพอจะไปทำ Skill 03 (test-case-generator) ได้

**Reviewer comment:**

**การตัดสินใจ:** approved / rejected / needs revision
