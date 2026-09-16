#!/usr/bin/env python3
"""
close_redmine_issues.py — คอมเมนต์ผลการ Retest กลับเข้า Ticket จริงใน Redmine (Pass และ Fail) พร้อมแนบ
ไฟล์ภาพผลการ Retest จริง แล้วปิด Ticket ให้อัตโนมัติเฉพาะเคสที่ Pass เท่านั้น เป็นสคริปต์หลักของ
qa-retest-closure (Skill 10a) — Skill นี้เป็น Skill เดียวในสายที่ **แก้ไข** Ticket ที่มีอยู่แล้ว (Skill 09
แค่สร้างใหม่, Skill 10 แค่อ่านอย่างเดียว)

**คำเตือนความปลอดภัยที่สำคัญที่สุด**: ห้าม log/print ค่า REDMINE_API_KEY แบบเต็มออกทาง stdout/stderr หรือ
เขียนลงไฟล์ใดๆ เด็ดขาด (เหตุผลเดียวกับทุกสคริปต์ที่คุย Redmine ในสายนี้) — รับ URL/API Key ผ่าน environment
variable เท่านั้น (REDMINE_URL, REDMINE_API_KEY) ไม่รับผ่าน --argument โดยตรง

**เรื่อง Textile vs Markdown**: เหมือนกับ create_redmine_issues.py (Skill 09) — Redmine แต่ละ instance
อาจตั้งค่า Text formatting เป็น Textile (ค่าเริ่มต้น ใช้ `*text*` ตัวหนา) หรือ Markdown (ใช้ `**text**`)
ต้องถามผู้ใช้ก่อนทุกครั้งที่รัน Skill นี้ครั้งแรกกับ instance ใหม่ แล้วส่งเข้า `--syntax markdown|textile`

คำสั่ง:
  list-statuses
      พิมพ์รายชื่อ Status ทั้งหมดที่มีจริงใน Redmine instance นี้ (GET /issue_statuses.json) ใช้ช่วยผู้ใช้
      เลือกชื่อ Status ที่จะใช้ตอนปิด Ticket ให้ตรงตัวสะกดเป๊ะๆ (กัน typo) ต้องมี REDMINE_URL/REDMINE_API_KEY
      แล้วเช่นกัน

  list-preview --cases-json <path>
      พิมพ์รายงานที่มนุษย์อ่านง่าย (banner + รายการแยกกลุ่ม Pass/Fail + เมนู Action) ให้ผู้ใช้ Recheck ก่อน
      ตัดสินใจ — ไม่ยิง API จริง ไม่ต้องมี credential เลย เรียงลำดับตาม Priority ก่อนเสมอ (P0 มาก่อน P3)
      หมายเหตุ: เมนู [?] ท้ายรายงานเป็นแค่ข้อความที่พิมพ์ออกมาเฉยๆ ไม่ได้ใช้ input() รอค่าจริง (หลักการเดียว
      กับ list-preview ของ Skill 09/10 — Claude ต้อง paste รายงานนี้ให้ผู้ใช้ดูแล้วถามผ่านเครื่องมือถาม
      คำถามจริงแทน)

  apply --cases-json <path> --close-status "<ชื่อ Status ที่จะใช้ตอนปิด เช่น Closed>"
        --syntax markdown|textile --out <result.json> [--only "TC-017,TC-009,..."]
      ทำงานจริงกับทุกเคสใน cases-json (หรือเฉพาะที่ระบุใน --only): อัปโหลดไฟล์ Screenshot ขึ้น Redmine ก่อน
      (ถ้าไฟล์มีอยู่จริง — ถ้าไม่เจอไฟล์จะยังคอมเมนต์ต่อได้แต่ไม่มีรูปแนบ ไม่ทำให้ทั้งเคส fail) แล้ว PUT
      คอมเมนต์ (Format ที่ยืนยันแล้ว — ดู mockup-retest-closure-format.md) เข้า Ticket พร้อมไฟล์แนบ:
        - **retest_result = "Pass"**: คอมเมนต์ Format Pass + ตั้ง status_id เป็น --close-status (ปิด Ticket)
        - **retest_result = "Fail"**: คอมเมนต์ Format Fail เท่านั้น **ไม่แตะ Status เลย** (Ticket ยังเปิดอยู่
          รอ Dev แก้ต่อ) — ผลลัพธ์เคสนี้เก็บไว้ในคีย์ `commented` เพื่อให้ SKILL.md เอาไปสร้างอีเมลแจ้ง Dev
          ต่อด้วย scripts/send_email_notification.py คำสั่ง build-retest-failed-body

cases-json schema (list ของ Test Case ที่ผ่านการ Retest จาก Skill 10 มาแล้ว และยังไม่ถูกปิด/Comment):
[
  {
    "tc_id": "TC-017",
    "issue_id": 1024,                          # หรือใช้ "issue_url" แทนก็ได้ (ดึงเลขจาก .../issues/<เลข>)
    "module": "ตะกร้าสินค้า - โค้ดส่วนลด",
    "title": "ลบโค้ด A แล้วใส่โค้ด B ต่อทันที...", # Test Scenario ล้วนๆ เหมือนที่ใช้ใน Skill 09
    "retest_result": "Pass",                    # "Pass" หรือ "Fail" เท่านั้น — ต้องเป็นค่า Status ที่รวมผล
                                                  # ข้าม Browser แล้วตามกฎของ qa-automation-script (06a)
                                                  # ขั้นตอนที่ 5 ข้อ 2 (Fail ถ้ามีอย่างน้อย 1 Browser ยัง Fail)
    "actual_result": "...",                      # ค่า Actual Result ปัจจุบันเต็มๆ จาก Workbook — ใช้แสดงใน
                                                  # list-preview เท่านั้น เพื่อให้ผู้ใช้เห็นว่าผลนี้ "สด" จาก
                                                  # การ Retest จริงหรือเป็นผลเก่าที่ยังไม่เคย Retest เลย (ดู
                                                  # หมายเหตุเรื่อง Scope ใน SKILL.md ขั้นตอนที่ 1 ข้อ 3)
    "reason_if_fail": "...",                     # จำเป็นเฉพาะตอน retest_result = "Fail" — สรุปสาเหตุที่ยัง
                                                  # ไม่ผ่านจาก Actual Result ล่าสุด (AI สรุปเอง เหมือน remark
                                                  # ของ Skill 09 — ถ้า Actual Result ระบุชื่อ Browser กำกับไว้
                                                  # ตามกฎ 06a ให้คงชื่อ Browser ไว้ในสรุปนี้ด้วย) ใช้ทั้งใน
                                                  # Comment และอีเมลแจ้ง Dev ซ้ำ
    "retest_date": "05 Sep 2026",
    "priority": "P2",                            # ใช้แค่ตอนเรียงลำดับ preview/อีเมล ไม่ได้ส่งเข้า Redmine
    "screenshot_path": "screenshots/Chromium/TC-017.png"  # path ไฟล์จริงในเครื่อง จะถูกอัปโหลดเป็น attachment
  }, ...
]

ผลลัพธ์ (--out และพิมพ์ stdout ด้วย):
{
  "closed":    [{"tc_id": ..., "issue_id": ..., "url": ...}],              # Pass — คอมเมนต์ + ปิดสำเร็จ
  "commented": [{"tc_id": ..., "issue_id": ..., "url": ...}],              # Fail — คอมเมนต์สำเร็จ ไม่ปิด
  "failed":    [{"tc_id": ..., "error": "..."}]                           # ทำไม่สำเร็จ (ไม่มี API Key ปน)
}
(ไฟล์ --out นี้เอาไปใช้ต่อกับ scripts/send_email_notification.py คำสั่ง build-retest-failed-body ได้เลย
เพื่อสร้างอีเมลแจ้ง Dev สำหรับทุกเคสในคีย์ `commented` — ดูขั้นตอนที่ 4 ของ SKILL.md)

หมายเหตุเรื่อง Attachment: ใช้ Redmine Attachments API มาตรฐาน 2 ขั้นตอน (1) POST /uploads.json พร้อม raw
binary ของไฟล์ ได้ token กลับมา (2) ส่ง token นั้นไปพร้อมกับ PUT /issues/{id}.json ในฟิลด์ "uploads" ของ
เคสนั้น — เป็นของใหม่ที่เขียนเพิ่มสำหรับ Skill นี้โดยเฉพาะ (create_redmine_issues.py ของ Skill 09 ไม่เคย
แนบไฟล์จริง แค่ใส่ path เป็นข้อความในหัวข้อ "หลักฐาน" ของ description เท่านั้น — จุดนี้เคยเข้าใจผิดระหว่าง
คุยออกแบบ Skill นี้ ต้องแก้ความเข้าใจให้ตรงก่อนใช้งานจริง) ยังไม่เคยทดสอบกับ Redmine จริงเพราะ environment
พัฒนา Skill นี้ต่อ HTTPS ออกไปยังโดเมนนอก allowlist ไม่ได้ (ปัญหาเดียวกับที่เจอตอนพัฒนา Skill 09) — โค้ด
เขียนตาม Redmine REST API ที่มีเอกสารทางการรองรับ แต่ผู้ใช้ควรทดสอบกับ Ticket ทดสอบ 1 ใบก่อนใช้งานจริงเต็มรูปแบบ
"""
import argparse
import json
import mimetypes
import os
import re
import sys

import requests

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def _priority_rank(priority):
    return PRIORITY_ORDER.get(str(priority).strip().upper(), 99)


def _headers_json(api_key):
    return {"X-Redmine-API-Key": api_key, "Content-Type": "application/json"}


def _headers_binary(api_key):
    return {"X-Redmine-API-Key": api_key, "Content-Type": "application/octet-stream"}


def _extract_issue_id(item):
    if item.get("issue_id"):
        return str(item["issue_id"])
    url = item.get("issue_url", "")
    m = re.search(r"/issues/(\d+)", url)
    if not m:
        raise ValueError(f"หา issue_id จาก issue_url ไม่ได้: {url!r} — ต้องมีรูปแบบ .../issues/<เลข>")
    return m.group(1)


def _bold(text, syntax):
    return f"*{text}*" if syntax == "textile" else f"**{text}**"


def _filter_only(cases, only):
    if not only:
        return cases
    wanted = {t.strip().upper() for t in only.split(",") if t.strip()}
    have = {c["tc_id"].strip().upper() for c in cases}
    missing = wanted - have
    if missing:
        sys.exit(f"ไม่พบ TC-ID ต่อไปนี้ใน cases-json: {sorted(missing)} — เช็คว่าพิมพ์ถูกหรือยัง")
    return [c for c in cases if c["tc_id"].strip().upper() in wanted]


def build_comment_pass(case, syntax):
    b = lambda t: _bold(t, syntax)
    lines = [
        "✅ Retest → Pass",
        "",
        f"เรื่องที่แก้ไข: {case['tc_id']} — {case.get('title', '-')}",
        "",
        f"{b('ผลการ Retest:')} Pass — พฤติกรรมของระบบตรงตาม Expected Result แล้ว",
        f"{b('วันที่ Retest:')} {case.get('retest_date', '-')}",
        f"{b('ผู้ทดสอบ/ระบบ:')} QA Automation Assistant",
        "",
        "📎 แนบไฟล์ภาพผลการ Retest (Pass) ประกอบคอมเมนต์นี้",
    ]
    return "\n".join(lines)


def build_comment_fail(case, syntax):
    b = lambda t: _bold(t, syntax)
    lines = [
        "❌ Retest → Fail",
        "",
        f"เรื่องที่ Retest: {case['tc_id']} — {case.get('title', '-')}",
        "",
        f"{b('ผลการ Retest:')} Fail — ยังพบปัญหาอยู่ ไม่ตรงตาม Expected Result",
        f"{b('สาเหตุที่ไม่ผ่าน:')} {case.get('reason_if_fail', '-')}",
        f"{b('วันที่ Retest:')} {case.get('retest_date', '-')}",
        f"{b('ผู้ทดสอบ/ระบบ:')} QA Automation Assistant",
        "",
        "📎 แนบไฟล์ภาพผลการ Retest (Fail) ประกอบคอมเมนต์นี้",
    ]
    return "\n".join(lines)


def cmd_list_statuses(args):
    base_url = os.environ.get("REDMINE_URL", "").strip()
    api_key = os.environ.get("REDMINE_API_KEY", "").strip()
    if not base_url or not api_key:
        sys.exit(
            "ต้องตั้งค่า environment variable REDMINE_URL และ REDMINE_API_KEY ก่อนเรียกคำสั่งนี้เสมอ "
            "(ห้ามส่งผ่าน --argument โดยตรง)"
        )
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/issue_statuses.json", headers=_headers_json(api_key), timeout=20)
    except requests.exceptions.RequestException as e:
        sys.exit(f"เชื่อมต่อ Redmine ไม่สำเร็จ: {type(e).__name__}: {e}")
    if resp.status_code != 200:
        sys.exit(f"HTTP {resp.status_code}: {resp.text[:300]}")
    statuses = [s["name"] for s in resp.json().get("issue_statuses", [])]
    print(json.dumps({"statuses": statuses}, ensure_ascii=False, indent=2))


def _print_list_preview(cases):
    passed = sorted([c for c in cases if c.get("retest_result") == "Pass"], key=lambda c: _priority_rank(c.get("priority")))
    failed = sorted([c for c in cases if c.get("retest_result") == "Fail"], key=lambda c: _priority_rank(c.get("priority")))
    unknown = [c for c in cases if c.get("retest_result") not in ("Pass", "Fail")]

    bar = "=" * 70
    thin = "-" * 70
    lines = [bar, "🔁 SKILL 10a: RETEST CLOSURE PREVIEW (Recheck ก่อนคอมเมนต์/ปิด Ticket จริง)", bar]
    lines.append(f"✅ Retest ผ่านแล้ว (จะคอมเมนต์ Verified + ปิด Ticket): {len(passed)} เคส")
    lines.append(f"❌ Retest ยังไม่ผ่าน (จะคอมเมนต์ + ส่งอีเมลแจ้ง Dev ซ้ำ ไม่ปิด Ticket): {len(failed)} เคส")
    if unknown:
        lines.append(f"⚠ retest_result ไม่ใช่ Pass/Fail (ข้ามไปก่อน ต้องแก้ cases-json): {len(unknown)} เคส")
    lines.append(thin)

    for c in passed:
        lines.append(f"[✅ PASS] {c['tc_id']} · {c.get('title', '-')} (Priority: {c.get('priority', '-')})")
        lines.append(f"          Actual Result: {c.get('actual_result', '-')}")
    if passed and failed:
        lines.append(thin)
    for c in failed:
        lines.append(f"[❌ FAIL] {c['tc_id']} · {c.get('title', '-')} (Priority: {c.get('priority', '-')})")
        lines.append(f"          Actual Result: {c.get('actual_result', '-')}")
        lines.append(f"          สาเหตุที่ไม่ผ่าน: {c.get('reason_if_fail', '-')}")
    lines.append(thin)
    lines.append("⚠ ตรวจ Actual Result ของแต่ละเคสด้านบนก่อนยืนยัน — ถ้าหน้าตาเหมือนผลเดิมตั้งแต่ก่อนเปิด Ticket")
    lines.append("  (ยังไม่เคยผ่าน qa-retest (10) จริง) ให้เลือก Action [2] เพื่อข้ามเคสนั้นออกไปก่อน")

    lines.append("[?] เลือก Action:")
    lines.append(f"  [1] ยืนยันทำทั้งหมด ({len(passed) + len(failed)} เคส)")
    lines.append("  [2] เลือกเฉพาะบางเคส")
    lines.append("  [3] Cancel — ไม่ทำอะไรเลย")
    print("\n".join(lines))


def cmd_list_preview(args):
    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)
    _print_list_preview(cases)


def _upload_screenshot(base_url, api_key, path):
    """อัปโหลดไฟล์ขึ้น Redmine แล้วคืน dict สำหรับใส่ใน 'uploads' ของ issue payload — คืน None ถ้าไฟล์ไม่มี
    จริง (ไม่ throw เพราะไม่อยากให้ทั้งเคส fail แค่เพราะหารูปไม่เจอ — ให้คอมเมนต์ต่อได้โดยไม่มีรูปแนบ)"""
    if not path or not os.path.isfile(path):
        return None, f"ไม่พบไฟล์ Screenshot ที่ path: {path!r} — จะคอมเมนต์ต่อโดยไม่มีรูปแนบ"
    filename = os.path.basename(path)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    resp = requests.post(
        f"{base_url.rstrip('/')}/uploads.json",
        params={"filename": filename},
        headers=_headers_binary(api_key),
        data=data,
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        return None, f"อัปโหลด Screenshot ไม่สำเร็จ HTTP {resp.status_code}: {resp.text[:300]}"
    token = resp.json()["upload"]["token"]
    return {"token": token, "filename": filename, "content_type": content_type}, None


def _resolve_status_id(base_url, api_key, status_name):
    resp = requests.get(f"{base_url.rstrip('/')}/issue_statuses.json", headers=_headers_json(api_key), timeout=20)
    resp.raise_for_status()
    statuses = resp.json().get("issue_statuses", [])
    for s in statuses:
        if s["name"].strip().lower() == status_name.strip().lower():
            return s["id"]
    names = [s["name"] for s in statuses]
    raise ValueError(f'ไม่พบ Status ชื่อ "{status_name}" ใน Redmine instance นี้ — Status ที่มีจริง: {names} (ใช้คำสั่ง list-statuses เพื่อดูรายชื่อที่ถูกต้อง)')


def cmd_apply(args):
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
        close_status_id = _resolve_status_id(base_url, api_key, args.close_status)
    except requests.exceptions.RequestException as e:
        sys.exit(f"เชื่อมต่อ Redmine ไม่สำเร็จตอนค้นหา Status (เช็ค REDMINE_URL / network access ก่อน): {type(e).__name__}: {e}")
    except ValueError as e:
        sys.exit(str(e))

    closed, commented, failed = [], [], []
    for c in cases:
        tc_id = c["tc_id"]
        result = c.get("retest_result")
        if result not in ("Pass", "Fail"):
            failed.append({"tc_id": tc_id, "error": f'retest_result ต้องเป็น "Pass" หรือ "Fail" เท่านั้น ได้ค่า: {result!r}'})
            continue

        try:
            issue_id = _extract_issue_id(c)
        except ValueError as e:
            failed.append({"tc_id": tc_id, "error": str(e)})
            continue

        upload, upload_warning = None, None
        try:
            upload, upload_warning = _upload_screenshot(base_url, api_key, c.get("screenshot_path"))
        except requests.exceptions.RequestException as e:
            upload_warning = f"อัปโหลด Screenshot ไม่สำเร็จ (network): {type(e).__name__}: {e} — จะคอมเมนต์ต่อโดยไม่มีรูปแนบ"

        payload = {
            "issue": {
                "notes": build_comment_pass(c, args.syntax) if result == "Pass" else build_comment_fail(c, args.syntax),
            }
        }
        if upload:
            payload["issue"]["uploads"] = [upload]
        if result == "Pass":
            payload["issue"]["status_id"] = close_status_id

        try:
            resp = requests.put(
                f"{base_url.rstrip('/')}/issues/{issue_id}.json",
                headers=_headers_json(api_key), json=payload, timeout=30,
            )
        except requests.exceptions.RequestException as e:
            failed.append({"tc_id": tc_id, "error": f"เชื่อมต่อ Redmine ไม่สำเร็จ: {type(e).__name__}: {e}"})
            continue

        if resp.status_code not in (200, 204):
            failed.append({"tc_id": tc_id, "error": f"HTTP {resp.status_code}: {resp.text[:500]}"})
            continue

        url = f"{base_url.rstrip('/')}/issues/{issue_id}"
        entry = {"tc_id": tc_id, "issue_id": issue_id, "url": url}
        if upload_warning:
            entry["warning"] = upload_warning
        if result == "Pass":
            closed.append(entry)
        else:
            commented.append(entry)

    result_out = {"closed": closed, "commented": commented, "failed": failed}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result_out, f, ensure_ascii=False, indent=2)
    print(json.dumps(result_out, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-statuses")

    lp = sub.add_parser("list-preview")
    lp.add_argument("--cases-json", required=True)

    ap = sub.add_parser("apply")
    ap.add_argument("--cases-json", required=True)
    ap.add_argument("--close-status", required=True, help='ชื่อ Status ที่จะใช้ตอนปิด Ticket เช่น "Closed" (ใช้เฉพาะเคส Pass)')
    ap.add_argument("--syntax", required=True, choices=["markdown", "textile"], help="รูปแบบตัวหนาที่ Redmine instance นี้ใช้")
    ap.add_argument("--only", default=None, help="comma-separated TC-ID เฉพาะที่จะทำ (ไม่ใส่ = ทุกเคสใน cases-json)")
    ap.add_argument("--out", required=True)

    args = p.parse_args()
    if args.cmd == "list-statuses":
        cmd_list_statuses(args)
    elif args.cmd == "list-preview":
        cmd_list_preview(args)
    elif args.cmd == "apply":
        cmd_apply(args)


if __name__ == "__main__":
    main()
