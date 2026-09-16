#!/usr/bin/env python3
"""
create_redmine_issues.py — สร้าง Ticket จริงใน Redmine ผ่าน REST API สำหรับ Test Case ที่ Fail จริง

**คำเตือนความปลอดภัยที่สำคัญที่สุด**: ห้าม log/print ค่า REDMINE_API_KEY แบบเต็มออกทาง stdout/stderr
หรือเขียนลงไฟล์ใดๆ (รวมถึง manifest, output JSON, error message) เด็ดขาด — สคริปต์นี้รับ URL/API Key
ผ่าน environment variable เท่านั้น (REDMINE_URL, REDMINE_API_KEY) ไม่รับผ่าน --argument โดยตรง เพื่อไม่ให้
ค่าไปโผล่ใน shell history / process list (`ps aux`) ซึ่งมองเห็นได้ง่ายกว่า environment variable

คำสั่ง:
  list-preview --cases-json <path> [--workbook-label <ข้อความ>]
      พิมพ์รายงานที่มนุษย์อ่านง่าย (banner + รายการ [Bug #] ทีละใบ + เมนู Action) ให้ผู้ใช้ดูก่อนตัดสินใจ
      — ไม่ยิง API จริง ไม่ต้องมี credential เลย เรียงลำดับ Bug ตาม Priority ก่อน (P0 มาก่อน P3) เสมอ
      หมายเหตุ: เมนู [?] ท้ายรายงานเป็นแค่ข้อความที่พิมพ์ออกมาเฉยๆ ไม่ได้ใช้ input() รอค่าจริง เพราะสคริปต์นี้
      ถูกเรียกโดย Claude ไม่ใช่ผู้ใช้พิมพ์ใส่ Terminal เอง — Claude มีหน้าที่ paste รายงานนี้ให้ผู้ใช้ดูในแชท
      ตรงๆ แล้วถามตัวเลือกเดียวกันผ่านเครื่องมือถามคำถามจริงแทน (ดูขั้นตอนที่ 3 ของ SKILL.md)

  preview --cases-json <path>
      เหมือน list-preview แต่พิมพ์เป็น JSON ดิบ (จำนวนที่จะสร้าง/ข้าม + subject) เผื่อต้องเอาไปใช้ต่อ
      ทางโปรแกรม — ไม่ยิง API จริงเช่นกัน

  export-excel --cases-json <path> --out <09-redmine-bugs-export.xlsx> [--only <TC-017,TC-009,...>]
      สร้างไฟล์ Excel สรุปรายการบั๊กที่เลือก (ไม่ยิง API เข้า Redmine เลย) ใช้ตอนผู้ใช้เลือก Action
      "Export เป็นไฟล์ Excel เท่านั้น" ในขั้นตอนที่ 3 — **การ export ไม่ถือว่าเปิด Ticket แล้ว** SKILL.md
      จะไม่แก้คอลัมน์ "Issue link" ใน Workbook ให้หลังขั้นตอนนี้ ใส่ --only เป็น comma-separated TC-ID
      เมื่อผู้ใช้เลือกเฉพาะบางเคส (ไม่ใส่ = export ทุกเคสที่ยังไม่มี existing_issue_link)

  create --cases-json <path> --project <id หรือ identifier> --tracker <ชื่อ หรือ id> --out <result.json>
         [--assignee <redmine user id>] [--only <TC-017,TC-009,...>]
      สร้าง Ticket จริงทุกใบตามรายการใน cases-json (ยกเว้นรายการที่มี existing_issue_link อยู่แล้ว — ข้าม
      อัตโนมัติเพื่อกัน Ticket ซ้ำเวลารัน Skill ซ้ำ) อ่าน REDMINE_URL/REDMINE_API_KEY จาก environment
      variable เท่านั้น ถ้าไม่มีค่าจะหยุดทำงานทันทีไม่เดา/ไม่ fallback ไปที่ไหน ใส่ --only เป็น
      comma-separated TC-ID เมื่อผู้ใช้เลือก Action "เลือกเฉพาะบางเคส" แทนที่จะเปิดทั้งหมด

cases-json schema (list ของแต่ละ Test Case ที่ Status=Fail จริง):
[
  {
    "tc_id": "TC-017",
    "module": "ตะกร้าสินค้า - โค้ดส่วนลด",        # ใช้แสดงใน list-preview/export-excel/email เท่านั้น
    "title": "ลบโค้ด A แล้วใส่โค้ด B ต่อทันที...", # Test Scenario ล้วนๆ ไม่ต้องมี [Priority]/TC-ID นำหน้า
    "remark": "ระบบนับสิทธิ์การใช้โค้ด A ทันที...", # Summary บรรทัดเดียว (ค่าเดียวกับบรรทัดแรกของ description)
    "steps": ["กดปุ่ม \"ลบโค้ด\"...", "กรอกโค้ด B...", "..."],  # ใช้ใน email เท่านั้น (ขั้นตอนที่ 6)
    "screenshot_path": "screenshots/Chromium/TC-017.png",
    "subject": "[P2] TC-017: ...",              # เตรียมมาให้พร้อมใช้ ไม่ต้องประกอบเองในสคริปต์นี้
    "description": "**Priority**: P2\\n...",     # ข้อความเต็ม เตรียมมาให้พร้อมใช้เช่นกัน
    "priority": "P2",
    "existing_issue_link": ""                    # ถ้ามีค่าอยู่แล้ว = เคยเปิด Ticket ไปแล้ว จะถูกข้าม
  }, ...
]
(module/title/remark/steps/screenshot_path จำเป็นเฉพาะตอนใช้ list-preview, export-excel หรือ
scripts/send_email_notification.py (ขั้นตอนที่ 6) เท่านั้น — คำสั่ง create ใช้แค่
tc_id/subject/description/priority/existing_issue_link เหมือนเดิม ไม่กระทบของเก่า)

ผลลัพธ์ (--out, และพิมพ์ออก stdout ด้วย):
{
  "created": [{"tc_id": ..., "issue_id": ..., "url": ..., "subject": ..., "priority": ...}],
  "skipped": [{"tc_id": ..., "reason": "..."}],
  "failed":  [{"tc_id": ..., "error": "..."}]   # ข้อความ error ต้องไม่มี API Key ปนอยู่ (ดู _headers)
}
(ไฟล์ --out นี้เอาไปใช้ต่อกับ scripts/send_email_notification.py คำสั่ง print-success ได้เลย เพื่อพิมพ์
รายงานสรุปความสำเร็จ + ถามผู้ใช้ว่าจะส่งอีเมลแจ้งเตือน Developer ต่อไหม — ดูขั้นตอนที่ 6 ของ SKILL.md)

หมายเหตุเรื่อง Priority: Redmine แต่ละ instance ตั้งค่า priority_id ไม่เหมือนกัน (Low/Normal/High/Urgent/...
ตัวเลข id ต่างกันไปตามการตั้งค่าของแต่ละองค์กร) สคริปต์นี้จึง**ไม่เดา/ไม่ตั้งค่า priority_id ให้อัตโนมัติ**
เพื่อกันสร้าง Ticket ผิด Priority แบบเงียบๆ — ใส่ค่า Priority (P0-P3) ไว้ใน subject/description แทนให้เห็น
ชัดเจนแทน ถ้าต้องการ map ไปยัง priority_id จริงของ Redmine instance นั้นๆ ต้องเพิ่ม logic เองภายหลัง
(เช่น ดึงจาก GET /enumerations/issue_priorities.json มา map ชื่อเทียบกับ P0-P3 เอง)
"""
import argparse
import json
import os
import sys
import textwrap

import requests

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def _priority_rank(priority):
    return PRIORITY_ORDER.get(str(priority).strip().upper(), 99)


def _filter_only(cases, only):
    """ใช้ร่วมกันระหว่าง create/export-excel — --only รับ TC-ID คั่นด้วย comma (ไม่สนตัวพิมพ์เล็ก/ใหญ่)
    ถ้าระบุ TC-ID ที่ไม่มีอยู่ใน cases-json เลยให้แจ้ง error ทันทีแทนที่จะเงียบๆ ข้ามไป เพราะอาจเป็นเพราะ
    ผู้ใช้พิมพ์ TC-ID ผิดตอนเลือกเฉพาะบางเคส ซึ่งอันตรายกว่าปล่อยผ่าน (จะทำให้เข้าใจผิดว่า export/สร้างแล้ว
    ทั้งที่จริงไม่มีเคสนั้นอยู่)"""
    if not only:
        return cases
    wanted = {t.strip().upper() for t in only.split(",") if t.strip()}
    have = {c["tc_id"].strip().upper() for c in cases}
    missing = wanted - have
    if missing:
        sys.exit(f"ไม่พบ TC-ID ต่อไปนี้ใน cases-json: {sorted(missing)} — เช็คว่าพิมพ์ถูกหรือยัง")
    return [c for c in cases if c["tc_id"].strip().upper() in wanted]


def _headers(api_key):
    return {"X-Redmine-API-Key": api_key, "Content-Type": "application/json"}


def _resolve_tracker_id(base_url, api_key, tracker):
    if str(tracker).strip().isdigit():
        return int(tracker)
    resp = requests.get(f"{base_url.rstrip('/')}/trackers.json", headers=_headers(api_key), timeout=20)
    resp.raise_for_status()
    trackers = resp.json().get("trackers", [])
    for t in trackers:
        if t["name"].strip().lower() == str(tracker).strip().lower():
            return t["id"]
    names = [t["name"] for t in trackers]
    raise ValueError(f'ไม่พบ Tracker ชื่อ "{tracker}" ใน Redmine instance นี้ — Tracker ที่มีจริง: {names}')


def cmd_preview(args):
    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)
    todo = [c for c in cases if not (c.get("existing_issue_link") or "").strip()]
    skip = [c for c in cases if (c.get("existing_issue_link") or "").strip()]
    print(json.dumps({
        "จะสร้าง Ticket ให้ (จำนวน)": len(todo),
        "จะสร้าง Ticket ให้": [
            {"tc_id": c["tc_id"], "subject": c["subject"]} for c in todo
        ],
        "ข้าม เพราะมี Issue link อยู่แล้ว (จำนวน)": len(skip),
        "ข้าม": [
            {"tc_id": c["tc_id"], "existing_issue_link": c["existing_issue_link"]} for c in skip
        ],
    }, ensure_ascii=False, indent=2))


def _wrap_field(label, value, width=70, indent="  "):
    """พิมพ์ '• Label: <value>' แบบ bullet โดยตัดบรรทัดยาวๆ ให้บรรทัดต่อเยื้อง 2 ช่องว่าง (ตามที่ยืนยัน
    รูปแบบไว้ใน mockup-preview-and-confirm.md — ไม่ใช้คอลัมน์ตายตัวแบบ fixed-width เพราะความกว้างจริงของ
    ตัวอักษรไทยกับอังกฤษในแต่ละ font ไม่เท่ากัน ใช้ hanging indent ง่ายๆ พอ)"""
    prefix = f"• {label}: "
    wrapped = textwrap.wrap(str(value), width=width) or [""]
    lines = [prefix + wrapped[0]]
    for extra in wrapped[1:]:
        lines.append(indent + extra)
    return "\n".join(lines)


def _print_list_preview(cases, workbook_label):
    todo = [c for c in cases if not (c.get("existing_issue_link") or "").strip()]
    skip = [c for c in cases if (c.get("existing_issue_link") or "").strip()]
    todo.sort(key=lambda c: _priority_rank(c.get("priority")))

    bar = "=" * 70
    thin = "-" * 70
    lines = [bar, "🐞 SKILL 09: REDMINE BUG LOGGING PREVIEW", bar]
    if workbook_label:
        lines.append(f"📂 Loaded Test Case Workbook: {workbook_label}")
    lines.append(f"🔍 Found {len(todo)} Failed Test Cases (พร้อมเปิด Ticket)")
    if skip:
        lines.append(f"⏭ ข้ามอัตโนมัติ (มี Ticket อยู่แล้ว): {len(skip)} เคส")
    lines.append(thin)

    for i, c in enumerate(todo, start=1):
        lines.append(f"[Bug #{i}]")
        lines.append(_wrap_field("Module", c.get("module", "-")))
        title = c.get("title", "-")
        lines.append(_wrap_field("Title", f"{c['tc_id']} · {title}"))
        lines.append(_wrap_field("Priority", c.get("priority", "-")))
        lines.append(_wrap_field("Remark", c.get("remark", "-")))
        lines.append(_wrap_field("Attached Proof", c.get("screenshot_path", "-")))
        lines.append(thin)

    lines.append("[?] เลือก Action:")
    lines.append(f"  [1] เปิด Ticket ทั้งหมด ({len(todo)} เคส) เข้า Redmine พร้อมแนบ Screenshot")
    lines.append("  [2] เลือกเฉพาะบางเคส (เช่น 1)")
    lines.append("  [3] Export รายการเป็นไฟล์ Excel เท่านั้น (ยังไม่เปิด Ticket เข้า Redmine)")
    lines.append("  [4] Cancel — ไม่ทำอะไรเลย")
    print("\n".join(lines))


def cmd_list_preview(args):
    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)
    _print_list_preview(cases, args.workbook_label)


def cmd_export_excel(args):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)

    todo = [c for c in cases if not (c.get("existing_issue_link") or "").strip()]
    todo = _filter_only(todo, args.only)
    todo.sort(key=lambda c: _priority_rank(c.get("priority")))

    wb = Workbook()
    ws = wb.active
    ws.title = "Redmine Bugs Export"

    headers = [
        "No.", "Test Case ID", "Module", "Title", "Priority", "Remark",
        "Screenshot Path", "Subject", "Description",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for i, c in enumerate(todo, start=1):
        ws.append([
            i,
            c["tc_id"],
            c.get("module", ""),
            c.get("title", ""),
            c.get("priority", ""),
            c.get("remark", ""),
            c.get("screenshot_path", ""),
            c.get("subject", ""),
            c.get("description", ""),
        ])

    widths = [5, 12, 22, 40, 9, 40, 26, 40, 60]
    for idx, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(args.out)
    result = {"exported": len(todo), "out": args.out, "note": "Export เท่านั้น ยังไม่เปิด Ticket จริง — ไม่แก้ Issue link ใน Workbook"}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_create(args):
    base_url = os.environ.get("REDMINE_URL", "").strip()
    api_key = os.environ.get("REDMINE_API_KEY", "").strip()
    if not base_url or not api_key:
        sys.exit(
            "ต้องตั้งค่า environment variable REDMINE_URL และ REDMINE_API_KEY ก่อนเรียกคำสั่งนี้เสมอ "
            "(ห้ามส่งผ่าน --argument โดยตรงเพราะจะโผล่ใน shell history/process list) — ไม่มีค่า default "
            "ให้ fallback ไปที่ไหนทั้งสิ้น"
        )

    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)
    cases = _filter_only(cases, args.only)

    try:
        tracker_id = _resolve_tracker_id(base_url, api_key, args.tracker)
    except requests.exceptions.RequestException as e:
        sys.exit(f"เชื่อมต่อ Redmine ไม่สำเร็จตอนค้นหา Tracker (เช็ค REDMINE_URL / network access ก่อน): {type(e).__name__}: {e}")
    except ValueError as e:
        sys.exit(str(e))

    created, skipped, failed = [], [], []
    for c in cases:
        tc_id = c["tc_id"]
        if (c.get("existing_issue_link") or "").strip():
            skipped.append({"tc_id": tc_id, "reason": f"มี Issue link อยู่แล้ว: {c['existing_issue_link']}"})
            continue

        payload = {
            "issue": {
                "project_id": args.project,
                "tracker_id": tracker_id,
                "subject": c["subject"],
                "description": c["description"],
            }
        }
        if args.assignee:
            payload["issue"]["assigned_to_id"] = args.assignee

        try:
            resp = requests.post(
                f"{base_url.rstrip('/')}/issues.json",
                headers=_headers(api_key), json=payload, timeout=30,
            )
        except requests.exceptions.RequestException as e:
            failed.append({"tc_id": tc_id, "error": f"เชื่อมต่อ Redmine ไม่สำเร็จ: {type(e).__name__}: {e}"})
            continue

        if resp.status_code not in (200, 201):
            # resp.text อาจมีรายละเอียด error ของ Redmine เอง (เช่น field ไหนไม่ถูกต้อง) — ไม่มี API Key ปนอยู่
            failed.append({"tc_id": tc_id, "error": f"HTTP {resp.status_code}: {resp.text[:500]}"})
            continue

        issue = resp.json()["issue"]
        issue_id = issue["id"]
        url = f"{base_url.rstrip('/')}/issues/{issue_id}"
        # เก็บ subject ไว้ด้วย (ไม่ได้เก็บแค่ tc_id/issue_id/url แบบเดิม) เพราะ send_email_notification.py
        # ต้องใช้ subject มาแสดงในรายงานสรุป/อีเมล โดยไม่ต้องเปิด cases-json ซ้ำ
        created.append({"tc_id": tc_id, "issue_id": issue_id, "url": url, "subject": c["subject"], "priority": c.get("priority", "")})

    result = {"created": created, "skipped": skipped, "failed": failed}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("preview")
    pv.add_argument("--cases-json", required=True)

    lp = sub.add_parser("list-preview")
    lp.add_argument("--cases-json", required=True)
    lp.add_argument("--workbook-label", default=None, help="ข้อความแสดงเป็น 'Loaded Test Case Workbook' (optional)")

    ex = sub.add_parser("export-excel")
    ex.add_argument("--cases-json", required=True)
    ex.add_argument("--out", required=True)
    ex.add_argument("--only", default=None, help="comma-separated TC-ID เฉพาะที่จะ export (ไม่ใส่ = ทุกเคส)")

    cr = sub.add_parser("create")
    cr.add_argument("--cases-json", required=True)
    cr.add_argument("--project", required=True, help="Redmine project id (ตัวเลข) หรือ identifier (slug)")
    cr.add_argument("--tracker", required=True, help='ชื่อ Tracker เช่น "Bug" (หรือใส่ id ตัวเลขตรงๆ ก็ได้)')
    cr.add_argument("--assignee", default=None, help="Redmine user id ที่จะ assign ticket ให้ (optional)")
    cr.add_argument("--only", default=None, help="comma-separated TC-ID เฉพาะที่จะสร้าง (ไม่ใส่ = ทุกเคสที่ยังไม่มี Issue link)")
    cr.add_argument("--out", required=True)

    args = p.parse_args()
    if args.cmd == "preview":
        cmd_preview(args)
    elif args.cmd == "list-preview":
        cmd_list_preview(args)
    elif args.cmd == "export-excel":
        cmd_export_excel(args)
    elif args.cmd == "create":
        cmd_create(args)


if __name__ == "__main__":
    main()
