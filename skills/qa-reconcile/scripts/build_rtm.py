#!/usr/bin/env python3
"""
build_rtm.py — สคริปต์สร้างไฟล์ Requirement Traceability Matrix (RTM) จริง สำหรับ RTM (qa-reconcile)

สคริปต์นี้ทำหน้าที่ "render" เท่านั้น — การคำนวณ Traceability ใหม่และหาจุด Orphan/Gap
เป็นวิจารณญาณของผู้ที่รัน Skill (Claude/Gemini) ตามขั้นตอนที่ 3 ใน SKILL.md ไม่ใช่ logic ในสคริปต์นี้

คำสั่ง:
  build --data <rtm.json> --out <RTM-traceability-matrix.xlsx>

data schema:
{
  "feature": str,
  "rtm_rows": [
    {
      "req_id": str, "description": str, "test_case_ids": [str],
      "statuses": {tc_id: status}, "priorities": {tc_id: priority},
      "traceability_status": "Linked" | "Orphan Requirement" | "Linked - มี Assumption ค้าง"
    }, ...
  ],
  "findings": [
    {"finding_type": str, "detail": str, "decision": str, "reason": str, "date": str}, ...
  ]
}

หมายเหตุการฟอร์แมต (คงรูปแบบนี้ไว้เสมอ — ยืนยันแล้วผ่าน Mockup):
  - ทุกช่องเปิด wrap_text + border บาง ๆ, ความสูงแถวคำนวณอัตโนมัติจากความยาวเนื้อหาจริงด้วย
    _est_lines() สูตรเดียวกับที่ใช้ใน qa_workbook.py (master script ของ Skill 03/04/05/06a)
    ที่ผ่านการปรับจูนกับข้อความภาษาไทยจริงมาแล้ว — ห้ามลด chars_per_line multiplier (1.3) หรือ
    ตัด +1 headroom line ออก เพราะจะทำให้ข้อความยาวถูกตัดตอนเปิดใน Excel จริง (ต่างจาก LibreOffice
    PDF export ที่คำนวณความสูงให้เองเสมอ ทำให้บั๊กนี้มองไม่เห็นตอนตรวจผ่าน PDF)
  - ทั้ง 2 ชีต (RTM, Findings) ตั้งเป็น Landscape + fitToWidth=1 ตอนพิมพ์ เพื่อไม่ให้คอลัมน์ขวาสุด
    หลุดหน้ากระดาษ, Freeze แถวหัวตาราง, เปิด AutoFilter
  - สีพื้นหลังของสถานะ Traceability (เขียว/เหลือง/แดง) ยังคงไว้ตามเดิม
"""
import argparse
import json
import math

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)
THIN_SIDE = Side(style="thin", color="B7B7B7")
THIN_BORDER = Border(top=THIN_SIDE, bottom=THIN_SIDE, left=THIN_SIDE, right=THIN_SIDE)

TRACE_COLORS = {
    "Linked": "C6EFCE",
    "Orphan Requirement": "FFC7CE",
    "Linked - มี Assumption ค้าง": "FFEB9C",
}

LINE_HEIGHT_PT = 16
ROW_PADDING_PT = 6
MAX_ROW_HEIGHT_PT = 260
MIN_ROW_HEIGHT_PT = 20


def _style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[row].height = 26


def _est_lines(text, col_width):
    """ประมาณจำนวนบรรทัดที่ข้อความจะ wrap ใน column ความกว้าง col_width — สูตรเดียวกับ
    _est_lines ใน qa_workbook.py ตั้งใจประมาณแบบอนุรักษ์นิยม (เผื่อบรรทัดเกินดีกว่าขาด)"""
    if text in (None, ""):
        return 1
    text = str(text)
    chars_per_line = max(6, int(col_width * 1.3))
    total_lines = 0
    for segment in text.split("\n"):
        total_lines += max(1, math.ceil(len(segment) / chars_per_line))
    return total_lines + 1  # +1 บรรทัดเผื่อ headroom


def _apply_page_setup(ws):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)


def build_rtm(data, out_path):
    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "RTM"
    headers = ["Requirement / Flow ID", "รายละเอียด", "Test Case ID ที่ครอบคลุม",
               "Status ของแต่ละ Test Case", "Priority", "สถานะ Traceability"]
    ws.append(headers)
    widths = [16, 48, 24, 34, 10, 24]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    _style_header(ws, 1, len(headers))

    for row in data["rtm_rows"]:
        tc_ids = row.get("test_case_ids", [])
        statuses = row.get("statuses", {})
        priorities = row.get("priorities", {})
        tc_str = ", ".join(tc_ids) if tc_ids else "(ไม่มี)"
        status_str = ", ".join(f"{tc}={statuses.get(tc, '?')}" for tc in tc_ids) if tc_ids else "-"
        prio_str = ", ".join(sorted(set(priorities.get(tc, "?") for tc in tc_ids))) if tc_ids else "-"

        r = ws.max_row + 1
        values = [row["req_id"], row["description"], tc_str, status_str, prio_str, row["traceability_status"]]
        for c, val in enumerate(values, start=1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        ws.cell(row=r, column=5).alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        trace_cell = ws.cell(row=r, column=6)
        trace_cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        color = TRACE_COLORS.get(row["traceability_status"])
        if color:
            trace_cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

        max_lines = max(_est_lines(v, widths[i]) for i, v in enumerate(values))
        ws.row_dimensions[r].height = min(
            MAX_ROW_HEIGHT_PT, max(MIN_ROW_HEIGHT_PT, max_lines * LINE_HEIGHT_PT + ROW_PADDING_PT)
        )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws.max_row}"
    _apply_page_setup(ws)

    ws2 = wb.create_sheet("Findings")
    f_headers = ["Finding Type", "รายละเอียด", "การตัดสินใจ", "เหตุผล", "วันที่"]
    ws2.append(f_headers)
    f_widths = [22, 55, 22, 40, 13]
    for i, w in enumerate(f_widths, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    _style_header(ws2, 1, len(f_headers))

    for f in data.get("findings", []):
        r = ws2.max_row + 1
        values = [f.get("finding_type", ""), f.get("detail", ""), f.get("decision", ""),
                  f.get("reason", ""), f.get("date", "")]
        for c, val in enumerate(values, start=1):
            cell = ws2.cell(row=r, column=c, value=val)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        max_lines = max(_est_lines(v, f_widths[i]) for i, v in enumerate(values))
        ws2.row_dimensions[r].height = min(
            MAX_ROW_HEIGHT_PT, max(MIN_ROW_HEIGHT_PT, max_lines * LINE_HEIGHT_PT + ROW_PADDING_PT)
        )

    ws2.freeze_panes = "A2"
    ws2.auto_filter.ref = f"A1:{get_column_letter(len(f_headers))}{ws2.max_row}"
    _apply_page_setup(ws2)

    wb.save(out_path)
    return out_path


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    p_build = sub.add_parser("build")
    p_build.add_argument("--data", required=True)
    p_build.add_argument("--out", required=True)
    args = p.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    out = build_rtm(data, args.out)
    print(json.dumps({"written": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
