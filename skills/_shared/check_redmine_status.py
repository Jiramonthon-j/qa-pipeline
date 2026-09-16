#!/usr/bin/env python3
"""
check_redmine_status.py — เช็ค Status + อ่าน Comment (journal) ของ Ticket ที่เคยเปิดโดย redmine-logging
(Skill 09) สำหรับ Skill 10 (qa-retest) ใช้ตัดสินว่า Ticket ไหน Dev แก้เสร็จแล้วพร้อม Retest

**ไฟล์นี้เป็น single source of truth ที่ใช้ร่วมกัน 2 Skill**: qa-retest (10) เรียกผ่าน stub ของตัวเอง
เพื่อเช็คว่า Ticket ไหน Dev แจ้งแก้เสร็จแล้ว (`--resolved-statuses` = ชื่อ Status ที่แปลว่า "แก้เสร็จแล้ว")
และ qa-retest-closure (10a) เรียกผ่าน stub ของตัวเองเพื่อกรอง Ticket ที่ปิดไปแล้วออกจาก Scope ก่อนแสดง
Preview (`--resolved-statuses` = ชื่อ Status ที่แปลว่า "ปิดแล้ว") — พฤติกรรมเหมือนกันทุกประการ ต่างกันแค่
ค่าที่ผู้เรียกส่งเข้ามา **ถ้าต้องแก้ logic ให้แก้ที่ไฟล์นี้ที่เดียว ห้ามแก้ตาม stub ของแต่ละ Skill**

**คำเตือนความปลอดภัยที่สำคัญที่สุด**: ห้าม log/print ค่า REDMINE_API_KEY แบบเต็มออกทาง stdout/stderr
หรือเขียนลงไฟล์ใดๆ เด็ดขาด (เหตุผลเดียวกับ create_redmine_issues.py ของ Skill 09) — สคริปต์นี้รับ
URL/API Key ผ่าน environment variable เท่านั้น (REDMINE_URL, REDMINE_API_KEY) ไม่รับผ่าน --argument
โดยตรง

คำสั่ง:
  check --tc-issue-map <path.json> --resolved-statuses "Resolved,Fixed" --out <result.json>
      สำหรับแต่ละรายการใน tc-issue-map ยิง GET {REDMINE_URL}/issues/{issue_id}.json?include=journals
      อ่าน Status ปัจจุบันของ Ticket + Comment (journal notes) ทั้งหมด แล้วแยกเป็น 3 กลุ่ม:
        - "ready": Status ปัจจุบันตรงกับหนึ่งใน --resolved-statuses (case-insensitive) — พร้อม Retest
        - "waiting": Status ยังไม่ตรง (Dev ยังไม่แจ้งว่าแก้เสร็จ) — ข้ามไปก่อน ไม่ใช่ error
        - "failed": ดึงข้อมูล Ticket ไม่สำเร็จ (network/permission/ticket ไม่มีอยู่จริง ฯลฯ)
      อ่าน REDMINE_URL/REDMINE_API_KEY จาก environment variable เท่านั้น ถ้าไม่มีค่าจะหยุดทำงานทันที

tc-issue-map schema (list):
[
  {"tc_id": "TC-017", "issue_url": "https://redmine.example.com/issues/1024"},
  ...
]
(รับ "issue_url" หรือ "issue_id" ก็ได้อย่างใดอย่างหนึ่ง — ถ้ามีทั้งคู่ใช้ issue_id ก่อน)

ผลลัพธ์ (--out และพิมพ์ stdout ด้วย):
{
  "ready": [
    {"tc_id": ..., "issue_id": ..., "status": "Resolved",
     "comments": [{"author": "...", "created_on": "...", "notes": "..."}]}
  ],
  "waiting": [{"tc_id": ..., "issue_id": ..., "status": "In Progress"}],
  "failed": [{"tc_id": ..., "issue_id": ..., "error": "..."}]
}
"""
import argparse
import json
import os
import re
import sys

import requests


def _headers(api_key):
    return {"X-Redmine-API-Key": api_key}


def _extract_issue_id(item):
    if item.get("issue_id"):
        return str(item["issue_id"])
    url = item.get("issue_url", "")
    m = re.search(r"/issues/(\d+)", url)
    if not m:
        raise ValueError(f"หา issue_id จาก issue_url ไม่ได้: {url!r} — ต้องมีรูปแบบ .../issues/<เลข>")
    return m.group(1)


def cmd_check(args):
    base_url = os.environ.get("REDMINE_URL", "").strip()
    api_key = os.environ.get("REDMINE_API_KEY", "").strip()
    if not base_url or not api_key:
        sys.exit(
            "ต้องตั้งค่า environment variable REDMINE_URL และ REDMINE_API_KEY ก่อนเรียกคำสั่งนี้เสมอ "
            "(ห้ามส่งผ่าน --argument โดยตรงเพราะจะโผล่ใน shell history/process list) — ไม่มีค่า default "
            "ให้ fallback ไปที่ไหนทั้งสิ้น"
        )

    resolved_statuses = {s.strip().lower() for s in args.resolved_statuses.split(",") if s.strip()}
    if not resolved_statuses:
        sys.exit("--resolved-statuses ต้องมีอย่างน้อย 1 ค่า เช่น \"Resolved,Fixed\"")

    with open(args.tc_issue_map, encoding="utf-8") as f:
        items = json.load(f)

    ready, waiting, failed = [], [], []
    for item in items:
        tc_id = item["tc_id"]
        try:
            issue_id = _extract_issue_id(item)
        except ValueError as e:
            failed.append({"tc_id": tc_id, "issue_id": None, "error": str(e)})
            continue

        try:
            resp = requests.get(
                f"{base_url.rstrip('/')}/issues/{issue_id}.json",
                params={"include": "journals"},
                headers=_headers(api_key),
                timeout=20,
            )
        except requests.exceptions.RequestException as e:
            failed.append({"tc_id": tc_id, "issue_id": issue_id, "error": f"เชื่อมต่อ Redmine ไม่สำเร็จ: {type(e).__name__}: {e}"})
            continue

        if resp.status_code != 200:
            failed.append({"tc_id": tc_id, "issue_id": issue_id, "error": f"HTTP {resp.status_code}: {resp.text[:300]}"})
            continue

        issue = resp.json().get("issue", {})
        status_name = issue.get("status", {}).get("name", "")
        journals = issue.get("journals", [])
        comments = [
            {
                "author": j.get("user", {}).get("name", "-"),
                "created_on": j.get("created_on", "-"),
                "notes": j.get("notes", ""),
            }
            for j in journals
            if (j.get("notes") or "").strip()  # journal บาง entry เป็นแค่ log การเปลี่ยน field ไม่มี comment จริง
        ]

        entry = {"tc_id": tc_id, "issue_id": issue_id, "status": status_name}
        if status_name.strip().lower() in resolved_statuses:
            entry["comments"] = comments
            ready.append(entry)
        else:
            waiting.append(entry)

    result = {"ready": ready, "waiting": waiting, "failed": failed}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    ck = sub.add_parser("check")
    ck.add_argument("--tc-issue-map", required=True)
    ck.add_argument("--resolved-statuses", required=True)
    ck.add_argument("--out", required=True)

    args = p.parse_args()
    if args.cmd == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
