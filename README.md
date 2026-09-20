# QA Pipeline — Process Flow

15 Skill ที่ทำงานต่อเนื่องกัน ตั้งแต่รวบรวม Requirement จนถึงปิด Ticket ใน Redmine หลังแก้บั๊ก ใช้เป็น Framework อ้างอิงเมื่อเริ่มทดสอบฟีเจอร์ใหม่ ทุก Skill ผ่านการรันจริงครบทั้งสายกับฟีเจอร์ตัวอย่าง "Newsletter Email Subscription" มาแล้วอย่างน้อย 1 รอบเต็ม (รวม Redmine จริง — ดู [`examples/newsletter-email-subscription/`](./examples/newsletter-email-subscription/))

**สรุป**: 15 Stage / 4 Phase เรียงเส้นตรง ยกเว้น Phase สุดท้ายวนซ้ำได้ · เกือบทั้งหมดอัตโนมัติ มีเพียง 3 จุดที่ต้องรอคนอนุมัติ (Stage 00-pre, 00, และลายเซ็นใน `08-qa-report.docx`) · Stage 09–10a ต่อ Redmine จริง ต้องขอ URL/API Key ใหม่ทุกครั้ง (ดู [ความปลอดภัย](#ความปลอดภัยของข้อมูลรับรอง))

---

## โครงสร้าง Repository

```
.
├── skills/                    # ตัว Pipeline framework — นิยาม 15 Skill
│   ├── 00-pre-source-ingest/
│   ├── 00-test-plan/
│   ├── 01-requirement-review/
│   ├── 02-e2e-flow-designer/
│   ├── 03-test-case-generator/
│   ├── 04-coverage-review/
│   ├── 05-risk-analysis/
│   ├── 06-test-data-generator/
│   ├── 06a-qa-automation-script/
│   ├── 07-result-analysis/
│   ├── 07a-RTM-qa-reconcile/
│   ├── 08-qa-report-generator/
│   ├── 09-redmine-logging/
│   ├── 10-qa-retest/
│   ├── 10a-qa-retest-closure/
│   └── _shared/                # โมดูลใช้ร่วมกันหลาย Skill (ไม่ใช่ Stage ในสาย Flow)
├── examples/
│   └── newsletter-email-subscription/   # ตัวอย่างรันจริงครบทั้ง 15 Skill กับฟีเจอร์เล็กๆ 1 ฟีเจอร์
│                                         # (รวม Redmine Ticket จริง, Playwright Automation จริง — ดู README ในนั้น)
├── docs/
│   └── qa-pipeline-flow.html  # แผนภาพกระบวนการแบบ standalone (ไฟล์เดียวกับ Mermaid ด้านล่าง เปิดดูได้โดยไม่ต้องพึ่ง GitHub renderer)
└── test-reports/               # รายงานผลการทดสอบ Skill ระหว่างพัฒนา (ไม่ใช่ส่วนหนึ่งของ Pipeline)
```

โฟลเดอร์ `skills/` ตั้งชื่อตามลำดับ Flow จริง (00 → 10a) — อยากเห็นตัวอย่างการรันจริงแบบจับต้องได้ (ไฟล์
เอกสาร, Test Case Workbook ทุก Version, สกรีนช็อตหลักฐานทุก Skill ที่แตะระบบภายนอก) ไปที่
[`examples/newsletter-email-subscription/`](./examples/newsletter-email-subscription/) ได้เลย

---

## ภาพรวม 4 Phase

| Phase | ขอบเขต | Stage |
|---|---|---|
| A — วิเคราะห์ Requirement | รวบรวมข้อมูล วางแผนทดสอบ ออกแบบ Test Case | 00-pre, 00, 01–05 |
| B — เตรียมข้อมูล/รันทดสอบ | สร้าง Test Data, รัน Automation, สรุปผล, ตรวจ Traceability | 06, 06a, 07, RTM |
| C — สรุปผล/ตัดสินใจ | รวมผลเป็นรายงาน Go / No-Go | 08 |
| D — ปิดบั๊ก (วนซ้ำ) | เปิด Ticket → Retest → ปิด Ticket จนไม่มี Fail เหลือ | 09, 10, 10a |

---

## แผนภาพกระบวนการ

```mermaid
flowchart TD
    subgraph A["Phase A — วิเคราะห์ Requirement"]
        direction TB
        A1["00-pre · source-ingest<br/>รวบรวม Requirement ต้นทาง"]:::gate
        A2["00 · test-plan<br/>วางแผนการทดสอบ"]:::gate
        A3["01 · requirement-review<br/>สกัด Business Rule"]:::auto
        A4["02 · e2e-flow-designer<br/>ออกแบบ User Flow"]:::auto
        A5["03 · test-case-generator<br/>สร้าง Test Case"]:::auto
        A6["04 · coverage-review<br/>ตรวจความครบถ้วน"]:::auto
        A7["05 · risk-analysis<br/>จัดลำดับความสำคัญ"]:::auto
        A1 --> A2 --> A3 --> A4 --> A5 --> A6 --> A7
    end

    subgraph B["Phase B — เตรียมข้อมูลและรันทดสอบจริง"]
        direction TB
        B1["06 · test-data-generator<br/>สร้างข้อมูลทดสอบ"]:::auto
        B2["06a · qa-automation-script<br/>รัน Automation จริง"]:::auto
        B3["07 · result-analysis<br/>สรุปผลและ Root Cause"]:::auto
        B4["RTM · qa-reconcile<br/>Traceability Matrix"]:::auto
        B1 --> B2 --> B3 --> B4
    end

    subgraph C["Phase C — สรุปผลและตัดสินใจ"]
        direction TB
        C1["08 · qa-report-generator<br/>สรุป Go / No-Go"]:::gate
        C2{"มี Test Case Fail ค้างหรือไม่"}
        C1 --> C2
    end

    subgraph D["Phase D — ปิดบั๊ก (วนซ้ำ)"]
        direction TB
        D1["09 · redmine-logging<br/>เปิด Ticket"]:::auto
        D2["10 · qa-retest<br/>Retest หลังแก้ไข"]:::auto
        D3["10a · qa-retest-closure<br/>ปิด / คอมเมนต์ Ticket"]:::auto
        D1 --> D2 --> D3
        D3 -. "ยังมี Fail เหลือ" .-> D1
    end

    A7 --> B1
    B4 --> C1
    C2 -- "ไม่มี" --> DONE(["ปิด Feature ได้"])
    C2 -- "มี" --> D1
    D3 -- "Pass ครบทุกเคส" --> DONE

    classDef auto fill:#eef5f3,stroke:#0f766e,color:#0b3630,stroke-width:1px;
    classDef gate fill:#faf0dd,stroke:#b45309,color:#4a2e04,stroke-width:1.5px;
    classDef terminal fill:#e7f4ea,stroke:#15803d,color:#0d3a1f,stroke-width:1.5px;
    class DONE terminal;
```

สีเขียวอ่อน = อัตโนมัติทั้งหมด · สีน้ำตาลอ่อน = ต้องอนุมัติ/ลงนามจากคนก่อนถือว่าเสร็จ

ดูแผนภาพนี้แบบ standalone (ไฟล์ HTML เดี่ยว ไม่ต้องพึ่ง Mermaid renderer ของ GitHub) ได้ที่
[`docs/qa-pipeline-flow.html`](./docs/qa-pipeline-flow.html)

---

## ตารางอ้างอิงแต่ละ Stage

| Stage | Skill | หน้าที่ | ข้อมูลนำเข้า | ผลลัพธ์ | ประเภท |
|---|---|---|---|---|---|
| 00-pre | `00-pre-source-ingest` | รวบรวมแหล่งข้อมูลต้นทาง สรุปเป็นชุดเดียว ชี้จุดขัดแย้ง/ช่องว่าง | ไฟล์ต้นฉบับดิบจากผู้ใช้ | `00-pre-source-ingest.md` | ต้องอนุมัติ |
| 00 | `00-test-plan` | วางแผนทดสอบ: ขอบเขต, Exit Criteria, Environment, ตารางเวลา, ความเสี่ยง | ผลจาก 00-pre, กำหนดการจริง | `testplans/TP-*.md` | ต้องอนุมัติ |
| 01 | `01-requirement-review` | สกัด Business Rule และ Open Question | 00-pre, 00 | `01-requirement-review.md` | อัตโนมัติ |
| 02 | `02-e2e-flow-designer` | ออกแบบ User Flow จาก Business Rule | 01 | `02-e2e-flow.md` | อัตโนมัติ |
| 03 | `03-test-case-generator` | สร้าง Test Case ครอบคลุมทุก Rule/Flow | 01, 02, ค่า Environment/Config จริง | `03-test-case-workbook.xlsx` | อัตโนมัติ |
| 04 | `04-coverage-review` | ตรวจความครบถ้วนของ Test Case เทียบ Requirement | Workbook (03) เทียบ 01+02 | `04-coverage-review.md` | อัตโนมัติ |
| 05 | `05-risk-analysis` | กำหนด Priority (P0–P3) ให้ทุก Test Case | Workbook (03) | `05-risk-analysis.md` | อัตโนมัติ |
| 06 | `06-test-data-generator` | แปลง Test Data ให้ใช้ทดสอบได้จริง | Workbook (03) | `06-test-data.md` | อัตโนมัติ |
| 06a | `06a-qa-automation-script` | เขียน/รัน Automation จริง บันทึกผลและหลักฐาน | Workbook (03), 06, Environment จริง | `automation/*`, `screenshots/*`, ผลใน Workbook | อัตโนมัติ |
| 07 | `07-result-analysis` | สรุปผลรวม วิเคราะห์ Root Cause ของ Fail/Blocked | Workbook หลัง 06a | `07-result-analysis.docx`, `07-photo-evidence.docx` | อัตโนมัติ |
| RTM | `07a-RTM-qa-reconcile` | คำนวณ Traceability Matrix ใหม่จากข้อมูลจริงเสมอ | 01, 02, Workbook (03) | `RTM-traceability-matrix.xlsx` | อัตโนมัติ |
| 08 | `08-qa-report-generator` | รวมผลทั้งหมดเป็นรายงานสรุป Go / Conditional Go / No-Go | 07, RTM, Workbook, Deadline | `08-qa-report.docx` | ต้องลงนาม |
| 09 | `09-redmine-logging` | เปิด Ticket ให้ทุกเคส Fail พร้อมหลักฐาน แจ้ง Dev | Workbook (เคส Fail), อีเมล Dev | Ticket ใน Redmine, `09-redmine-log.md` | อัตโนมัติ* |
| 10 | `10-qa-retest` | รัน Automation ซ้ำหลัง Dev แก้ไข เทียบผลใหม่ | Workbook (เคสที่มี Issue link) | `10-retest-run-result.json`, ผลใน Workbook | อัตโนมัติ* |
| 10a | `10a-qa-retest-closure` | ปิด Ticket (Pass) หรือคอมเมนต์แจ้งผล (Fail) กลับ Redmine | ผล Retest จาก 10 | `10a-closure-result.json`, สถานะ Ticket อัปเดต | อัตโนมัติ* |

\* Stage 09, 10, 10a อัตโนมัติได้ทั้งหมด แต่ต้องรับ Redmine URL/API Key ใหม่จากผู้ใช้ทุกครั้งที่รัน — ดูหัวข้อถัดไป

---

## วงรอบการปิดบั๊ก (Stage 09–10a)

Stage 09–10a ไม่ใช่ลำดับเชิงเส้นเหมือน Phase อื่น แต่วนซ้ำจนไม่มี Test Case Fail เหลือ:

**09 เปิด Ticket** (แนบหลักฐาน แจ้ง Dev) → **10 Retest** (หลัง Dev แจ้งว่าแก้แล้ว รันเฉพาะเคสที่มี Ticket ค้าง) → **10a ปิด/คอมเมนต์ Ticket** ตามผล Retest → ถ้ายังมี Fail กลับไปเริ่มที่ 09 ใหม่เฉพาะเคสที่ไม่ผ่าน จนกว่าจะ Pass ครบและปิด Ticket หมด จึงถือว่า Pipeline เสร็จสมบูรณ์

---

## ความปลอดภัยของข้อมูลรับรอง

Stage 09–10a ต่อ Redmine จริง จึงมีข้อกำหนดตลอดทั้งสาย:

- Redmine URL และ API Key ต้องขอใหม่จากผู้ใช้ทุกครั้ง ห้ามบันทึก/แคชไว้ในไฟล์ใดๆ
- ตั้งค่าผ่าน Environment Variable เท่านั้น ห้ามส่งผ่าน command-line argument
- กฎเดียวกันใช้กับ SMTP credentials ที่ใช้ส่งอีเมลแจ้ง Dev (อีเมลของ Dev เองไม่ถือเป็นข้อมูลลับ ใช้ซ้ำได้ปกติ)

---

## เงื่อนไขการปิด Feature

Feature จะปิดสมบูรณ์ได้ต่อเมื่อครบทุกข้อ:

1. Stage 01–10a มีสถานะ Complete ใน `_pipeline-manifest.md`
2. ไม่มี Test Case สถานะ Fail ค้างใน Workbook
3. Stage 00-pre และ 00 ได้รับการอนุมัติจริงจากผู้ใช้ (กรอก "QA Review & Sign-off" ด้วยตนเอง)
4. ช่องลงนาม QA Lead และ PM/Product Owner ใน `08-qa-report.docx` ลงนามจริงแล้ว

ข้อ 3–4 ต้องผ่านการกระทำของบุคคลจริงเสมอ ไม่มีกลไกให้ระบบอัตโนมัติทำแทนได้
