# ตัวอย่างจริง: Newsletter Email Subscription

ตัวอย่างการใช้ QA Pipeline ทั้ง 15 Skill กับฟีเจอร์เล็กๆ ฟีเจอร์หนึ่ง (สมัครรับข่าวสารทาง Footer)
แบบจบทุกขั้นตอนจริง — ไม่ใช่ mock ทั้งหมด มีทั้งการรัน Test Automation จริงด้วย Playwright,
เว็บเดโมจริงที่ implement ตาม Business Rule ที่ Requirement Review เขียนไว้จริง, และ (ในขั้นตอนหลัง)
การเปิด Ticket ใน Redmine จริง + ส่งอีเมลแจ้งเตือนจริง เพื่อให้เห็นภาพรวม Flow ทั้งสายว่าแต่ละ Skill
ทำงานต่อกันอย่างไร และไฟล์ไหนควรอยู่ที่ไหนเวลาดูใน GitHub

> ไฟล์นี้เป็นเอกสารที่ปรับปรุงต่อเนื่องไปพร้อมกับความคืบหน้าของ Pipeline (ดูตาราง "สถานะปัจจุบัน" ด้านล่าง)
> ตอนที่เขียนล่าสุด Pipeline วิ่งมาครบทั้ง **15/15 Skill แล้ว** — ปิด Redmine Ticket #9 จริงใน Skill 10a (qa-retest-closure) เรียบร้อย วงจร QA↔Dev ของ TC-005 จบสมบูรณ์

## โครงสร้างไฟล์ในตัวอย่างนี้

ไฟล์แบ่งเป็นโฟลเดอร์ตามหัวข้อ ไม่ใช่กองรวมกันที่ root — สองไฟล์ที่ root มีแค่ไฟล์นี้กับ
`_pipeline-manifest.md` (ตารางสถานะรวมทุก Stage เป็น single source of truth) ที่เหลือแยกตามหน้าที่:

```
examples/newsletter-email-subscription/
├── README.md                          ← ไฟล์นี้
├── _pipeline-manifest.md              ← ตารางสถานะรวมทุก Stage
│
├── reports/                           ← เอกสารผลลัพธ์ของแต่ละ Skill เรียงเลขตามลำดับ Flow จริง
│   ├── 00-pre-source-ingest.md/.docx  ← Stage 00-pre: สรุปเอกสารต้นทาง
│   ├── 01-requirement-review.md/.docx ← Stage 01: ตีความ Requirement + Business Rule
│   ├── 02-e2e-flow.md/.docx           ← Stage 02: ออกแบบ User Flow
│   ├── 04-coverage-review.md          ← Stage 04: ตรวจ Coverage
│   ├── 05-risk-analysis.md            ← Stage 05: กำหนด Priority
│   ├── 06-test-data.md                ← Stage 06: แผน Test Data ก่อนรัน
│   ├── 07-result-analysis.docx        ← Stage 07: สรุปผล + Root Cause
│   ├── 07-photo-evidence.docx         ← Stage 07: ภาพหลักฐานประกอบ (9 รูป)
│   ├── 08-qa-report.docx              ← Stage 08: รายงาน Go/No-Go
│   ├── 09-redmine-log.md              ← Stage 09: บันทึกการเปิด Ticket จริง
│   ├── 10-qa-retest.md                ← Stage 10: บันทึกผล Retest จริง
│   └── 10a-qa-retest-closure.md       ← Stage 10a: บันทึกการปิด Ticket จริง
│
├── workbook/                          ← Test Case Workbook ตัวจริงที่หลาย Skill แก้ไขต่อกัน
│   ├── 03-test-case-workbook.xlsx     ← ไฟล์ live (เวอร์ชันล่าสุด — v6)
│   ├── RTM-traceability-matrix.xlsx   ← Traceability Matrix (Stage RTM)
│   └── history/                       ← สำเนา Workbook ณ จุดต่างๆ เปิดเทียบก่อน/หลังแต่ละ Skill ได้ตรงๆ
│       ├── README.md                  ← อธิบายว่าแต่ละไฟล์ต่างกันตรงไหน
│       ├── v1-after-03-create.xlsx
│       ├── v2-after-03-test-case-generator.xlsx
│       ├── v2-after-04-coverage-review-no-change.xlsx
│       ├── v3-after-05-risk-analysis.xlsx
│       ├── v3-after-06-test-data-generator-no-change.xlsx
│       ├── v4-after-06a-qa-automation-script.xlsx
│       ├── v5-after-09-redmine-logging.xlsx
│       └── v6-after-10-qa-retest.xlsx
│
├── automation/                        ← Stage 06a: โค้ดที่รันจริง
│   ├── TC-*.py                        ← Playwright Script จริง 1 ไฟล์ต่อ 1 Test Case
│   ├── automation-results.json        ← ผลดิบจาก runner ก่อนเขียนกลับ Workbook
│   └── demo-app/server.py             ← เว็บเดโมจริง (Flask) ที่ automation รันทดสอบด้วยจริง
│
├── evidence/                          ← ภาพหลักฐานจริงทุกจุดที่แตะระบบภายนอกหรือรันแล้วเห็นผลด้วยตา
│   ├── 06a-automation/                ← Stage 06a: ภาพจากการรัน Automation (วงเขียว=Pass, วงแดง=Fail)
│   │   ├── TC-*.png                   ← ผลปัจจุบัน 11 เคส
│   │   └── _history/                  ← ภาพผลรอบก่อนหน้าที่ถูกทับ (เก็บไว้เป็น audit trail)
│   ├── 09-redmine-ticket/             ← Stage 09: หน้า Ticket #9 ตอนเปิดใหม่ (5 รูป)
│   └── 10-qa-retest/                  ← Stage 10/10a: หน้า Ticket #9 ตอน Dev แจ้งแก้ และตอนปิดสำเร็จ (3 รูป)
│
├── sources/                           ← เอกสารต้นทางจำลอง (สเปกจาก PM, Slack chat log)
└── testplans/                         ← Stage 00: แผนการทดสอบ
```

> อยากเห็นว่าแต่ละ Skill ทำให้ Test Case Workbook เปลี่ยนแปลงตรงไหนบ้าง (หรือไม่เปลี่ยนเลยเพราะแค่ตรวจ
> สอบ) แบบเปิดไฟล์เทียบกันได้ตรงๆ ดูที่ [`workbook/history/`](./workbook/history/) ได้เลย — มีสำเนาให้ครบ
> ตั้งแต่สร้าง Workbook ครั้งแรก (v1) จนถึงหลัง Retest ปิด Ticket ผ่าน (v6)

## ทำไม Staging URL ถึงไม่ใช่ URL จริง

`Env & Config` ในเอกสารระบุ `https://staging.example-shop.test/` ซึ่งเป็น URL สมมติ (ตัวอย่างนี้ไม่มี
ระบบ e-commerce จริงอยู่เบื้องหลัง) — เพื่อให้ Stage 06a รัน Automation ได้ "จริง" แทนที่จะ mock ผลลัพธ์
ไว้ล่วงหน้า จึงสร้าง [`automation/demo-app/server.py`](./automation/demo-app/server.py) เป็นเว็บเดโมขึ้นมาเองที่ implement ตาม Business Rule ใน
[`reports/01-requirement-review.md`](./reports/01-requirement-review.md) ตรงๆ (รวมถึงบั๊กที่ตั้งใจปลูกไว้ตาม BR-002) แล้วให้ Playwright รันเทสกับเว็บ
เดโมนี้แทน ผลที่ได้ (Pass/Fail) จึงเป็นผลจริงจากการรันจริง ไม่ใช่ค่าที่เขียนดักไว้ล่วงหน้า

## Skill ไหนแก้ Test Case Workbook จริง vs. Skill ไหนแค่ตรวจ/ผลิตไฟล์แยก

ฟีเจอร์นี้ผ่านมาแล้วครบทั้ง **15/15 Skill** คำถามที่พบบ่อยเวลาดูตัวอย่างนี้คือ "แล้วรู้ได้
ไงว่าแต่ละ Skill ทำอะไรจริง ไม่ใช่แค่พูดผ่านๆ" — คำตอบสั้นๆ คือ Skill ในสายนี้แบ่งเป็น 2 กลุ่มชัดเจนตาม
การออกแบบ (ไม่ใช่ทุก Skill ควรแก้ Workbook — Skill ที่มีหน้าที่ "ตรวจสอบ/สรุปผล" ถูกออกแบบให้ **ห้ามแก้ไข
Workbook เด็ดขาด** เพื่อไม่ให้ขั้นตอนตรวจสอบไปปนกับขั้นตอนที่สร้างข้อมูล):

| # | Skill | ไฟล์ผลลัพธ์ของ Skill นี้ | แก้ Test Case Workbook จริงไหม | รายละเอียด |
|---|---|---|---|---|
| 1 | `source-ingest` (00-pre) | `reports/00-pre-source-ingest.md/.docx` | ไม่ (Workbook ยังไม่ถูกสร้าง) | สรุปเอกสารต้นทาง ยังไม่มี Test Case |
| 2 | `test-plan` (00) | `testplans/TP-*.md/.docx` | ไม่ | วางแผนการทดสอบระดับสูง |
| 3 | `requirement-review` (01) | `reports/01-requirement-review.md/.docx` | ไม่ | ตีความ Requirement/Business Rule/ประเมินความเสี่ยงเบื้องต้น |
| 4 | `e2e-flow-designer` (02) | `reports/02-e2e-flow.md/.docx` | ไม่ | ออกแบบ User Flow + Decision Point |
| 5 | `test-case-generator` (03) | `workbook/03-test-case-workbook.xlsx` | **ใช่ (สร้างไฟล์ + เพิ่ม Test Case)** | v1 = สร้าง Workbook, v2 = เพิ่ม TC-001–TC-011 |
| 6 | `coverage-review` (04) | `reports/04-coverage-review.md` | ขึ้นอยู่กับผล — รอบนี้ **ไม่แก้** | พบ 2 จุด แต่ผู้ใช้เลือก Defer/Keep-as-is ทั้งคู่ จึงไม่มีอะไรต้องแก้ (ถ้าเลือก Fix จะกลับไปแก้ที่ Skill 03 แทน ไม่ใช่แก้เอง) |
| 7 | `risk-analysis` (05) | `reports/05-risk-analysis.md` | **ใช่ (คอลัมน์ Priority)** | v3 = กำหนด P0–P3 ให้ครบ 11 เคส |
| 8 | `test-data-generator` (06) | `reports/06-test-data.md` | ไม่ (เป็นแผนก่อนรัน) | ค่าจริงจะถูกใส่กลับ Workbook ทีหลังโดย Skill 06a |
| 9 | `qa-automation-script` (06a) | `automation/`, `evidence/06a-automation/` | **ใช่ (Status/Actual Result/Test Data/Remarks/Execution Date/Test By/Test Photo)** | v4 = รัน Automation จริง 11 เคส (Pass 10, Fail 1 คือ TC-005) |
| 10 | `result-analysis` (07) | `reports/07-result-analysis.docx` + `reports/07-photo-evidence.docx` | **ไม่ — ห้ามแก้เด็ดขาดตาม SKILL.md** | ทำแล้ว (Partial): Coverage 11/11 บน Chromium, พบ Root Cause จริง 1 ประเด็น (TC-005, P1) |
| 11 | `qa-reconcile` (RTM, 07a) | `workbook/RTM-traceability-matrix.xlsx` | **ไม่ — ห้ามแก้เด็ดขาดตาม SKILL.md** | ทำแล้ว: คำนวณ Traceability ใหม่สดจากไฟล์ต้นทาง (ไม่เชื่อชีต Requirement Matrix เดิม) ตรงกัน 100% ไม่พบความไม่ตรงกัน — พบ Finding 4 รายการ (TC-010 Orphan → Accepted Gap, REQ-NF-003/004 ไม่มี Test Case → Defer ต่อ, BR-002/FLOW-001 ยังมี Assumption ค้างจาก RISK-001 → ติดตามต่อ) บันทึกไว้ในชีต Findings ของไฟล์ผลลัพธ์ |
| 12 | `qa-report-generator` (08) | `reports/08-qa-report.docx` | **ไม่ — ห้ามแก้เด็ดขาดตาม SKILL.md** | ทำแล้ว (Provisional เพราะ Stage 07 ยังเป็น Partial): อ่านสดจาก Workbook + RTM Findings สรุปผลเป็น **Conditional Go** (ไม่มี P0 Fail แต่มี P1 Fail 1 เคส คือ TC-005) |
| 13 | `redmine-logging` (09) | Ticket จริงใน Redmine + `reports/09-redmine-log.md` | **ใช่ เฉพาะคอลัมน์ "Issue link"** (ถ้าเลือก Export แทนจะไม่แก้) | ทำแล้ว: เปิด **Ticket #9** จริงใน Planio ให้ TC-005 (เคสเดียวที่ Fail จริง) บันทึกลิงก์กลับเข้า Workbook แล้ว (v5) — เปิดผ่านหน้าเว็บเองเพราะ network allowlist ของ environment บล็อกโดเมน Planio ไว้ (ดู `reports/09-redmine-log.md`) |
| 14 | `qa-retest` (10) | `reports/10-qa-retest.md` | **ใช่ (Status/Actual Result/Remarks/Execution Date/Test Photo)** | ทำแล้ว: Dev แก้บั๊ก TC-005 จริงใน `automation/demo-app/server.py` (BR-002 → case-insensitive) เปลี่ยน Ticket #9 เป็น `Resolved` → Retest จริงด้วย Playwright บน Chromium **ผล Pass** บันทึกกลับ Workbook แล้ว (v6) |
| 15 | `qa-retest-closure` (10a) | คอมเมนต์/ปิด Ticket ใน Redmine จริง + `reports/10a-qa-retest-closure.md` | **ไม่** | ทำแล้ว: Recheck ผล Retest ของ TC-005 แล้วปิด **Ticket #9** จริงใน Planio (คอมเมนต์ "Retest → Pass" พร้อมแนบภาพ) — อ่าน Workbook เป็นข้อมูลอ้างอิงเท่านั้น ไม่เขียนกลับ |

ครบทั้ง 15 Skill แล้ว — TC-005 (บั๊กเดียวที่พบจริงในตัวอย่างนี้) ผ่านวงจรครบ: เปิด Ticket (09) → Retest
หลัง Dev แก้ (10) → ปิด Ticket จริง (10a)

**อยากเห็นของจริงแบบเปิดไฟล์เทียบกันเลยไม่ต้องอ่านตาราง?** ไปที่ [`workbook/history/`](./workbook/history/)
— มีสำเนา Workbook แยกไฟล์ตามจุดที่ Skill 03/04/05/06/06a/09/10 ทำงานจริง เปิด 2 ไฟล์ข้างๆ กันแล้วเห็นความ
ต่าง (หรือความเหมือนเป๊ะในกรณีที่ Skill นั้นไม่ได้แก้ไข) ได้ทันที

### แล้วดูหลักฐานการแก้ไข Workbook แบบ "จับต้องได้" ได้จากไหน

เปิด [`workbook/03-test-case-workbook.xlsx`](./workbook/03-test-case-workbook.xlsx) ไปที่ชีต **"Document Control"** — มีตาราง Version History ที่บันทึกไว้
อัตโนมัติทุกครั้งที่มี Skill ไหนแก้ไฟล์นี้จริง (Version / วันที่ / **ชื่อ Skill ที่แก้** / สรุปว่าแก้อะไร) ปัจจุบัน
(หลัง Stage 10) หน้าตาเป็นแบบนี้:

| Version | วันที่ | แก้โดย (Skill) | สรุปการเปลี่ยนแปลง |
|---|---|---|---|
| 1 | 2026-09-19 | test-case-generator | สร้าง Workbook ครั้งแรก |
| 2 | 2026-09-19 | test-case-generator | เพิ่ม Test Case ชุดแรก TC-001 ถึง TC-011 |
| 3 | 2026-09-19 | risk-analysis | กำหนด Priority ให้ Test Case ทั้งหมด 11 เคส |
| 4 | 2026-09-19 | qa-automation-script | รัน Playwright Automation จริง 11 Test Case บน Chromium — TC-005 Fail จริงตาม RISK-001 |
| 5 | 2026-09-19 | redmine-logging | บันทึกลิงก์ Redmine Ticket #9 กลับเข้าคอลัมน์ "Issue link" ของ TC-005 |
| 6 | 2026-09-19 | qa-retest | Retest TC-005 หลัง Dev แก้ Ticket #9 — ผล Pass |

ตารางนี้คือ "ของจริง" ที่พิสูจน์ได้ว่า Skill ไหนแตะไฟล์นี้บ้าง เพราะเขียนอัตโนมัติโดยสคริปต์
(`qa_workbook.py`) ทุกครั้งที่มีการแก้ไข ไม่ใช่คำอธิบายที่พิมพ์เอาไว้เฉยๆ — เทียบกับตาราง Skill Usage
Map ด้านบนแล้วจะเห็นตรงกันว่า Skill ที่ควร "ห้ามแก้" (04 รอบนี้/07/07a/08/10a) จะไม่มีชื่อโผล่ในตาราง
Version History นี้เลย ในขณะที่ Skill ที่ควรแก้จริง (03/05/06a/09/10) จะมีชื่อโผล่มาทุกครั้ง

## บั๊กจริงที่เจอในตัวอย่างนี้ (TC-005 / RISK-001)

ตั้งใจปลูกความคลุมเครือไว้ตั้งแต่ต้นสาย (`sources/.../SRC-002-slack-chat-log.md`) ว่าทีม Dev ตัดสินใจ
ชั่วคราวให้เช็คอีเมลซ้ำแบบ exact-match (case-sensitive) — ประเด็นนี้ถูกส่งต่อและยืนยันความเสี่ยงผ่านมา
ทุก Stage: [`reports/01-requirement-review.md`](./reports/01-requirement-review.md) (BR-002 + RISK-001 High) → [`reports/02-e2e-flow.md`](./reports/02-e2e-flow.md) (DP-002) →
`workbook/03-test-case-workbook.xlsx` (TC-005) → [`reports/04-coverage-review.md`](./reports/04-coverage-review.md) (ยืนยัน Deferred ไม่ใช่จุดตกหล่น) →
[`reports/05-risk-analysis.md`](./reports/05-risk-analysis.md) (Priority P1) → **`06a` รันจริงแล้ว Fail จริง** ตามที่คาดไว้ทุกประการ →
[`reports/09-redmine-log.md`](./reports/09-redmine-log.md) (เปิด Ticket #9 จริงใน Planio ให้ Dev แก้) → [`reports/10-qa-retest.md`](./reports/10-qa-retest.md) (Dev แก้บั๊กจริง
ใน `automation/demo-app/server.py` แล้ว Retest ด้วย Playwright จริง ผล `Pass`) → **[`reports/10a-qa-retest-closure.md`](./reports/10a-qa-retest-closure.md)
(ปิด Ticket #9 จริง พร้อมคอมเมนต์ยืนยันผลและแนบภาพ)** — สามารถไล่อ่านตามลำดับไฟล์ด้านบนเพื่อดู
Traceability ของบั๊กตัวนี้ตั้งแต่ต้นจนจบ (เปิด → พบ → แจ้ง Dev → แก้ → ยืนยันด้วย Retest จริง → ปิด Ticket)
ได้ครบวงจรทั้ง 15 Skill

## สถานะปัจจุบัน (อัปเดตล่าสุดจาก `_pipeline-manifest.md`)

| Stage | สถานะ |
|---|---|
| 00-pre, 00 | Pending Review (ไม่บังคับต้อง approve แต่ยังไม่ปิด) |
| 01, 02, 03, 04, 05, 06 | Complete |
| 06a | In Progress — รันได้จริงแค่ Chromium (environment นี้ไม่มี Safari/Firefox/Edge ติดตั้ง) |
| **07** | **Complete (Partial)** — วิเคราะห์ผลเท่าที่มี (Chromium) ตามที่ผู้ใช้ยืนยัน |
| **RTM** | **Complete** — Traceability ตรงกับชีตเดิม 100%, Finding ทั้งหมดผ่านการตัดสินใจของผู้ใช้แล้ว |
| **08** | **Complete (Provisional)** — ผล **Conditional Go** (มี P1 Fail ค้าง 1 เคส คือ TC-005, Browser ยังไม่ครบ) |
| **09** | **Complete** — เปิด Redmine/Planio Ticket #9 ให้ TC-005 แล้ว |
| **10** | **Complete** — Dev แก้ TC-005 แล้ว (Ticket #9 = Resolved), Retest ด้วย Playwright จริง **Pass** |
| **10a** | **Complete (รอบนี้)** — ปิด Redmine Ticket #9 จริงแล้ว (closed=1, commented=0) |

ดูรายละเอียดเต็มและเหตุผลของแต่ละสถานะได้ที่ [`_pipeline-manifest.md`](./_pipeline-manifest.md)
