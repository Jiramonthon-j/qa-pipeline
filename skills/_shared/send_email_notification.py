#!/usr/bin/env python3
"""
send_email_notification.py — แจ้งเตือน Developer ทาง Email หลังเปิด Ticket ใน Redmine สำเร็จ (ขั้นตอนที่ 6
ของ Skill 09 redmine-logging) เป็นสคริปต์แยกจาก create_redmine_issues.py เพราะเป็นระบบภายนอกคนละตัว
(SMTP mail server ไม่ใช่ Redmine) ต้องใช้ credential คนละชุด

**ไฟล์นี้เป็น single source of truth ที่ใช้ร่วมกัน 2 Skill**: redmine-logging (09) เรียกผ่าน stub ของตัวเอง
ใช้คำสั่ง `build-body` (Format "DEFECT SUMMARY REPORT" ตอนเปิดบั๊กใหม่) และ qa-retest-closure (10a) เรียก
ผ่าน stub ของตัวเองใช้คำสั่ง `build-retest-failed-body` (Format "RETEST FAILED REPORT" ตอน Retest แล้วยังไม่
ผ่าน — คนละ Format กับ `build-body` เพราะบริบทต่างกัน) ส่วนคำสั่ง `print-success`/`send` ใช้ร่วมกันได้ตรงๆ
ไม่ต้องแยก **ถ้าต้องแก้ logic ให้แก้ที่ไฟล์นี้ที่เดียว ห้ามแก้ตาม stub ของแต่ละ Skill**

**คำเตือนความปลอดภัยที่สำคัญที่สุด**: ห้าม log/print ค่า SMTP_PASSWORD แบบเต็มออกทาง stdout/stderr หรือ
เขียนลงไฟล์ใดๆ เด็ดขาด (เหตุผลเดียวกับ REDMINE_API_KEY ใน create_redmine_issues.py) — สคริปต์นี้รับค่า SMTP
ผ่าน environment variable เท่านั้น (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM ไม่บังคับ)
ไม่รับผ่าน --argument โดยตรง

**ข้อจำกัดสำคัญที่ต้องรู้ก่อนใช้งาน (พบระหว่างพัฒนา Skill นี้)**: environment ที่ใช้พัฒนา/ทดสอบ Skill นี้
(cloud sandbox) **ต่อ SMTP (raw TCP) ออกอินเทอร์เน็ตไม่ได้เลย** — ทดสอบแล้วพบว่า timeout ทุกครั้งไม่ว่า
credential จะถูกหรือผิด เพราะ network egress ของ environment นั้นอนุญาตเฉพาะ HTTP/HTTPS ผ่าน proxy ไปยัง
โดเมนที่อยู่ใน allowlist เท่านั้น ส่วน SMTP เป็น protocol แบบอื่นที่ไม่ผ่าน proxy นี้เลยจึงไม่มีทางออก
**ถ้ารันคำสั่ง send ในสคริปต์นี้แล้วเจอ error แบบ timeout/connection refused ให้สงสัยไว้ก่อนว่าอาจเป็นเพราะ
environment ที่รัน Skill นี้ไม่อนุญาต raw TCP egress ไปยัง SMTP server ไม่ใช่ credential ผิดหรือ SMTP server
มีปัญหา** (ปัญหาประเภทเดียวกับที่เจอกับ Redmine ตอนพัฒนา Skill 09 แต่หนักกว่าเพราะ SMTP ไม่ผ่าน proxy เลยแม้แต่
น้อย ไม่ได้แค่ถูก proxy ปฏิเสธเป็น 403 เหมือน Redmine)

คำสั่ง:
  print-success --result-json <result.json จาก create_redmine_issues.py create --out>
      พิมพ์รายงานสรุปความสำเร็จแบบอ่านง่าย (banner ✅ SUCCESS + รายการ Ticket ที่เปิดสำเร็จ) ให้ผู้ใช้ดู
      ก่อนถามว่าจะส่งอีเมลแจ้งเตือนต่อไหม — ไม่ต้องมี credential เลย อ่านจากไฟล์ผลลัพธ์ที่มีอยู่แล้วเฉยๆ

  build-body --cases-json <path เดียวกับที่ใช้กับ create> --result-json <result.json>
             --run-date "<เช่น 01 Sep 2026>" --environment "<เช่น Staging (mock) — ทดสอบผ่าน Chromium>"
             --out <body.txt>
      ประกอบเนื้อหาอีเมล (Format ที่ยืนยันแล้วกับผู้ใช้ — ดู mockup-email-format.md) จาก field
      module/title/remark/steps ใน cases-json + issue_id/url/priority ใน result.json (จับคู่กันด้วย
      tc_id) เรียงบั๊กตาม Priority ก่อนเสมอ (เหมือน list-preview) แปลง Priority → คำ Severity ด้วย mapping
      คงที่ P0=Critical/P1=High/P2=Medium/P3=Low (ยืนยันกับผู้ใช้แล้ว) เขียนผลลงไฟล์ --out และพิมพ์ออก
      stdout ด้วยเพื่อให้ตรวจสอบก่อนส่งจริงได้ **หมายเหตุ**: Format ต้นฉบับที่ผู้ใช้ให้มามีทั้ง "Description"
      และ "Remark" แยกกัน 2 บรรทัดต่อบั๊ก แต่ cases-json ของ Pipeline นี้มีแค่ field เดียว (`remark` = summary
      บรรทัดเดียวจาก Actual Result) จึงรวมเป็นบรรทัด "Description" บรรทัดเดียว ไม่ได้แยก 2 บรรทัดตามต้นฉบับ
      เป๊ะๆ — ถ้าต้องการแยกจริงต้องเพิ่ม field ใหม่ใน cases-json ภายหลัง (ยังไม่ได้ทำเพราะไม่มีข้อมูลต้นทาง
      ที่ต่างจาก remark ให้ใช้)

  build-retest-failed-body --cases-json <path> --result-json <result.json จาก close_redmine_issues.py apply>
             --run-date "<วันที่ Retest>" --environment "<Environment>" --out <body.txt>
      ประกอบเนื้อหาอีเมล **"RETEST FAILED REPORT"** (Format ที่ยืนยันแล้ว — คนละ Format กับ `build-body`)
      ใช้แจ้ง Dev ว่า Retest แล้วบางเคสยังไม่ผ่าน ไม่ใช่แจ้งเปิดบั๊กใหม่ ดึง field module/title/priority/
      reason_if_fail จาก cases-json จับคู่กับ issue_id/url ใน result-json (คีย์ `commented`) ด้วย tc_id
      เรียงตาม Priority ก่อนเสมอ (เหมือน `build-body`) **ไม่มีหัวข้อ Description/Steps to Reproduce**
      (Dev เห็น Ticket เดิมอยู่แล้ว) มีแค่ "สาเหตุที่ไม่ผ่าน" (ค่าเดียวกับที่คอมเมนต์กลับ Ticket ไปแล้ว) และ
      อ้างอิงกลับไปดูรูปที่ Comment ล่าสุดของ Ticket แทนการแนบรูปซ้ำในอีเมล (ยืนยันกับผู้ใช้แล้วว่าไม่ต้อง
      แนบรูปซ้ำเพราะรูปถูกแนบเข้า Comment ของ Redmine ไปแล้วจาก close_redmine_issues.py)

  send --to <developer email> --subject <หัวข้ออีเมล> --body-file <path ไฟล์เนื้อหาอีเมล เตรียมมาให้พร้อมใช้>
      ส่งอีเมลจริงผ่าน SMTP อ่าน SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD จาก environment variable
      เท่านั้น (SMTP_FROM ไม่บังคับ — ไม่ใส่จะใช้ SMTP_USERNAME แทน) ใช้ STARTTLS เสมอยกเว้น port 465 (ใช้
      SSL ตั้งแต่ต้นการเชื่อมต่อ) ถ้าขาด environment variable ที่จำเป็นจะหยุดทำงานทันทีไม่เดา/ไม่ fallback
      ใช้ร่วมกันได้ทั้ง Skill 09 (build-body) และ Skill 10a (build-retest-failed-body) ไม่ต้องแยกคำสั่ง
"""
import argparse
import json
import os
import smtplib
import socket
import sys
from email.message import EmailMessage

REQUIRED_ENV = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
PRIORITY_TO_SEVERITY = {"P0": "Critical", "P1": "High", "P2": "Medium", "P3": "Low"}


def _priority_rank(priority):
    return PRIORITY_ORDER.get(str(priority).strip().upper(), 99)


def _severity_word(priority):
    return PRIORITY_TO_SEVERITY.get(str(priority).strip().upper(), "-")


def build_email_body(cases, created, run_date, environment):
    case_by_id = {c["tc_id"]: c for c in cases}
    created_sorted = sorted(created, key=lambda c: _priority_rank(c.get("priority")))
    n = len(created_sorted)

    bar = "=" * 80
    thin = "-" * 80
    lines = [
        "Hi Dev Team,",
        "",
        f"ระบบ QA Automation ได้ทำการทดสอบระบบล่าสุดเสร็จสิ้น และพบ Bug ที่ต้องการการแก้ไขจำนวน {n} รายการ",
        "รายละเอียดและลิงก์สำหรับเข้าดู Ticket ใน Redmine ถูกสรุปไว้ด้านล่างนี้ครับ:",
        "",
        bar,
        "🐞 DEFECT SUMMARY REPORT",
        bar,
        f"Test Run Date: {run_date} | Environment: {environment}",
        thin,
    ]
    for i, c in enumerate(created_sorted, start=1):
        tc_id = c["tc_id"]
        case = case_by_id.get(tc_id, {})
        priority = c.get("priority") or case.get("priority", "")
        title = case.get("title") or c.get("subject", tc_id)
        lines.append(f"{i}. [{priority} - {_severity_word(priority)}] {title}")
        lines.append(thin)
        lines.append(f"• Issue Link : {c.get('url', '-')}")
        lines.append(f"• Module     : {case.get('module', '-')}")
        lines.append(f"• Test Case  : {tc_id}")
        lines.append(f"• Description: {case.get('remark', '-')}")
        steps = case.get("steps") or []
        if steps:
            lines.append("• Steps to Reproduce:")
            for j, s in enumerate(steps, start=1):
                lines.append(f"  {j}. {s}")
        if i < n:
            lines.append(thin)
    lines += [
        bar,
        "📁 Attached Evidence:",
        "- สามารถดู Path ของไฟล์ Screenshot ผลการทดสอบได้ที่หัวข้อ \"หลักฐาน\" ใน Description ของแต่ละ Ticket (อ้างอิง path ในระบบไฟล์ของทีม QA — Skill นี้ยังไม่ได้อัปโหลดไฟล์แนบขึ้น Redmine โดยตรง)",
        "- สามารถคลิกที่ Issue Link ด้านบนเพื่อดูรายละเอียดเพิ่มเติมและอัปเดต Status ได้ทันทีครับ",
        "",
        "Best regards,",
        "QA Automation Assistant",
        thin,
    ]
    return "\n".join(lines)


def build_retest_failed_body(cases, commented, run_date, environment):
    """ประกอบอีเมล "RETEST FAILED REPORT" (Format ยืนยันแล้ว — ดู mockup-retest-closure-format.md)
    ต่างจาก build_email_body ตรงที่: (1) ประโยคเปิดพูดถึง Retest ไม่ใช่บั๊กใหม่ (2) แบนเนอร์คนละชื่อ/อีโมจิ
    (3) ไม่มี Description/Steps to Reproduce — มีแค่ "สาเหตุที่ไม่ผ่าน" (4) อ้างอิงกลับไปดูรูปที่ Comment
    ของ Ticket แทนการแนบรูปซ้ำในอีเมล เพราะรูปถูกแนบเข้า Comment ของ Redmine ไปแล้วจาก close_redmine_issues.py
    """
    case_by_id = {c["tc_id"]: c for c in cases}
    commented_sorted = sorted(commented, key=lambda c: _priority_rank(case_by_id.get(c["tc_id"], {}).get("priority")))
    n = len(commented_sorted)

    bar = "=" * 80
    thin = "-" * 80
    lines = [
        "Hi Dev Team,",
        "",
        f"ระบบ QA Automation ได้ทำการ Retest ตามที่แจ้งว่าแก้ไขแล้วเสร็จสิ้น แต่พบว่ายังมี Defect ที่ยังไม่ผ่านจำนวน {n} รายการ",
        "รายละเอียดและลิงก์สำหรับเข้าดู Ticket ใน Redmine ถูกสรุปไว้ด้านล่างนี้ครับ:",
        "",
        bar,
        "🔁 RETEST FAILED REPORT",
        bar,
        f"Retest Date: {run_date} | Environment: {environment}",
        thin,
    ]
    for i, c in enumerate(commented_sorted, start=1):
        tc_id = c["tc_id"]
        case = case_by_id.get(tc_id, {})
        priority = case.get("priority", "")
        title = case.get("title", tc_id)
        lines.append(f"{i}. [{priority} - {_severity_word(priority)}] {title}")
        lines.append(thin)
        lines.append(f"• Issue Link       : {c.get('url', '-')}")
        lines.append(f"• Module           : {case.get('module', '-')}")
        lines.append(f"• Test Case        : {tc_id}")
        lines.append(f"• สาเหตุที่ไม่ผ่าน : {case.get('reason_if_fail', '-')}")
        lines.append(f"• ดูภาพประกอบเพิ่มเติมได้ที่ Comment ล่าสุดของ Defect#{c.get('issue_id', '-')}")
        if i < n:
            lines.append(thin)
    lines += [
        bar,
        "📁 Attached Evidence:",
        "- ไฟล์ Screenshot ผลการ Retest (Fail) ได้ถูกแนบเข้าไปในคอมเมนต์ล่าสุดของ Ticket แต่ละใบเรียบร้อยแล้ว",
        "- สามารถคลิกที่ Issue Link ด้านบนเพื่อดูรายละเอียดเพิ่มเติมและอัปเดต Status ได้ทันทีครับ",
        "",
        "Best regards,",
        "QA Automation Assistant",
        thin,
    ]
    return "\n".join(lines)


def cmd_build_retest_failed_body(args):
    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)
    with open(args.result_json, encoding="utf-8") as f:
        result = json.load(f)
    commented = result.get("commented", [])
    if not commented:
        sys.exit("result.json ไม่มีรายการ commented เลย — ไม่ควรเรียก build-retest-failed-body ในกรณีนี้")

    body = build_retest_failed_body(cases, commented, args.run_date, args.environment)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(body)
    print(body)


def cmd_build_body(args):
    with open(args.cases_json, encoding="utf-8") as f:
        cases = json.load(f)
    with open(args.result_json, encoding="utf-8") as f:
        result = json.load(f)
    created = result.get("created", [])
    if not created:
        sys.exit("result.json ไม่มีรายการ created เลย — ไม่ควรเรียก build-body ในกรณีนี้ (ดูขั้นตอนที่ 6 ของ SKILL.md)")

    body = build_email_body(cases, created, args.run_date, args.environment)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(body)
    print(body)


def cmd_print_success(args):
    with open(args.result_json, encoding="utf-8") as f:
        result = json.load(f)
    created = result.get("created", [])
    failed = result.get("failed", [])
    skipped = result.get("skipped", [])

    bar = "=" * 70
    lines = [bar]
    if created:
        lines.append(f"✅ SUCCESS: {len(created)} Bugs posted to Redmine successfully!")
        for c in created:
            lines.append(f"   • #{c['issue_id']} - {c.get('subject', c['tc_id'])}")
    else:
        lines.append("⚠ No bugs were posted to Redmine this run.")
    if failed:
        lines.append("")
        lines.append(f"❌ FAILED: {len(failed)} เคสเปิด Ticket ไม่สำเร็จ")
        for fitem in failed:
            lines.append(f"   • {fitem['tc_id']} - {fitem['error']}")
    if skipped:
        lines.append("")
        lines.append(f"⏭ SKIPPED: {len(skipped)} เคส (มี Ticket อยู่แล้ว)")
    lines.append(bar)
    print("\n".join(lines))


def cmd_send(args):
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_port_raw = os.environ.get("SMTP_PORT", "").strip()
    smtp_username = os.environ.get("SMTP_USERNAME", "").strip()
    smtp_password = os.environ.get("SMTP_PASSWORD", "").strip()
    smtp_from = os.environ.get("SMTP_FROM", "").strip() or smtp_username

    missing = [name for name in REQUIRED_ENV if not os.environ.get(name, "").strip()]
    if missing:
        sys.exit(
            f"ต้องตั้งค่า environment variable ต่อไปนี้ก่อนเรียกคำสั่งนี้เสมอ: {', '.join(missing)} "
            "(ห้ามส่งผ่าน --argument โดยตรงเพราะจะโผล่ใน shell history/process list) — ไม่มีค่า default "
            "ให้ fallback ไปที่ไหนทั้งสิ้น"
        )

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        sys.exit(f"SMTP_PORT ต้องเป็นตัวเลข แต่ได้ค่า: {smtp_port_raw!r}")

    with open(args.body_file, encoding="utf-8") as f:
        body = f.read()

    msg = EmailMessage()
    msg["Subject"] = args.subject
    msg["From"] = smtp_from
    msg["To"] = args.to
    msg.set_content(body)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
        with server:
            server.ehlo()
            if smtp_port != 465:
                server.starttls()
                server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
    except (socket.timeout, TimeoutError) as e:
        sys.exit(
            f"เชื่อมต่อ SMTP server ไม่สำเร็จ (timeout): {type(e).__name__}: {e} — ถ้ารัน Skill นี้ใน "
            "environment ที่จำกัด network egress (เช่น cloud sandbox ที่ใช้พัฒนา Skill นี้) SMTP อาจต่อออก "
            "ไม่ได้เลยเพราะเป็น raw TCP ไม่ผ่าน HTTP proxy — ให้สงสัยเรื่อง network ก่อน ไม่ใช่ credential ผิด"
        )
    except smtplib.SMTPAuthenticationError as e:
        sys.exit(f"Login SMTP ไม่สำเร็จ (username/password หรือ App Password ผิด): {e}")
    except (OSError, smtplib.SMTPException) as e:
        sys.exit(
            f"ส่งอีเมลไม่สำเร็จ: {type(e).__name__}: {e} — ถ้าข้อความมีคำว่า refused/unreachable/network "
            "ให้สงสัยเรื่อง network egress ของ environment ก่อนเช่นกัน"
        )

    print(json.dumps({"sent": True, "to": args.to}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("print-success")
    ps.add_argument("--result-json", required=True)

    bb = sub.add_parser("build-body")
    bb.add_argument("--cases-json", required=True)
    bb.add_argument("--result-json", required=True)
    bb.add_argument("--run-date", required=True)
    bb.add_argument("--environment", required=True)
    bb.add_argument("--out", required=True)

    bf = sub.add_parser("build-retest-failed-body")
    bf.add_argument("--cases-json", required=True)
    bf.add_argument("--result-json", required=True)
    bf.add_argument("--run-date", required=True)
    bf.add_argument("--environment", required=True)
    bf.add_argument("--out", required=True)

    sd = sub.add_parser("send")
    sd.add_argument("--to", required=True)
    sd.add_argument("--subject", required=True)
    sd.add_argument("--body-file", required=True)

    args = p.parse_args()
    if args.cmd == "print-success":
        cmd_print_success(args)
    elif args.cmd == "build-body":
        cmd_build_body(args)
    elif args.cmd == "build-retest-failed-body":
        cmd_build_retest_failed_body(args)
    elif args.cmd == "send":
        cmd_send(args)


if __name__ == "__main__":
    main()
