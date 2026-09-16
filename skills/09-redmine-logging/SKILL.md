---
name: redmine-logging
description: หลังจาก qa-report-generator (08) สรุปผล Go/No-Go และไล่ Known Issues แล้ว Skill นี้แสดงรายงานสรุปบั๊กที่ Fail จริงให้ผู้ใช้เลือกก่อนเสมอว่าจะ (1) เปิด Ticket จริงใน Redmine ทั้งหมด (ผ่าน REST API จริง ไม่ใช่ mock) (2) เปิดเฉพาะบางเคส (3) Export เป็นไฟล์ Excel แทนโดยยังไม่เปิด Ticket หรือ (4) ยกเลิก แล้วบันทึกเลขที่/ลิงก์ Ticket กลับเข้า Test Case Workbook คอลัมน์ "Issue link" เมื่อเปิด Ticket จริง จากนั้นถามว่าจะส่งอีเมลแจ้งเตือน Developer ผ่าน SMTP จริงต่อไหม เป็น Skill ที่ 9 ของ QA Pipeline นี้ ให้ใช้ Skill นี้ทันทีเมื่อผู้ใช้พูดถึงการเปิด Ticket ให้บั๊กที่เจอ, ส่ง bug เข้า Redmine, log ผลทดสอบเข้าระบบ tracking, export รายการบั๊กเป็น Excel, หรือแจ้งเตือน Developer ทางอีเมลหลังเปิดบั๊ก แม้จะไม่ได้เอ่ยชื่อ Skill ตรงๆ
---

# redmine-logging

Skill นี้เป็น**ขั้นตอนที่ 9** ของ QA Pipeline หน้าที่คือเอาบั๊กจริง (Test Case ที่ Fail จริง ไม่ใช่ Blocked) ที่เจอระหว่างทดสอบไปเปิดเป็น Ticket จริงใน Redmine ผ่าน REST API แล้วเขียนลิงก์ Ticket กลับเข้า Workbook เพื่อให้เป็น audit trail ที่ครบวงจร — **Skill นี้เชื่อมต่อระบบภายนอกจริง (สร้าง Ticket จริงในระบบของผู้ใช้) ต่างจาก Skill อื่นในสายที่ทำงานแค่กับไฟล์ในเครื่องเท่านั้น จึงต้องระมัดระวังเป็นพิเศษ**

## ขั้นตอนที่ 1 — ตรวจสอบขั้นตอนก่อนหน้าและสถานะเดิม

1. หาโฟลเดอร์ Project Root และโฟลเดอร์ Feature เหมือน Skill อื่นๆ ในสาย อ่าน `_pipeline-manifest.md`
2. **เช็ค Gate**: ต้องรันต่อจาก `qa-report-generator` (08) เสมอ — ตรวจสอบสถานะ Stage `08 qa-report-generator` (สถานะ `Complete` หรือ `Complete (Provisional — ...)` ถือว่าผ่าน Gate ทั้งคู่ เพราะรายงานสร้างเสร็จแล้วไม่ว่าผล Go/No-Go จะเป็นอะไร):
   - **ถ้ายังไม่ `Complete` เลย**: หยุดและถามผู้ใช้ว่าต้องการไปรัน `qa-report-generator` ให้เสร็จก่อนไหม (แนะนำ) — ห้ามข้ามไปเปิด Ticket เองจากข้อมูลดิบโดยไม่ผ่าน 08 เพราะ 08 คือจุดที่สรุป Known Issues ไว้อย่างเป็นทางการแล้ว
3. **ถ้า Stage `09 redmine-logging` เคยรันไปแล้ว (Complete)**: แจ้งผู้ใช้ว่าเคยรันแล้วเมื่อไหร่ (ดูวันที่ใน manifest) แล้วถามว่าต้องการรันซ้ำเพื่อเช็คว่ามี Test Case ที่ Fail เพิ่มใหม่หรือไม่ (เช่นหลังทำ `qa-retest` (10) แล้วพบ Fail เคสใหม่)

## ขั้นตอนที่ 2 — รวบรวม Test Case ที่ต้องเปิด Ticket

1. อ่าน Test Case Workbook ชีต "Test Case" **สดจากไฟล์จริงเสมอ** ด้วย `python3 scripts/qa_workbook.py read-cases --path "<path>"` (ห้ามเชื่อตัวเลขที่ 08 เคยสรุปไว้ เพราะอาจมีการแก้ไขเพิ่มเติมหลังจากนั้น)
2. กรองเฉพาะ Test Case ที่ **Status = "Fail" เท่านั้น** (ไม่รวม Blocked — Blocked ยังไม่ใช่บั๊กจริง เป็นแค่ Test Case ที่ตัดสิน Pass/Fail ไม่ได้เพราะรอ Open Question ปิดก่อน ตามกฎเดียวกับที่ `result-analysis` (07) และ `qa-report-generator` (08) ใช้ — ถ้า Blocked เคสไหนควรมี Ticket ด้วย ให้ผู้ใช้เปิดเองหรือบอกให้ Skill นี้รวมเข้ามาเป็นกรณีพิเศษ อย่าตัดสินใจรวมเองอัตโนมัติ)
3. สำหรับแต่ละ Test Case ที่ผ่านข้อ 2 เตรียมข้อมูลสำหรับสร้าง Ticket ตาม **Format ที่ยืนยันกับผู้ใช้แล้ว** (ดู Mockup เต็มที่ `mockup-defect-format.md` — ยืนยันผ่านแล้วโดยใช้ TC-017 เป็นตัวอย่างจริง):

   **`subject`**: `[<Priority>] <Test Case ID>: <Test Scenario>` เช่น `[P2] TC-017: ลบโค้ด A แล้วใส่โค้ด B ต่อทันที — กรณีสมมติฐาน...`

   **`description`**: ใช้ Markdown syntax เสมอ (ตัวหนา `**text**`) — **ถามผู้ใช้ก่อนทุกครั้งที่รัน Skill นี้ครั้งแรกกับ Redmine instance ใหม่ว่าใช้ Textile หรือ Markdown** (Redmine ค่าเริ่มต้นคือ Textile ซึ่งใช้ `*text*` ตัวหนาแทน — ถ้าใช้ syntax ผิดฝั่ง Ticket จะมีเครื่องหมายดอกจันเพี้ยนปนในเนื้อหาแทนที่จะ render สวยๆ) เรียงลำดับ field ตามนี้เสมอ **ห้ามยุบ Priority, Test Case ID, Module ไว้บรรทัดเดียวกันหรือติดกันโดยไม่มีบรรทัดว่างคั่นเด็ดขาด — ทั้ง 3 field นี้ต้องแยกคนละบรรทัดกันหมด** (เคยลองแล้วใน Markdown บรรทัดติดกันไม่มีบรรทัดว่างคั่นจะถูก render รวมเป็นย่อหน้าเดียว อ่านยาก) ต้องมีบรรทัดว่างคั่นระหว่างทุก field เสมอ:

   ```
   <Summary บรรทัดเดียวสรุปจาก Actual Result — เขียนให้กระชับ อ่านแล้วเข้าใจว่าเจออะไร>

   **Priority:** <P0-P3>

   **Test Case ID:** <TC-xxx>

   **Module:** <Module>

   **Environment:** <Environment จาก Env & Config sheet + Browser ที่เจอบั๊ก>

   **Steps to Reproduce:**
   1. <แปลง Test Step เป็น numbered list>
   ...

   **Test Data:** <ค่าจริงที่ใช้ทดสอบ ไม่ใช่แค่คำอธิบาย>

   **Expected Result:** <Expected Result>

   **Actual Result:** <Actual Result>

   **Root Cause:** <ถ้า 07-result-analysis.docx วิเคราะห์ไว้แล้วให้ใส่ — ถ้ายังไม่มีให้ตัดหัวข้อนี้ทิ้งไปเลย ห้ามใส่ "ยังไม่วิเคราะห์" ค้างไว้เพราะไม่มีประโยชน์กับคนอ่าน>

   **หลักฐาน:** <path รูป เช่น screenshots/Chromium/TC-017.png (ดูรูปเต็มใน 07-photo-evidence.docx หน้า TC-xxx)>

   **อ้างอิง:** 03-test-case-workbook.xlsx (Test Case ID: <TC-xxx>)
   ```

   Summary บรรทัดแรกให้ AI สรุปเองจาก Actual Result ทุกครั้ง (ไม่ต้องถามผู้ใช้ทีละเคส) — คนที่เปิดอ่าน Ticket ใน Redmine ต้องเข้าใจบั๊กได้ครบโดยไม่ต้องเปิด Workbook ประกอบ

   **`existing_issue_link`**: ค่าปัจจุบันในคอลัมน์ "Issue link" ของ Test Case นั้น (ถ้ามีค่าอยู่แล้ว = เคยเปิด Ticket ไปแล้วในรอบก่อนหน้า **ต้องข้าม ห้ามเปิดซ้ำ**)

   นอกจาก 4 field ด้านบนที่ใช้ยิงเข้า Redmine จริง ต้องเตรียมอีก 5 field เพิ่มสำหรับแสดงในรายงาน preview/Excel export/email ที่ขั้นตอนที่ 3 และ 6 (ไม่ได้ส่งเข้า Redmine โดยตรง แค่ใช้แสดงผล):
   - **`module`**: ค่า Module จาก Workbook ตรงๆ
   - **`title`**: Test Scenario ล้วนๆ (ไม่ต้องมี `[Priority] TC-xxx:` นำหน้าซ้ำ เพราะรายงานจะเอา TC-ID ไปแสดงแยกอยู่แล้ว)
   - **`remark`**: ใช้ค่าเดียวกับ Summary บรรทัดแรกของ `description` ด้านบน (ไม่ต้องเขียน logic สรุปข้อความซ้ำสองที่)
   - **`steps`**: list ของ Test Step แต่ละขั้น (ข้อความเดียวกับที่แปลงเป็น numbered list ใน "Steps to Reproduce" ของ description ด้านบน) ใช้ในอีเมลแจ้งเตือนที่ขั้นตอนที่ 6 เท่านั้น
   - **`screenshot_path`**: path เดียวกับที่ใส่ในหัวข้อ "หลักฐาน" ของ description (เช่น `screenshots/Chromium/TC-017.png`)
4. เขียนข้อมูลทั้งหมดนี้เป็นไฟล์ `cases-json` (ดู schema ใน docstring ของ `scripts/create_redmine_issues.py`)

**ถ้าไม่มี Test Case ที่ Fail จริงเลย (กรองแล้วว่างเปล่า)**: แจ้งผู้ใช้ว่าไม่มีอะไรต้องเปิด Ticket ในรอบนี้ ตั้ง Stage `09 redmine-logging` เป็น `Complete (ไม่มี Ticket ให้เปิด)` แล้วจบ Skill ทันที ไม่ต้องทำขั้นตอนถัดไป

## ขั้นตอนที่ 3 — แสดงรายงาน Preview แล้วให้ผู้ใช้เลือก Action ก่อนเสมอ

รัน `list-preview` ก่อนเสมอ (ไม่ต้องมี credential เลยเพราะไม่ยิง API จริง — สคริปต์แค่พิมพ์รายงานออกมา):
```
python3 scripts/create_redmine_issues.py list-preview --cases-json "<path>.json" --workbook-label "<path Workbook จริงที่ใช้ในขั้นตอนที่ 2>"
```
รูปแบบผลลัพธ์ (ยืนยันกับผู้ใช้แล้ว ดู `mockup-preview-and-confirm.md`):
```
======================================================================
🐞 SKILL 09: REDMINE BUG LOGGING PREVIEW
======================================================================
📂 Loaded Test Case Workbook: 03-test-case-workbook.xlsx (Discount Code Application)
🔍 Found 2 Failed Test Cases (พร้อมเปิด Ticket)
⏭ ข้ามอัตโนมัติ (มี Ticket อยู่แล้ว): 1 เคส
----------------------------------------------------------------------
[Bug #1]
• Module: ...
• Title: TC-009 · ...
• Priority: P1
• Remark: ...
• Attached Proof: screenshots/Chromium/TC-009.png
----------------------------------------------------------------------
[Bug #2]
...
----------------------------------------------------------------------
[?] เลือก Action:
  [1] เปิด Ticket ทั้งหมด (2 เคส) เข้า Redmine พร้อมแนบ Screenshot
  [2] เลือกเฉพาะบางเคส (เช่น 1)
  [3] Export รายการเป็นไฟล์ Excel เท่านั้น (ยังไม่เปิด Ticket เข้า Redmine)
  [4] Cancel — ไม่ทำอะไรเลย
```
เรียง `[Bug #]` ตาม Priority ก่อนเสมอ (P0 มาก่อน P3) — สคริปต์เรียงให้อัตโนมัติแล้ว ไม่ต้องจัดลำดับเอง

**สำคัญมาก — เมนู `[?]` นี้ไม่ใช่ prompt ที่รอ input จริงจาก Terminal**: สคริปต์แค่พิมพ์ข้อความออกมาเฉยๆ (ไม่มี `input()` ในโค้ด) เพราะ Claude เป็นคนรันสคริปต์ผ่าน command นี้ ไม่ใช่ผู้ใช้พิมพ์ใส่ Terminal เอง ดังนั้นหลังรันแล้วต้องทำตามนี้เสมอ:
1. **Paste รายงานที่ได้ให้ผู้ใช้ดูในแชทตรงๆ ตามที่สคริปต์พิมพ์จริง** (ห้ามสรุปเอง ห้ามแต่งข้อมูลเพิ่ม/ตัดออก)
2. ใช้เครื่องมือถามคำถามจริงถามผู้ใช้ 4 ตัวเลือกเดียวกับในรายงาน (All / Select เฉพาะบางเคส / Export Excel / Cancel)
3. แยกทำตามคำตอบดังนี้:

   **(1) เปิดทั้งหมด**: ไปขั้นตอนที่ 4 โดยไม่ใส่ `--only` (สร้าง Ticket ให้ทุกเคสที่ยังไม่มี Issue link)

   **(2) เลือกเฉพาะบางเคส**: ถามผู้ใช้ต่ออีกรอบให้เลือกได้ว่าจะเอา `[Bug #]` ไหนบ้าง (เลือกได้จากลิสต์ชื่อ Bug ที่เห็นจริงในรายงาน ไม่ต้องให้ผู้ใช้พิมพ์เลขเอง กันพิมพ์ผิด) แล้วแปลงเป็น TC-ID ส่งต่อเป็น `--only "TC-xxx,TC-yyy"` ในขั้นตอนที่ 4

   **(3) Export เป็นไฟล์ Excel เท่านั้น**: **ข้ามขั้นตอนที่ 4 ทั้งหมด ไม่ยิง API เข้า Redmine เลย** ไม่ต้องขอ Redmine URL/API Key ด้วยซ้ำ (เพราะไม่ได้ใช้) รันแทน:
   ```
   python3 scripts/create_redmine_issues.py export-excel --cases-json "<path>.json" --out "<Feature folder>/09-redmine-bugs-export.xlsx" [--only "TC-xxx,TC-yyy"]
   ```
   ผลลัพธ์คือไฟล์ `09-redmine-bugs-export.xlsx` ในโฟลเดอร์ Feature มีคอลัมน์ No./Test Case ID/Module/Title/Priority/Remark/Screenshot Path/Subject/Description (Subject กับ Description เป็นข้อความเต็มพร้อมก็อปไปเปิด Ticket เองทีหลังได้เลย) **การ Export ไม่ถือว่าเปิด Ticket แล้ว — ห้ามแก้คอลัมน์ "Issue link" ใน Workbook หลังจากนี้เด็ดขาด** เพราะยังไม่มี Ticket จริงให้ลิงก์กลับ (ดูรายละเอียดขั้นตอนที่ 5 ข้อ Export) แจ้งผู้ใช้ให้เข้าใจชัดเจนว่านี่แค่ "พิมพ์รายการออกมาดู" ไม่ใช่ "บันทึกว่าจัดการบั๊กนี้แล้ว" รันซ้ำรอบหน้าเคสเดิมจะยังขึ้นมาให้เลือกอีก

   **(4) Cancel**: จบ Skill ทันที ไม่ต้องขอ Redmine URL/API Key ไม่ต้องทำขั้นตอนที่ 4-5 ต่อ (ดูการอัปเดต Manifest ในขั้นตอนที่ 5 ข้อ Cancel)

ถ้าเลือก (1) หรือ (2) เท่านั้นที่ต้องขอข้อมูลเชื่อมต่อ Redmine ต่อ — **ต้องถามผู้ใช้ตรงๆ ทุกครั้งที่รัน Skill นี้ (ห้ามจำ/เก็บค่าจากรอบก่อนไว้ใช้ซ้ำ ห้ามเขียนค่าเหล่านี้ลงไฟล์ใดๆ ในโปรเจคเด็ดขาดรวมถึง manifest)**:
1. Redmine URL (เช่น `https://redmine.yourcompany.com`)
2. Redmine API Key (ดูได้จากหน้า "My account" ของผู้ใช้ใน Redmine เอง)
3. Project identifier หรือ Project ID ที่จะเปิด Ticket เข้า
4. ชื่อ Tracker ที่จะใช้ (ปกติคือ "Bug" — แต่ต้องถามเพราะแต่ละ instance อาจตั้งชื่อไม่เหมือนกัน)
5. (ไม่บังคับ) Redmine user ID ที่จะ assign Ticket ให้

ตั้งค่า 2 ตัวแรกเป็น environment variable ก่อนเรียกสคริปต์เสมอ (`REDMINE_URL`, `REDMINE_API_KEY`) — **ห้ามส่งเป็น `--argument` ตรงๆ** เพราะจะโผล่ใน shell history/process list ให้คนอื่นในเครื่องเดียวกันมองเห็นได้

ก่อนไปขั้นตอนที่ 4 จริง ให้ยืนยันกับผู้ใช้อีกครั้งสั้นๆ ว่ากำลังจะสร้าง Ticket ให้กี่เคส (ตามที่เลือกในข้อ (1)/(2)) เพราะการสร้าง Ticket จริงเป็นการเปลี่ยนแปลงระบบภายนอกที่ย้อนกลับเองไม่ได้ง่ายๆ (ต้องไปลบ/ปิดเองใน Redmine)

## ขั้นตอนที่ 4 — สร้าง Ticket จริง

หลังผู้ใช้เลือก Action (1) หรือ (2) และ confirm แล้วเท่านั้น รัน:
```
python3 scripts/create_redmine_issues.py create --cases-json "<path>.json" --project "<project>" --tracker "<tracker>" [--assignee "<user id>"] [--only "TC-xxx,TC-yyy"] --out "<result>.json"
```
(ใส่ `--only` เฉพาะตอนเลือก Action (2); ไม่ใส่ = สร้างให้ทุกเคสที่ยังไม่มี Issue link ตาม Action (1) — ตั้ง `REDMINE_URL`/`REDMINE_API_KEY` เป็น environment variable ก่อนรันบรรทัดนี้เสมอตามขั้นตอนที่ 3)

อ่านผลลัพธ์ที่ได้ (`created`/`skipped`/`failed`) แล้วรายงานให้ผู้ใช้ทราบครบทุกกรณี **ไม่ใช่แค่กรณีที่สำเร็จ**:
- ถ้ามี `failed` (เช่น เชื่อมต่อ Redmine ไม่ได้, Project/Tracker ผิด, สิทธิ์ API Key ไม่พอ) ให้แจ้งข้อความ error จริงที่ได้กลับมา ห้ามสรุปเอาเองว่า "สำเร็จ" ทั้งที่มีบางเคส fail — โดยเฉพาะถ้า error มีคำว่า "403"/"Forbidden" จาก proxy (ไม่ใช่จาก Redmine เอง) ให้สงสัยไว้ก่อนว่าอาจเป็นเพราะ network egress ของ environment ที่รัน Skill นี้ยังไม่ได้ allowlist โดเมนของ Redmine ไว้ (ปัญหาประเภทเดียวกับที่เคยเจอตอนพยายามติดตั้ง Playwright/WebKit ในเซสชันนี้) — แจ้งผู้ใช้ตรงๆ ว่าอาจต้อง allowlist โดเมนก่อน ไม่ใช่เดาสาเหตุอื่น
- ถ้ามี `skipped` ให้แจ้งว่าข้ามเพราะมี Issue link อยู่แล้ว (ไม่ใช่ error)

## ขั้นตอนที่ 5 — บันทึกกลับเข้า Workbook และอัปเดต Manifest

**กรณีเลือก Action (1)/(2) แล้วมี Ticket ถูกสร้างจริง**:
1. สำหรับทุกรายการใน `created` เตรียมไฟล์ JSON แบบ `[{"tc_id": "...", "field": "Issue link", "value": "<url>"}]` แล้วรัน
   ```
   python3 scripts/qa_workbook.py update-fields-batch --path "<path Workbook>" --updates-json "<path>.json" --editor "redmine-logging" --note "เปิด Ticket ให้ <จำนวน> เคสที่ Fail จริง"
   ```
   (อัปเดตทีเดียวทั้งชุด ไม่ทำทีละเคส — เหตุผลเดียวกับที่ `qa-automation-script` (06a) ทำ คือกัน Document Control History ท่วม)
2. สร้างไฟล์สรุป `09-redmine-log.md` ในโฟลเดอร์ Feature — บันทึกรายการ Ticket ที่เปิดสำเร็จ (Test Case ID, Priority, Ticket URL, วันที่), รายการที่ข้าม, และรายการที่ failed พร้อมเหตุผล **ห้ามใส่ค่า API Key ลงไฟล์นี้เด็ดขาด** — ไฟล์นี้คือ output หลักที่ manifest จะชี้ไปหา (เพราะ Ticket จริงอยู่นอกระบบไฟล์ ต้องมีสำเนาสรุปไว้ในโปรเจคด้วย)
3. อัปเดต `_pipeline-manifest.md`: ตั้งค่า Stage `09 redmine-logging` เป็น `Complete` เมื่อประมวลผลครบทุกเคสที่เลือก (นับว่า Complete ได้แม้บางเคส `failed` ตราบใดที่ได้พยายามครบและรายงานผลไว้ชัดเจนแล้ว — ถ้ามี failed ค้าง ให้ระบุใน manifest ว่ายังมีกี่เคสที่ยังไม่ได้เปิด Ticket จริง เพื่อให้ผู้ใช้ตามแก้เอง; ถ้าเลือก Action (2) และเหลือเคสที่ยังไม่ได้เลือกเปิด ให้ระบุใน manifest ด้วยว่ายังมีกี่เคสที่ผู้ใช้ตั้งใจข้ามไว้ก่อน)
4. แจ้งผู้ใช้ผลสรุป (เปิดสำเร็จกี่ใบ, ข้ามกี่ใบ, fail กี่ใบพร้อมเหตุผล) แล้วแนะนำขั้นตอนถัดไป (`qa-retest` (10) หลังบั๊กถูกแก้แล้ว)

**กรณีเลือก Action (3) Export Excel**: ไม่ต้องแก้คอลัมน์ "Issue link" ใน Workbook และไม่ต้องสร้าง `09-redmine-log.md` (เพราะยังไม่มี Ticket จริงให้ทำ audit trail) อัปเดต `_pipeline-manifest.md` ให้ Stage `09 redmine-logging` เป็น `Complete (Export เท่านั้น — ยังไม่เปิด Ticket จริง N เคส ดู 09-redmine-bugs-export.xlsx)` แล้วแจ้งผู้ใช้ว่าไฟล์ Export อยู่ที่ไหน และย้ำว่ารันรอบหน้าเคสเดิมจะยังขึ้นมาให้เลือกอีกเพราะยังไม่นับว่าเปิด Ticket แล้ว

**กรณีเลือก Action (4) Cancel**: ไม่ต้องแก้ไฟล์ใดๆ ในโปรเจค อัปเดต `_pipeline-manifest.md` ให้ Stage `09 redmine-logging` เป็น `ยังไม่เปิด Ticket (ผู้ใช้ยกเลิก N เคสที่พบ)` แล้วจบ Skill ทันที ไม่ต้องแนะนำขั้นตอนถัดไป (ผู้ใช้ยกเลิกเอง อาจกลับมารัน Skill นี้ใหม่ทีหลังเมื่อพร้อม)

## ขั้นตอนที่ 6 — แจ้งเตือน Developer ทาง Email (เฉพาะกรณีเปิด Ticket สำเร็จอย่างน้อย 1 ใบ)

ขั้นตอนนี้ทำเฉพาะตอนเลือก Action (1)/(2) ในขั้นตอนที่ 3 แล้วผลลัพธ์จากขั้นตอนที่ 4 มี `created` อย่างน้อย 1 รายการเท่านั้น (Action (3) Export กับ (4) Cancel ไม่ต้องทำขั้นตอนนี้ และถ้า `created` ว่างเปล่าทั้งหมด fail ก็ไม่ต้องทำเช่นกัน)

**หมายเหตุสำคัญเรื่อง environment ก่อนเริ่ม**: ตอนพัฒนา Skill นี้ทดสอบแล้วว่า cloud sandbox ที่ใช้พัฒนาไม่สามารถต่อ SMTP (raw TCP) ออกอินเทอร์เน็ตได้เลย (timeout เสมอไม่ว่า credential จะถูกหรือผิด เพราะ network ของ environment นั้นอนุญาตแค่ HTTP/HTTPS ผ่าน proxy ไปยังโดเมนใน allowlist เท่านั้น) **ถ้ารัน Skill นี้ใน environment แบบเดียวกัน ขั้นตอนนี้จะส่งอีเมลไม่ออกแน่นอนไม่ว่าจะตั้งค่าถูกแค่ไหน** — ให้แจ้งผู้ใช้ตรงๆ ถ้าเจอ error แบบ timeout/connection ล้มเหลว อย่าเข้าใจผิดว่า credential ผิดหรือ SMTP server มีปัญหา (ดูรายละเอียดเพิ่มใน docstring ของ `scripts/send_email_notification.py`)

1. รัน:
   ```
   python3 scripts/send_email_notification.py print-success --result-json "<result>.json"
   ```
   (ไฟล์เดียวกับ `--out` ของคำสั่ง `create` ในขั้นตอนที่ 4) แล้ว **paste รายงานที่ได้ให้ผู้ใช้ดูในแชทตรงๆ** รูปแบบผลลัพธ์:
   ```
   ======================================================================
   ✅ SUCCESS: 2 Bugs posted to Redmine successfully!
      • #1024 - [P2] TC-017: ลบโค้ด A แล้วใส่โค้ด B ต่อทันที
      • #1025 - [P1] TC-009: ใช้โค้ดส่วนลดเปอร์เซ็นต์ซ้อนกับสินค้าที่ลดราคาอยู่แล้ว
   ======================================================================
   ```
2. ถามผู้ใช้ผ่านเครื่องมือถามคำถามจริง (ไม่ใช่รอ input จาก Terminal — หลักการเดียวกับขั้นตอนที่ 3): **ต้องการส่งอีเมลแจ้งเตือน Developer ไหม (y/n)**
   - ถ้า **ไม่ส่ง**: จบขั้นตอนนี้ทันที ไปสรุปผลรวมให้ผู้ใช้แล้วจบ Skill ตามปกติ
3. ถ้า **ต้องการส่ง**: ถามผู้ใช้ **ใหม่ทุกครั้ง** (ห้ามจำ/เก็บค่าจากรอบก่อน) ทีละอย่าง:
   - Developer Email Address ที่จะส่งถึง
   - SMTP Host, Port, Username, Password (App Password ถ้าใช้ Gmail) — ตั้งเป็น environment variable `SMTP_HOST`/`SMTP_PORT`/`SMTP_USERNAME`/`SMTP_PASSWORD` ก่อนเรียกสคริปต์เสมอ **ห้ามส่งเป็น `--argument` ตรงๆ** เพราะจะโผล่ใน shell history/process list (เหตุผลเดียวกับ Redmine API Key)
4. เตรียมเนื้อหาอีเมล (Subject + Body) — **Format ยืนยันแล้ว** (ดู `mockup-email-format.md` สำหรับตัวอย่างเต็มที่ใช้ TC-017 จริง) รัน:
   ```
   python3 scripts/send_email_notification.py build-body --cases-json "<path เดียวกับขั้นตอนที่ 2>.json" --result-json "<result>.json จากขั้นตอนที่ 4" --run-date "<วันที่รัน Skill 09 วันนี้ เช่น 01 Sep 2026>" --environment "<Environment เดียวกับที่ใช้ใน description ticket>" --out "<body>.txt"
   ```
   สคริปต์จะประกอบ Body ให้อัตโนมัติจาก field `module`/`title`/`remark`/`steps` ใน cases-json จับคู่กับ `issue_id`/`url`/`priority` ใน result.json (เรียงตาม Priority ก่อนเสมอเหมือน `list-preview`) แปลง Priority → คำ Severity ด้วย mapping ที่ยืนยันแล้ว: **P0=Critical, P1=High, P2=Medium, P3=Low** รูปแบบผลลัพธ์ (Subject แยกกำหนดเองในขั้นตอนถัดไป ไม่ได้อยู่ใน body):
   ```
   Hi Dev Team,

   ระบบ QA Automation ได้ทำการทดสอบระบบล่าสุดเสร็จสิ้น และพบ Bug ที่ต้องการการแก้ไขจำนวน <N> รายการ
   รายละเอียดและลิงก์สำหรับเข้าดู Ticket ใน Redmine ถูกสรุปไว้ด้านล่างนี้ครับ:

   ================================================================================
   🐞 DEFECT SUMMARY REPORT
   ================================================================================
   Test Run Date: <run-date> | Environment: <environment>
   --------------------------------------------------------------------------------
   1. [<Priority> - <Severity>] <Title>
   --------------------------------------------------------------------------------
   • Issue Link : <url>
   • Module     : <Module>
   • Test Case  : <TC-ID>
   • Description: <remark>
   • Steps to Reproduce:
     1. <step>
     ...
   --------------------------------------------------------------------------------
   ... (1 บล็อกต่อ 1 Ticket ใน created เรียงตาม Priority)
   ================================================================================
   📁 Attached Evidence:
   - สามารถดู Path ของไฟล์ Screenshot ผลการทดสอบได้ที่หัวข้อ "หลักฐาน" ใน Description ของแต่ละ Ticket (อ้างอิง path ในระบบไฟล์ของทีม QA — Skill นี้ยังไม่ได้อัปโหลดไฟล์แนบขึ้น Redmine โดยตรง)
   - สามารถคลิกที่ Issue Link ด้านบนเพื่อดูรายละเอียดเพิ่มเติมและอัปเดต Status ได้ทันทีครับ

   Best regards,
   QA Automation Assistant
   --------------------------------------------------------------------------------
   ```
   **หมายเหตุที่ยืนยันแล้วกับผู้ใช้**: Format ต้นฉบับมีทั้ง "Description" และ "Remark" แยก 2 บรรทัดต่อบั๊ก แต่ cases-json ของ Pipeline นี้มีแค่ field เดียว (`remark`) จึงรวมเป็นบรรทัด "Description" บรรทัดเดียว, "Test Run Date" ใช้วันที่รัน Skill 09 จริง (ไม่ใช่วันที่ทดสอบเสร็จใน 08-qa-report.docx), และย้าย Module ออกมาเป็นบรรทัดของตัวเองแทนการยัดไว้ในหัวข้อ/วงเล็บ Test Case เพื่อให้ field ตรงกับรายงาน Terminal/Excel export

   จากนั้นรัน:
   ```
   python3 scripts/send_email_notification.py send --to "<developer email>" --subject "[QA] Bug Report Summary — <N> Ticket(s) Opened" --body-file "<body>.txt"
   ```
5. อ่านผลลัพธ์แล้วรายงานผู้ใช้ตามจริงเสมอ **ห้ามพิมพ์ "✅ Email sent successfully" ถ้าสคริปต์ยังไม่ยืนยันว่าส่งสำเร็จจริง**:
   - สำเร็จ: แจ้งว่าอีเมลส่งถึง `<developer email>` แล้ว
   - ไม่สำเร็จ: แจ้ง error จริงที่ได้กลับมา — ถ้าเป็น timeout/connection ล้มเหลว ให้อธิบายผู้ใช้ตามหมายเหตุด้านบนว่าน่าจะเป็นข้อจำกัดของ environment ไม่ใช่ credential ผิด
6. ไม่ต้องอัปเดต `_pipeline-manifest.md` เพิ่มสำหรับขั้นตอนนี้ (ถือเป็นส่วนเสริมของ Stage 09 เดิม ไม่ใช่ Stage แยก) แต่ถ้าส่งสำเร็จให้จดในข้อความสรุปท้าย Skill ว่าได้แจ้งเตือน Developer ทางอีเมลแล้ว

## ข้อควรระวัง

- **ห้ามเก็บ/cache Redmine URL หรือ API Key ไว้ที่ไหนก็ตามข้ามรอบการรัน** ต้องถามผู้ใช้ใหม่ทุกครั้งตามที่ผู้ใช้ยืนยันไว้ตอนออกแบบ Skill นี้ — รวมถึงห้ามเขียนลง `_pipeline-manifest.md`, ไฟล์ log, หรือ commit message ใดๆ
- **ห้ามเปิด Ticket ให้ Test Case ที่ Status เป็น Blocked** เด็ดขาดโดยไม่ถามผู้ใช้ก่อน (ดูขั้นตอนที่ 2.2)
- **ห้ามเปิด Ticket ซ้ำ** ให้ Test Case ที่มีค่าในคอลัมน์ "Issue link" อยู่แล้ว — สคริปต์ข้ามให้อัตโนมัติแล้ว แต่ต้องรายงานให้ผู้ใช้เห็นด้วยว่าข้ามอะไรไปบ้าง
- **ต้องขอ confirm จากผู้ใช้ก่อนยิง API สร้าง Ticket จริงเสมอ** (ดูขั้นตอนที่ 3) เพราะเป็นการเปลี่ยนแปลงระบบภายนอกจริง ย้อนกลับเองไม่ได้ง่ายๆ ต่างจาก Skill อื่นในสายที่แค่แก้ไฟล์ในเครื่อง
- ถ้าเจอ error แบบ proxy/network block (403 Forbidden จากตัวกลาง ไม่ใช่จาก Redmine) ให้บอกผู้ใช้ตรงๆ ว่าน่าจะเป็นเพราะ network egress allowlist ของ environment ที่รัน ไม่ใช่ปัญหาที่ credential หรือ Redmine เอง — อย่าเดาสาเหตุอื่นแล้วลองแก้มั่ว
- Skill นี้**ไม่ตั้งค่า `priority_id` ของ Ticket** เพราะแต่ละ Redmine instance ตั้งค่าตัวเลขไม่เหมือนกัน (ดูเหตุผลเต็มในสคริปต์) — ใส่ Priority ไว้ใน subject/description ให้เห็นชัดแทน
- **รายงาน `list-preview` ใช้คำว่า "Priority" ไม่ใช่ "Severity"** เพราะ Workbook ของ Pipeline นี้มีแค่คอลัมน์ Priority (P0-P3) ไม่มีคอลัมน์ Severity แยกต่างหาก — ห้ามเดา mapping Priority→Severity level (เช่น P0=Critical) ขึ้นมาเองโดยไม่มีใครยืนยัน
- **เมนู `[?]` ท้ายรายงาน `list-preview` ไม่ใช่ prompt ที่รอ input จริงจาก Terminal** (ดูขั้นตอนที่ 3) — ต้อง paste รายงานให้ผู้ใช้ดูในแชทแล้วถามผ่านเครื่องมือถามคำถามจริงเสมอ ห้ามเข้าใจผิดว่าสคริปต์รอรับค่าจาก stdin
- **Action "Export เป็นไฟล์ Excel" (ตัวเลือกที่ 3) ไม่ถือว่าเปิด Ticket แล้ว** ห้ามแก้คอลัมน์ "Issue link" ใน Workbook หลัง Export เด็ดขาด และห้ามตั้ง Stage 09 เป็น `Complete` เฉยๆ โดยไม่ระบุว่าเป็น Export เท่านั้น (ดูขั้นตอนที่ 5)
- **ห้ามเก็บ/cache SMTP credential (Host/Port/Username/Password) หรือ Developer Email Address ไว้ข้ามรอบการรัน** ต้องถามผู้ใช้ใหม่ทุกครั้งที่ทำขั้นตอนที่ 6 เหมือนกับ Redmine credential — ห้ามเขียนลง `_pipeline-manifest.md`, ไฟล์ log, หรือ commit message ใดๆ เช่นกัน
- **ขั้นตอนที่ 6 (แจ้งเตือน Email) อาจใช้งานไม่ได้จริงถ้ารันใน environment ที่จำกัด network egress แบบ raw TCP** (ยืนยันแล้วว่า cloud sandbox ที่ใช้พัฒนา Skill นี้ต่อ SMTP ไม่ได้เลย) — ถ้าเจอ timeout/connection error ให้อธิบายผู้ใช้ตรงๆ ว่าน่าจะเป็นข้อจำกัดของ environment ห้ามเดาว่า credential ผิดหรือไปแก้ credential มั่ว
- **รูปแบบเนื้อหาอีเมล (Body) ในขั้นตอนที่ 6 ยืนยันแล้ว** (ดู `mockup-email-format.md`) ประกอบด้วยสคริปต์ `build-body` อัตโนมัติ ห้ามพิมพ์เนื้อหาเองมือเปล่าหรือเปลี่ยน field/ลำดับเอง — ถ้าจะเพิ่ม/แก้ field ต้องแก้ที่สคริปต์ให้ตรงกันด้วย (เหตุผลเดียวกับ Format ของ Redmine defect ticket ใน `mockup-defect-format.md`)
- **cases-json ต้องมี field `steps` (list) เพิ่มจากเดิม** ก่อนจะใช้ `build-body` ได้ (ดูขั้นตอนที่ 2) ถ้าลืมเตรียม field นี้ อีเมลจะขาดหัวข้อ "Steps to Reproduce" ไปเงียบๆ (สคริปต์ไม่ error เพราะถือว่า steps ว่างเปล่า = ไม่มี field นี้ในบั๊กนั้น)
