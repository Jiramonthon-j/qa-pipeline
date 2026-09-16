#!/usr/bin/env python3
"""
qa_workbook.py — เครื่องมือกลางสำหรับสร้าง/แก้ไข Test Case Workbook (.xlsx) ของ QA Pipeline
ใช้ร่วมกันโดย Skill: test-case-generator (03), coverage-review (04), risk-analysis (05)
(และในอนาคต qa-automation-script (06a) สำหรับอัปเดตผล Pass/Fail)

วิธีใช้ (command line):
  python3 qa_workbook.py create --feature "<ชื่อ Feature>" --out "<path>.xlsx"
  python3 qa_workbook.py add-cases --path "<path>.xlsx" --cases-json "<path ไปยังไฟล์ .json ที่มี list ของ test case>" --editor "<ชื่อ skill ที่แก้ไข>" --note "<คำอธิบายสั้นๆ>"
  python3 qa_workbook.py bump --path "<path>.xlsx" --editor "<ชื่อ skill>" --note "<คำอธิบายสั้นๆ>"
  python3 qa_workbook.py read-cases --path "<path>.xlsx"   (พิมพ์ JSON ของ Test Case ทั้งหมดออกทาง stdout)
  python3 qa_workbook.py update-field --path "<path>.xlsx" --tc-id "TC-001" --field "Priority" --value "P0" --editor "<ชื่อ skill>" --note "<คำอธิบายสั้นๆ>"
  python3 qa_workbook.py finalize-layout --path "<path>.xlsx"
    (จัดฟอร์แมตทั้ง Workbook ใหม่ทั้งไฟล์ — wrap/border/สี, ความสูงแถวตามเนื้อหาจริง, page setup,
     แปลง ' เดี่ยวในข้อความเป็น " คู่ ฯลฯ — เรียกอัตโนมัติทุกครั้งท้าย add-cases/update-field/
     update-fields-batch อยู่แล้ว แต่ถ้าไปแก้เซลล์เอง (เช่น เติมแถว Requirement Matrix / Env & Config
     ด้วยมือผ่าน openpyxl ตรงๆ ตามขั้นตอนที่ 4 ใน SKILL.md) ให้เรียกคำสั่งนี้เองอีกครั้งท้ายสุดเสมอ)

ทุกคำสั่งที่แก้ไขเนื้อหา (add-cases, bump, update-field) จะ bump Version ใน Document Control
+1 โดยอัตโนมัติ และเพิ่ม 1 บรรทัดใน History ทุกครั้ง (ตามกฎ versioning ของโปรเจค)

หมายเหตุการฟอร์แมต (สรุปจากการไล่แก้ Workbook จริงหลายรอบร่วมกับผู้ใช้ — ทุกจุดด้านล่างนี้ผ่าน
การตรวจสอบใน Excel จริงแล้ว ไม่ใช่แค่ผ่านการ render PDF เท่านั้น เพราะบางบั๊ก เช่น wrap_text ที่ไม่มี
row height กำกับ จะมองไม่เห็นใน PDF/LibreOffice แต่เห็นชัดใน Excel จริง):
  - เซลล์ข้อมูลทุกเซลล์ (ไม่ใช่แค่ header) ต้องมี wrap_text + border + vertical="top" เสมอ ไม่งั้นข้อความ
    ยาวจะ "ตกขอบ" อ่านไม่ออกในคอลัมน์แคบ
  - openpyxl ไม่ set row height ให้อัตโนมัติเวลา set wrap_text=True — ต้องคำนวณและ set .height เองเสมอ
    (ดู _finalize_layout / _est_lines) ไม่งั้น Excel จะโชว์แค่ 1 บรรทัดแล้วตัดข้อความส่วนเกินทิ้งไปเฉยๆ
    ทั้งที่ไฟล์ยังมีข้อความอยู่ครบ (แค่มองไม่เห็น)
  - แถวที่ไม่มีเซลล์ไหนมีข้อมูลเลย (blank spacer row ที่ตั้งใจเว้นไว้เพื่อความสวยงาม) ต้องไม่ใส่กรอบ/wrap
    ให้เลย ไม่งั้นจะกลายเป็นกล่องว่างเปล่าดูเหมือนพลาด
  - แถวที่มีข้อมูลอยู่เซลล์เดียว (lone note/caption แบบ "*ข้อความ*" สีแดง) ต้องไม่ปนกับ logic
    ของแถวข้อมูลปกติ — ดูตัวอย่างที่ _build_dashboard (คงตำแหน่งเดิม มีแถวว่างคั่น) กับ
    _build_requirement_matrix (ย้ายไปข้างขวาบรรทัดเดียวกับข้อมูลแถวแรก ไม่มีแถวว่างคั่น) ซึ่งเป็น 2
    รูปแบบที่ต่างกันตามชนิดชีต: ชีตแบบ "หัวข้อสรุป/dashboard" ใช้แบบแรก ชีตแบบ "ตารางข้อมูล" ใช้แบบหลัง
  - ตัวอักษร ' (single quote) ในข้อความ (ไม่ใช่ syntax อ้างอิงชื่อชีตในสูตร เช่น 'Test Case'!A1) ให้ใช้
    " (double quote) แทนเสมอ เพื่อความสม่ำเสมอ — ดู _normalize_quotes
  - Test Case sheet เท่านั้นที่ fitToHeight=0 (ปล่อยให้พิมพ์ข้ามหลายหน้าได้ตามจริง) เพราะมีคอลัมน์เยอะ
    และแถวมักสูง ถ้าบีบให้พอดี 1 หน้าเหมือนชีตอื่นจะเล็กจนอ่านไม่ออก — ชีตอื่นทั้งหมด fitToHeight=1

คอลัมน์ Test Photo: เขียนค่าผ่าน update-field/update-fields-batch ตามปกติ (value = path ไปยังไฟล์รูป
เช่น "screenshots/Chromium/TC-017.png") แต่แทนที่จะเก็บเป็นข้อความ path เฉยๆ ระบบจะพยายาม "ฝังรูปจริง"
(thumbnail ย่อขนาด) เข้าไปในเซลล์นั้นเลย โดย resolve path เทียบกับโฟลเดอร์ของ Workbook ก่อนแล้วค่อย
fallback ไปเทียบกับ working directory — ถ้าหาไฟล์รูปไม่เจอจะ fallback กลับไปเขียน path เป็นข้อความแทน
เหมือนเดิม (ไม่ให้ข้อมูลหายไปเงียบๆ) path เดิมยังเก็บไว้เป็น cell comment (hover ดูได้) เสมอเวลาฝังรูป
สำเร็จ ต้องมี Pillow (PIL) ติดตั้งอยู่ด้วย (openpyxl ใช้อ่านขนาดภาพจริงตอนฝัง)
"""

import argparse
import datetime
import json
import math
import os
import re
import sys
import tempfile

import openpyxl
from openpyxl.comments import Comment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

TC_COLUMNS = [
    "Test Case ID", "Module", "Feature", "Test Type", "Priority",
    "Test Scenario", "Pre-condition", "Test Step", "Test Data",
    "Expected Result", "Actual Result", "Status", "Issue link",
    "Test By", "Execution Date", "Remarks", "Test Photo",
]

TEST_TYPE_OPTIONS = ["positive", "negative", "edge case", "other"]
PRIORITY_OPTIONS = ["P0", "P1", "P2", "P3"]
STATUS_OPTIONS = ["not start", "Pass", "Fail", "Blocked", "Rejected / Not a Bug"]

TEST_TYPE_COLORS = {
    "positive": "C6EFCE",
    "negative": "FFC7CE",
    "edge case": "FFEB9C",
    "other": "D9D9D9",
}
PRIORITY_COLORS = {
    "P0": "FF0000",
    "P1": "FFA500",
    "P2": "FFFF00",
    "P3": "ADD8E6",
}
STATUS_COLORS = {
    "not start": "D9D9D9",
    "Pass": "C6EFCE",
    "Fail": "FFC7CE",
    "Blocked": "FFCC99",
    "Rejected / Not a Bug": "BFBFBF",
}

HEADER_FILL = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF")
THIN_SIDE = Side(style="thin", color="B7B7B7")
THIN_BORDER = Border(top=THIN_SIDE, bottom=THIN_SIDE, left=THIN_SIDE, right=THIN_SIDE)
NO_BORDER = Border()
NO_FILL = PatternFill(fill_type=None)
NOTE_FONT = Font(name="Calibri", size=11, color="FFFF0000")

# ---------------------------------------------------------------------------
# Layout engine constants (ดูหมายเหตุการฟอร์แมตด้านบน docstring)
# ---------------------------------------------------------------------------

LINE_HEIGHT_PT = 16
ROW_PADDING_PT = 6
MAX_ROW_HEIGHT_PT = 260
DEFAULT_MIN_HEIGHT_PT = 20

# ชีตที่ต้องการพื้นความสูงขั้นต่ำสูงกว่าปกติ (Test Case เผื่อที่ให้ Test Photo วางรูปได้จริง)
SHEET_MIN_HEIGHT_PT = {
    "Test Case": 90,
}

# คอลัมน์ Test Photo — ใส่รูปจริง (ฝังเข้าเซลล์) แทนที่จะเป็น path ข้อความเฉยๆ (แก้ตามที่ผู้ใช้ขอ
# หลังพบว่าคอลัมน์นี้มีแค่ข้อความ path ไม่ใช่รูปที่แนบมาให้ดูจริง) รอบแรกตั้งขนาด thumbnail ไว้แค่
# 160x100px ให้พอดีกับ SHEET_MIN_HEIGHT_PT เดิม แต่ผู้ใช้ทดสอบแล้วบอกว่าเล็กเกินไปจนมองไม่เห็นอะไร
# เลย (ภาพต้นฉบับเป็น screenshot 1280x720 — ย่อ 8 เท่าอ่านอะไรไม่ออกจริง) จึงขยายเป็นขนาดนี้แทน — เพื่อ
# ไม่ให้แถวถูกบีบเตี้ยกว่ารูปอีก (จะทำให้รูปโดนตัด/ทับกับแถวถัดไป) ต้องแก้ _finalize_layout ให้รู้จัก
# รูปที่ฝังไว้ในแต่ละแถวด้วย (ดู image_height_pt_by_row ใน _finalize_layout) ไม่ใช่พึ่งพา
# SHEET_MIN_HEIGHT_PT แบบเดาสุ่มเหมือนรอบแรกอีกต่อไป — ความกว้างคอลัมน์ Test Photo (Q) ก็ขยายจาก 32
# เป็น 45 หน่วยคู่กัน (ดู _build_test_case_sheet + WRAP_DRIVER_COLS["Test Case"]["Q"]) ให้พอดีกับ
# ความกว้างภาพใหม่ ไม่ให้ภาพล้นทะลุคอลัมน์สุดท้ายออกไปในพื้นที่ว่าง
PHOTO_COLUMN = "Test Photo"
PHOTO_MAX_W_PX = 280
PHOTO_MAX_H_PX = 200
PHOTO_ROW_PADDING_PT = 12
PX_TO_PT = 0.75  # 1px = 0.75pt ที่ 96 DPI มาตรฐาน (ใช้แปลงความสูงรูปเป็นหน่วยแถว Excel)

# เคสที่ Status เป็น Fail/Blocked คือหลักฐานที่สำคัญที่สุด (ต้องดูง่าย/ชัดที่สุดตอนตรวจสอบ) ต่างจาก Pass
# ที่ผู้ใช้ระบุชัดเจนว่าไม่ต้องเน้น — ใช้ขนาด thumbnail ที่ใหญ่กว่ามากสำหรับ Fail/Blocked โดยเฉพาะ (ดู
# _embed_photo) ส่วน Pass ยังคงใช้ PHOTO_MAX_W_PX/H_PX เดิมพร้อม fill-to-cell ตามปกติ ไม่เปลี่ยนแปลง
PHOTO_EMPHASIS_STATUSES = {"Fail", "Blocked"}
PHOTO_EMPHASIS_MAX_W_PX = 480
PHOTO_EMPHASIS_MAX_H_PX = 320


def _pad_box_to_aspect(left, top, right, bottom, img_w, img_h, target_aspect):
    """ขยายกรอบครอป (left, top, right, bottom) ให้สัดส่วนกว้าง:สูง ตรงกับ target_aspect มากที่สุดเท่าที่
    ทำได้ โดยไม่ล้นขอบภาพต้นฉบับ (img_w, img_h) — ใช้เพื่อให้ thumbnail หลังย่อขนาด "เต็มช่อง" เซลล์ปลายทาง
    พอดี แทนที่จะเหลือขอบขาวด้านใดด้านหนึ่ง (เพราะสัดส่วนเนื้อหาจริงในภาพกับสัดส่วนเซลล์ปลายทางไม่เท่ากัน)

    เลือกขยายด้านขวา/ล่างก่อนเสมอ (screenshot ของ mock-app มีพื้นที่ว่างเหลือเยอะทางขวา/ล่างของ UI จริง
    อยู่แล้ว) แล้วค่อยขยายด้านซ้าย/บนถ้าพื้นที่ฝั่งขวา/ล่างไม่พอ — ถ้าขยายเต็มที่แล้วยังไม่ถึงสัดส่วนเป้าหมาย
    (เช่นภาพต้นฉบับเล็กเกินไป) ก็คืนกรอบที่ขยายได้มากที่สุดเท่าที่ทำได้ ไม่ error
    """
    cur_w = right - left
    cur_h = bottom - top
    if cur_w <= 0 or cur_h <= 0 or not target_aspect or target_aspect <= 0:
        return left, top, right, bottom

    cur_aspect = cur_w / cur_h
    if abs(cur_aspect - target_aspect) < 0.02:
        return left, top, right, bottom

    if cur_aspect > target_aspect:
        # กรอบปัจจุบันกว้างเกินไปเทียบกับเป้าหมาย (เตี้ยเกินไป) — ต้องขยายความสูง
        desired_h = cur_w / target_aspect
        extra = desired_h - cur_h
        grow_bottom = min(extra, img_h - bottom)
        bottom += grow_bottom
        extra -= grow_bottom
        if extra > 0:
            grow_top = min(extra, top)
            top -= grow_top
    else:
        # กรอบปัจจุบันสูงเกินไปเทียบกับเป้าหมาย (แคบเกินไป) — ต้องขยายความกว้าง
        desired_w = cur_h * target_aspect
        extra = desired_w - cur_w
        grow_right = min(extra, img_w - right)
        right += grow_right
        extra -= grow_right
        if extra > 0:
            grow_left = min(extra, left)
            left -= grow_left

    return left, top, right, bottom


def _autocrop_to_content(pil_img, padding=24, bg_tolerance=12,
                          skip_if_fraction_over=0.85, min_content_px=20, target_aspect=None):
    """ตัดขอบพื้นหลังว่างๆ ออกก่อนย่อขนาด — คืนรูปที่ครอปแล้ว (หรือรูปเดิมถ้าครอปไม่ปลอดภัย/ไม่จำเป็น)

    พบปัญหาจริงกับ screenshot จาก mock-app: ตัว browser capture เต็ม viewport 1280x720 แต่ตัว UI จริง
    (ตะกร้าสินค้า/ฟอร์มกรอกโค้ด) มีขนาดแค่ราวๆ 480x200px วางอยู่มุมซ้ายบน ที่เหลือเป็นพื้นหลังขาวว่างเปล่า
    ทั้งหมด — ตอนย่อเป็น thumbnail (PHOTO_MAX_W_PX x PHOTO_MAX_H_PX) โดยไม่ครอปก่อน เนื้อหาที่มีประโยชน์
    จริงๆ เลยเหลือแค่เศษเสี้ยวของ thumbnail (ประมาณ 100x55px) เล็กจนแทบมองไม่ออกว่าเป็นอะไร ทั้งที่ตัว
    thumbnail ถูกฝังด้วยขนาด/ความละเอียดที่ถูกต้องแล้วก็ตาม — การขยาย PHOTO_MAX_W_PX/H_PX ต่อไปเรื่อยๆ
    แก้ปัญหานี้ไม่ได้จริง เพราะสัดส่วนเนื้อหา:พื้นหลังว่างในภาพต้นฉบับไม่เปลี่ยน ต้องครอปพื้นหลังว่างออก
    ก่อนย่อขนาดเสมอ เนื้อหาถึงจะเต็มเฟรมจริง

    ใช้สีมุมภาพ (0,0) เป็นสีพื้นหลังอ้างอิง หา bounding box ของพิกเซลที่ต่างจากพื้นหลังเกิน bg_tolerance
    แล้วเผื่อขอบ (padding) รอบ bounding box นั้น — เพื่อความปลอดภัย (ไม่อยากครอปผิดจนตัดเนื้อหาที่ตั้งใจ
    ให้เห็นเต็มจอออกไป) จะข้ามการครอปถ้า: หา bounding box ไม่เจอเลย (ภาพเป็นสีเดียวล้วน), bounding box
    ครอบคลุมพื้นที่ภาพเกิน skip_if_fraction_over อยู่แล้ว (แปลว่าภาพเต็มเฟรมอยู่แล้วจริงๆ ไม่ใช่กรณีนี้),
    หรือเกิด error ใดๆ ระหว่างคำนวณ — ทุกกรณีข้างต้นจะคืนรูปต้นฉบับกลับไปเฉยๆ ไม่ครอป

    ถ้าระบุ target_aspect (กว้าง/สูง ของเซลล์ปลายทางจริงที่จะฝังรูป) มาด้วย จะขยายกรอบครอปเพิ่มเติมให้
    สัดส่วนตรงกับเซลล์ปลายทางที่สุดเท่าที่ทำได้ (ดู _pad_box_to_aspect) — เพื่อให้ thumbnail ที่ย่อขนาด
    ภายหลังเต็มทั้งความกว้างและความสูงของเซลล์จริง แทนที่จะเหลือขอบขาวด้านใดด้านหนึ่งเพราะสัดส่วนไม่ตรงกัน
    (พบว่าครอปแค่ให้พอดีเนื้อหา (สัดส่วนธรรมชาติของ UI ~2:1) ไม่พอ ถ้าเซลล์ปลายทางสัดส่วนแคบกว่านั้น เช่น
    คอลัมน์กว้าง 45 หน่วย แถวสูงเท่าที่ข้อความใน Remarks ต้องการ ~1.75:1 — ก็ยังเหลือขอบขาวรอบรูปในเซลล์)
    """
    try:
        import numpy as np

        arr = np.asarray(pil_img)
        if arr.ndim != 3:
            return pil_img
        w, h = pil_img.size
        bg = arr[0, 0].astype(int)
        diff = np.abs(arr.astype(int) - bg).sum(axis=2)
        mask = diff > bg_tolerance
        ys, xs = np.where(mask)
        if len(xs) == 0 or len(ys) == 0:
            return pil_img  # สีเดียวล้วนทั้งภาพ — ไม่มีอะไรให้ครอป

        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        content_w, content_h = (x1 - x0), (y1 - y0)
        if content_w < min_content_px or content_h < min_content_px:
            return pil_img  # เนื้อหาเล็กเกินไปจนอาจเป็น noise ไม่ใช่ UI จริง — ไม่เสี่ยงครอปผิด

        if (content_w * content_h) >= skip_if_fraction_over * (w * h):
            return pil_img  # เนื้อหาเต็มเฟรมอยู่แล้ว ไม่ต้องครอป

        left = max(0, x0 - padding)
        top = max(0, y0 - padding)
        right = min(w, x1 + padding)
        bottom = min(h, y1 + padding)

        if target_aspect:
            left, top, right, bottom = _pad_box_to_aspect(left, top, right, bottom, w, h, target_aspect)

        return pil_img.crop((left, top, right, bottom))
    except Exception:
        return pil_img  # ครอปผิดพลาดกรณีใดก็ตาม — ปลอดภัยไว้ก่อน ใช้ภาพเต็มต้นฉบับ ไม่ทำให้ข้อมูลหาย


def _make_thumbnail_file(image_path, max_w, max_h, target_aspect=None):
    """ครอปพื้นหลังว่างออกก่อน (ดู _autocrop_to_content — ครอปให้พอดีสัดส่วน target_aspect ถ้าระบุมา)
    แล้วย่อรูปจริงๆ เซฟเป็นไฟล์ PNG ชั่วคราวใหม่ (คงสัดส่วนเดิมของภาพหลังครอป ไม่เกิน max_w x max_h พิกเซล)

    เหตุผลที่ต้องเซฟเป็นไฟล์ใหม่จริงๆ แทนที่จะแค่ตั้ง XLImage(...).width/.height ให้เล็กลงเฉยๆ: openpyxl
    ตอน save ไฟล์ .png/.jpeg/.gif จะ copy ไบต์ไฟล์ต้นฉบับตรงๆ ไม่สนใจ .width/.height ที่ override ไว้เลย
    (อ่าน source แล้วยืนยันจริง — ดู Image._data() ที่ seek(0) แล้วอ่าน fp ตรงๆ) แปลว่าต่อให้ตั้ง
    .width/.height เล็กลง ไฟล์ที่ฝังจริงก็ยังเป็นขนาดเต็มอยู่ดี แล้วพอ _finalize_layout เปิดไฟล์กลับมา
    อ่านใหม่ (เพื่อจัด layout อื่นๆ) มันจะคำนวณ .width/.height ใหม่จากขนาดภาพจริงในไฟล์อีกที ทำให้ค่าที่
    override ไว้หายไปเงียบๆ พอ save ซ้ำ (บั๊กที่เจอจริงระหว่างเขียนฟีเจอร์นี้ — ทดสอบแล้วว่า resize ที่
    เซฟเป็นไฟล์จริงแบบนี้ผ่าน round-trip โหลด/เซฟซ้ำหลายรอบได้ถูกต้อง เพราะขนาด "จริง" ของไฟล์เล็กลงจริง)
    """
    from PIL import Image as PILImage

    pil_img = PILImage.open(image_path)
    pil_img = pil_img.convert("RGB")
    pil_img = _autocrop_to_content(pil_img, target_aspect=target_aspect)
    pil_img.thumbnail((max_w, max_h), PILImage.LANCZOS)
    fd, thumb_path = tempfile.mkstemp(suffix=".png", prefix="qa_photo_thumb_")
    os.close(fd)
    pil_img.save(thumb_path, format="PNG", optimize=True)
    return thumb_path


def _col_width_to_px(width):
    """แปลงความกว้างคอลัมน์ Excel (หน่วย 'character width' ที่เก็บใน column_dimensions) เป็นพิกเซล
    โดยประมาณ — ใช้สูตรง่ายมาตรฐาน (Calibri 11, ~7px ต่อหน่วยตัวอักษร + 5px padding คงที่) ไม่ใช่สูตรทางการ
    ของ Excel เป๊ะๆ (ซึ่งซับซ้อนกว่านี้ ขึ้นกับ font metrics จริง) แต่แม่นพอสำหรับกะขนาดพื้นที่วางรูป"""
    if not width:
        return None
    return round(width * 7 + 5)


def _row_height_pt_to_px(height_pt):
    """แปลงความสูงแถว Excel (หน่วย point) เป็นพิกเซล — 1pt = 4/3 px ที่ความละเอียดมาตรฐาน 96 DPI"""
    if not height_pt:
        return None
    return round(height_pt * (4 / 3))


def _remove_photo_at(ws, row, col_idx):
    """ลบรูปที่เคยฝังไว้ที่ anchor (row, col_idx) นี้ออก (ถ้ามี) พร้อมเคลียร์ค่าเซลล์/comment ที่แนบมาด้วย
    ใช้ตอนเคส Retest เปลี่ยนจาก Fail เป็น Pass (qa-retest ขั้นตอนที่ 6 ข้อ 2 — ไม่ต้องเน้นหลักฐานภาพของ
    เคสที่ผ่านแล้วอีกต่อไป) — แยกออกมาจาก _embed_photo เพราะกรณีนี้ไม่มีรูปใหม่ให้ฝังทับ (ค่าที่ส่งมาว่างเปล่า)
    เดิม update_field/update_fields_batch จะข้าม branch นี้ไปเงียบๆ ถ้า value ว่าง ทำให้รูปเก่าค้างอยู่ในไฟล์
    ทั้งที่ Status เปลี่ยนเป็น Pass ไปแล้ว — แก้ช่องโหว่นี้ตรงนี้"""
    existing = getattr(ws, "_images", [])
    keep = []
    for im in existing:
        im_col = im.anchor._from.col if hasattr(im.anchor, "_from") else None
        im_row = im.anchor._from.row if hasattr(im.anchor, "_from") else None
        if im_col == col_idx - 1 and im_row == row - 1:
            continue
        keep.append(im)
    ws._images = keep
    cell = ws.cell(row=row, column=col_idx)
    cell.value = None
    cell.comment = None


def _embed_photo(ws, row, col_idx, image_path):
    """ฝังรูปจริง (ย่อขนาดคงสัดส่วนเป็นไฟล์ thumbnail จริงก่อน — ดู _make_thumbnail_file) ลงในเซลล์
    (row, col_idx) ของ ws แทนที่จะเขียนแค่ path เป็นข้อความ ลบรูปเก่าที่เคยฝังไว้ที่ตำแหน่งเดียวกันออก
    ก่อนเสมอ (กันภาพซ้อนกันเวลารันซ้ำ/อัปเดตผลทับของเดิม) เก็บ path ไฟล์ต้นฉบับ (ก่อนย่อ) ไว้เป็น
    cell comment (hover ดูได้) แทนการโชว์เป็นข้อความในเซลล์ตรงๆ เพราะข้อความจะไปทับ/ปนกับรูปที่ลอยอยู่
    ด้านบน ดูรก — คืนค่า True ถ้าฝังสำเร็จ, False ถ้าไม่พบไฟล์รูป (ในกรณีนี้จะ fallback กลับไปเขียน path
    เป็นข้อความในเซลล์แทน เพื่อไม่ให้ข้อมูลหายไปเงียบๆ)

    ผู้ใช้ระบุชัดเจนว่าไม่ต้องการให้เน้น Pass — ให้เน้นเฉพาะ Fail/Blocked (หลักฐานที่สำคัญที่สุดตอนตรวจสอบ)
    ให้ใหญ่ชัดแทน จึงแยกการคำนวณขนาด thumbnail เป็น 2 ทาง ตาม Status ปัจจุบันของแถวนั้น (อ่านจากคอลัมน์
    Status ในชีตตรงๆ ณ ตอนฝังรูป):
    - Fail/Blocked: ใช้เพดานขนาดใหญ่ที่ตั้งไว้ตายตัว (PHOTO_EMPHASIS_MAX_W_PX/H_PX) ครอปแบบพอดีเนื้อหา UI
      ธรรมชาติเท่านั้น (ไม่บังคับสัดส่วนตามเซลล์ — ปล่อยให้ _finalize_layout ขยายความสูงแถวให้พอดีกับรูป
      ใหญ่นี้เอาเองภายหลัง ผลคือรูปใหญ่ชัดไม่มีขอบขาวเกินจำเป็นรอบเนื้อหา)
    - Pass (หรือสถานะอื่น): คงพฤติกรรมเดิม — คำนวณพื้นที่ว่างจริงของเซลล์ปลายทาง ณ ขณะนั้น (ความกว้าง
      คอลัมน์ปัจจุบัน, ความสูงแถวปัจจุบัน) แล้วครอป+ย่อให้เต็มพอดีเซลล์เดิม ไม่เปลี่ยนแปลงขนาดที่เคยเป็น
    """
    col_letter = get_column_letter(col_idx)
    anchor = f"{col_letter}{row}"

    if not image_path or not os.path.isfile(image_path):
        return False

    # ลบรูปเก่าที่ anchor ตำแหน่งเดียวกัน (ถ้ามี) ก่อนฝังรูปใหม่ — ป้องกันรูปซ้อนกันหลายชั้นเวลา
    # Skill 06a/10 เขียนผลทับซ้ำ (เช่น qa-retest รันซ้ำเฉพาะเคสที่ Fail แล้วอัปเดตภาพใหม่)
    existing = getattr(ws, "_images", [])
    keep = []
    for im in existing:
        im_col = im.anchor._from.col if hasattr(im.anchor, "_from") else None
        im_row = im.anchor._from.row if hasattr(im.anchor, "_from") else None
        # openpyxl เก็บ col/row แบบ 0-based ใน anchor._from ต่างจาก openpyxl cell ที่ 1-based
        if im_col == col_idx - 1 and im_row == row - 1:
            continue
        keep.append(im)
    ws._images = keep

    status_col = TC_COLUMNS.index("Status") + 1
    status = ws.cell(row=row, column=status_col).value

    if status in PHOTO_EMPHASIS_STATUSES:
        target_w = PHOTO_EMPHASIS_MAX_W_PX
        target_h = PHOTO_EMPHASIS_MAX_H_PX
        target_aspect = None  # ครอปพอดีเนื้อหาธรรมชาติ ไม่บังคับยืดสัดส่วน ให้ใหญ่ชัดไม่มีขอบขาวเกินจำเป็น
    else:
        col_dim = ws.column_dimensions.get(col_letter)
        avail_w_px = _col_width_to_px(col_dim.width if col_dim else None) or PHOTO_MAX_W_PX
        row_dim = ws.row_dimensions.get(row)
        fallback_pt = SHEET_MIN_HEIGHT_PT.get(ws.title, DEFAULT_MIN_HEIGHT_PT)
        avail_h_px = _row_height_pt_to_px(row_dim.height if row_dim else None) or _row_height_pt_to_px(fallback_pt)

        margin_px = 6  # เผื่อขอบเล็กน้อยไม่ให้รูปชิดเส้นกรอบเซลล์สนิทเกินไป
        target_w = max(20, min(avail_w_px - margin_px, PHOTO_MAX_W_PX))
        target_h = max(20, min(avail_h_px - margin_px, PHOTO_MAX_H_PX))
        target_aspect = target_w / target_h

    thumb_path = _make_thumbnail_file(image_path, target_w, target_h, target_aspect=target_aspect)
    img = XLImage(thumb_path)
    ws.add_image(img, anchor)

    cell = ws.cell(row=row, column=col_idx)
    cell.value = None
    cell.comment = Comment(f"ไฟล์ต้นฉบับ: {image_path}", "qa_workbook.py")
    return True

# sheet name -> {column_letter: width} สำหรับคอลัมน์ที่ข้อความ wrap ควรเป็นตัวกำหนดความสูงแถว
# (ต้องตรงกับความกว้างจริงที่ตั้งใน _autosize ของแต่ละชีต)
WRAP_DRIVER_COLS = {
    "Test Case": {
        "A": 12, "B": 18, "C": 25, "D": 12, "E": 10, "F": 40, "G": 30,
        "H": 70, "I": 60, "J": 45, "K": 45, "L": 14, "M": 35, "N": 12,
        # Q (Test Photo) = 71 หน่วย (~502px) ไม่ใช่ 45 (~320px) เหมือนเดิม — ขยายเพื่อรองรับรูป
        # Fail/Blocked ที่ตอนนี้ใหญ่ถึง 480px กว้าง (ดู PHOTO_EMPHASIS_MAX_W_PX) ถ้าคอลัมน์แคบกว่านี้
        # รูปจะล้นขอบคอลัมน์ออกไปแทนที่จะอยู่ใน "กรอบ" ตามที่ผู้ใช้ขอ — ผลข้างเคียงที่ต้องรู้ไว้: รูป
        # Pass (คงเพดานเดิม 280px ไม่เปลี่ยน เพราะไม่ต้องการให้ Pass ใหญ่ตาม) จะเหลือพื้นที่ว่างด้านขวา
        # ของคอลัมน์มากขึ้นกว่าก่อนหน้านี้ (ก่อนหน้าเคย fill พอดี 280/320) แต่ผู้ใช้ยืนยันแล้วว่ายอมรับ
        # trade-off นี้เพื่อให้ Fail/Blocked อยู่ในกรอบพอดีจริง ไม่ล้น
        "O": 14, "P": 45, "Q": 71,
    },
    "Requirement Matrix": {"B": 55, "C": 28, "D": 30},
    "Env & Config": {"B": 60},
    "Priority & Risk Matrix": {"B": 55, "C": 45},
    "Glossary": {"B": 60},
    # เดิมมีแค่ "D" เป็น driver — แถวป้ายกำกับ (Feature / Current Version / Last Updated ที่แถว
    # 3-5) ใช้คอลัมน์ A/B แต่ column width เดิม (10/14) แคบเกินไปจนข้อความอย่าง "Current Version"
    # ต้องขึ้นบรรทัดใหม่ ในขณะที่ความสูงแถวคำนวณจากคอลัมน์ D เท่านั้น (ซึ่งว่างเปล่าในแถวนั้น) — แถว
    # เลยเตี้ยเกินไปจนข้อความ 2 บรรทัดถูกตัด/ทับกันจริงเมื่อเปิดใน Excel จริง (LibreOffice ที่ใช้
    # เรนเดอร์ PDF ตรวจสอบไม่เจอเพราะมันคำนวณความสูงแถวใหม่เองเสมอ ไม่สนใจค่าที่บันทึกในไฟล์)
    # แก้โดยกว้างคอลัมน์ A/B ให้พอสำหรับข้อความจริง (ดู _build_document_control) และใส่ทั้งคู่เป็น
    # wrap driver ไว้ด้วย เผื่อชื่อ Feature ยาวจนต้อง wrap ในอนาคต ความสูงแถวจะยังคำนวณถูกต้อง
    "Document Control": {"A": 20, "B": 26, "D": 50},
}

# sheet name -> set ของคอลัมน์ที่ให้ align กึ่งกลางแนวนอน (นอกเหนือจาก header ที่กึ่งกลางเสมออยู่แล้ว)
# ข้อควรระวัง: ห้ามใส่คอลัมน์ที่มีข้อความยาวหลายบรรทัดลงในนี้ — center + wrap_text + vertical="top"
# เรนเดอร์เพี้ยนเป็นเหมือน vertical-center ทั้งใน LibreOffice และ Excel จริง (ยืนยันจากการทดสอบจริง)
# เคสที่เจอ: Requirement Matrix คอลัมน์ D (Coverage Status) เคย center ไว้ แล้ว multi-line text ดู
# เหมือนลอยกลางเซลล์ไม่ชิดบนเหมือนคอลัมน์ข้างๆ ที่ align ซ้าย — แก้โดยเอา D ออกจาก set นี้
CENTER_COLS = {
    "Test Case": {"A", "D", "E", "L", "N", "O", "Q"},
    "Requirement Matrix": {"A"},
    "Priority & Risk Matrix": {"A"},
    "Document Control": {"A", "B"},
}

# ชีตที่ fitToHeight=0 (พิมพ์ข้ามหลายหน้าได้ ไม่บีบให้พอดี 1 หน้า) — ทุกชีตอื่น fitToHeight=1
UNLIMITED_HEIGHT_SHEETS = {"Test Case"}

# sheet name -> set ของคอลัมน์ที่เป็น "ช่องไฟ" ล้วนๆ (ตั้งใจเว้นว่างเสมอ ไม่มีข้อมูล ไม่มีกรอบ) —
# ต่างจากแถวว่างเปล่า (is_blank_row) ตรงที่นี่คือ "คอลัมน์" ว่างเปล่าใน "แถวที่มีข้อมูล" (เช่น
# Requirement Matrix คอลัมน์ E คั่นระหว่างตารางกับ caption ข้างขวาที่คอลัมน์ F) — ถ้าไม่ยกเว้นไว้ตรงนี้
# generic pass ด้านล่างจะเห็นว่าแถวนั้น "มีข้อมูล" (เพราะ F มีข้อความ) แล้วใส่กรอบให้ทุกเซลล์ในแถว
# รวมถึงคอลัมน์ช่องไฟด้วย ทำให้ช่องไฟที่ควรจะโปร่งใสกลายเป็นกล่องเปล่าที่มองเห็นได้ (ยืนยันจากไฟล์จริง)
GAP_COLS = {
    "Requirement Matrix": {"E"},
}


def _style_header_row(ws, row_idx, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER


def _autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _normalize_quotes(value):
    """แทน ' (single quote) ด้วย " (double quote) ในข้อความ — ใช้กับข้อความล้วนเท่านั้น
    (ห้ามใช้กับสูตร ตัวเรียกจึงต้องเช็คว่า value ไม่ได้ขึ้นต้นด้วย '=' ก่อนเรียกฟังก์ชันนี้เสมอ)
    """
    if isinstance(value, str) and not value.startswith("="):
        return value.replace("'", '"')
    return value


_STEP_SPLIT_RE = re.compile(r"(?=\d+\)\s)")
_DATA_SPLIT_RE = re.compile(r",\s*(?=[^,]*?[:=])")


def _split_test_step(text):
    """แยกแต่ละข้อของ Test Step (รูปแบบ '1) ... 2) ... 3) ...') ให้ขึ้นบรรทัดใหม่ (\\n จริง)
    แทนที่จะปล่อยให้ word-wrap ตัดกลางข้อความเอง — ผู้เขียน Test Step (AI หรือคน) ไม่ต้องทำอะไรพิเศษ
    เขียนเป็น '1) ... 2) ... 3) ...' ตามปกติ ฟังก์ชันนี้จะจัดการแยกบรรทัดให้อัตโนมัติ
    """
    if not isinstance(text, str) or not text:
        return text
    parts = [p.strip() for p in _STEP_SPLIT_RE.split(text) if p.strip()]
    if len(parts) <= 1:
        return text
    return "\n".join(parts)


def _split_test_data(text):
    """แยก Test Data ที่มีหลาย key=value (หรือ label: value) คั่นด้วย comma ให้ขึ้นบรรทัดใหม่
    คอมม่าจะถูกตัดบรรทัดก็ต่อเมื่อสิ่งที่ตามมาหลังจากมันมีลักษณะเป็น label ใหม่ (มี '=' หรือ ':')
    เท่านั้น — ประโยคบรรยายธรรมดาที่มี comma ปนอยู่จะไม่ถูกแตะ
    """
    if not isinstance(text, str) or not text:
        return text
    parts = [p.strip() for p in _DATA_SPLIT_RE.split(text) if p.strip()]
    if len(parts) <= 1:
        return text
    return "\n".join(parts)


def _est_lines(text, col_width):
    """ประมาณจำนวนบรรทัดที่ข้อความจะ wrap ใน column ความกว้าง col_width — ตั้งใจประมาณแบบ
    "อนุรักษ์นิยม" (เผื่อบรรทัดเกินดีกว่าขาด) เพราะแถวที่สูงเกินไปนิดหน่อยไม่เป็นปัญหา แต่แถวที่เตี้ย
    เกินไปจะทำให้ข้อความโดนตัดพอไปเปิดใน Excel จริง (ต่างจาก LibreOffice PDF export ที่คำนวณความสูง
    ให้เองเสมอไม่ว่าไฟล์จะเก็บค่าอะไรไว้ — ทำให้บั๊กนี้มองไม่เห็นตอนตรวจผ่าน PDF)
    """
    if text in (None, ""):
        return 1
    text = str(text)
    chars_per_line = max(6, int(col_width * 1.3))
    total_lines = 0
    for segment in text.split("\n"):
        total_lines += max(1, math.ceil(len(segment) / chars_per_line))
    return total_lines + 1  # +1 บรรทัดเผื่อ headroom


def _merged_full_width_note_rows(ws):
    """หา row ที่มี caption/note ถูก merge เต็มความกว้างที่ใช้งานของชีต (แบบ Executive Dashboard)
    เพื่อให้คำนวณความสูงจากผลรวมความกว้างทุกคอลัมน์ที่ merge ไว้ แทนที่จะใช้ความกว้างคอลัมน์เดียว
    """
    max_col = ws.max_column
    result = {}
    for merged_range in ws.merged_cells.ranges:
        if (
            merged_range.min_row == merged_range.max_row
            and merged_range.min_col == 1
            and merged_range.max_col == max_col
        ):
            r = merged_range.min_row
            # ต้องใช้ .get() ไม่ใช่ [] — การอ่านด้วย [] บน DimensionHolder จะสร้าง
            # ColumnDimension ใหม่ให้อัตโนมัติสำหรับคอลัมน์ที่ยังไม่เคยตั้ง width มาก่อน (แม้แค่
            # "อ่าน" เฉยๆ) แล้วค่า default (13.0) ที่ถูกสร้างขึ้นมานี้จะถูกบันทึกลงไฟล์จริงตอน save
            # กลายเป็นความกว้างคอลัมน์ปลอมๆ ที่ไม่ได้ตั้งใจ (บั๊กที่เจอจริงตอนตรวจสอบ: Executive
            # Dashboard คอลัมน์ D-G ที่ไม่เคยตั้ง width ไว้เลย กลับโดนบันทึกเป็น 13.0 ไปด้วย)
            total_width = 0
            for c in range(1, max_col + 1):
                dim = ws.column_dimensions.get(get_column_letter(c))
                total_width += (dim.width if dim and dim.width else 8.43)
            result[r] = total_width
    return result


def _finalize_layout(path):
    """จัดฟอร์แมตทั้ง Workbook ใหม่ทั้งไฟล์: normalize เครื่องหมายคำพูด, wrap/border/align เซลล์ข้อมูล,
    คำนวณความสูงแถวจากเนื้อหาจริง, ตั้งค่า page setup/freeze panes/print title rows

    เรียกอัตโนมัติท้าย add_test_cases / update_field / update_fields_batch อยู่แล้ว — เรียกตรงๆ
    เองอีกครั้ง (ผ่าน CLI subcommand finalize-layout) หลังแก้ไขเซลล์ด้วยมือ (เช่น เติมแถว
    Requirement Matrix ตามขั้นตอนที่ 4 ใน SKILL.md) เสมอ
    """
    wb = openpyxl.load_workbook(path)

    for name in wb.sheetnames:
        ws = wb[name]
        max_row, max_col = ws.max_row, ws.max_column
        if max_row < 1 or max_col < 1:
            continue

        center_set = CENTER_COLS.get(name, set())
        gap_set = GAP_COLS.get(name, set())
        is_dc_history = name == "Document Control"

        nonempty_per_row = {}
        for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
            r = row[0].row
            nonempty_per_row[r] = sum(1 for c in row if c.value not in (None, ""))

        # เซลล์ note สีแดง (เช่น Dashboard's A3:G3) ถ้าถูก merge ไว้ เฉพาะเซลล์มุมบนซ้าย (anchor)
        # เท่านั้นที่มี .font จริง ส่วนเซลล์ MergedCell อื่นๆ ในช่วงเดียวกันมี font เริ่มต้น (ไม่แดง)
        # เสมอ — ถ้าเช็คสีทีละเซลล์แบบตรงๆ เซลล์ที่ไม่ใช่ anchor จะหลุด แล้วโดน border/alignment ปกติ
        # ทับ (บั๊กที่เจอจริง: ขอบ thin โผล่มาที่ขอบล่างของ merge range ทั้งที่ตั้งใจไม่ให้มีกรอบเลย)
        # จึงต้องเดินหา merged range ที่ anchor เป็นสีแดงไว้ก่อน แล้ว mark ทุกเซลล์ในช่วงนั้นให้ข้าม
        protected_note_cells = set()
        for merged_range in ws.merged_cells.ranges:
            anchor = ws.cell(row=merged_range.min_row, column=merged_range.min_col)
            if anchor.font and anchor.font.color and anchor.font.color.rgb == "FFFF0000":
                for rr in range(merged_range.min_row, merged_range.max_row + 1):
                    for cc in range(merged_range.min_col, merged_range.max_col + 1):
                        protected_note_cells.add((rr, cc))
        # เซลล์ note สีแดงแบบ "เดี่ยว" ไม่ได้ merge เลย (เช่น Requirement Matrix's F2 ที่วางข้าง
        # ตาราง) ก็ต้องอยู่ใน set เดียวกันนี้ด้วย ไม่งั้น logic คำนวณความสูงแถวด้านล่าง (ซึ่งอ่านจาก
        # protected_note_cells อย่างเดียว) จะไม่รู้จักเซลล์นี้เลย
        for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
            for cell in row:
                if cell.font and cell.font.color and cell.font.color.rgb == "FFFF0000":
                    protected_note_cells.add((cell.row, cell.column))

        # ก่อนอื่นทำ quote normalization ทุกเซลล์ข้อความ (ไม่แตะสูตร)
        for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
            for cell in row:
                if isinstance(cell.value, str):
                    cell.value = _normalize_quotes(cell.value)

        for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
            for cell in row:
                # MergedCell (non-anchor cells inside a merged range, e.g. the
                # Dashboard note merged A3:G3) has no .column_letter in this
                # openpyxl version — get_column_letter(cell.column) works for
                # both Cell and MergedCell alike.
                col_letter = get_column_letter(cell.column)
                r = cell.row
                is_header = r == 1 or (is_dc_history and r == 7)
                lone_title = r == 1 and nonempty_per_row.get(1, 0) <= 1
                is_blank_row = nonempty_per_row.get(r, 0) == 0

                if is_blank_row:
                    continue  # แถวว่างเปล่าตั้งใจ (spacer) — ไม่ต้องใส่กรอบ/wrap ให้
                if col_letter in gap_set:
                    continue  # คอลัมน์ช่องไฟ (เช่น Requirement Matrix คอลัมน์ E) — ไม่ใส่กรอบ/wrap ให้เช่นกัน แม้แถวนั้นจะมีข้อมูลในคอลัมน์อื่น
                if lone_title:
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
                    continue
                # เซลล์ note สีแดง (font สีแดงที่ตั้งไว้ตอนสร้างชีต ไม่ว่าจะ merge ไว้หรือเป็นเซลล์เดี่ยว)
                # ข้ามไปเลย ไม่ให้ generic pass นี้ไปเขียนทับ border/alignment ที่ตั้งใจไว้เป็นพิเศษ
                is_note_cell = (cell.font and cell.font.color and cell.font.color.rgb == "FFFF0000") or (
                    (r, cell.column) in protected_note_cells
                )
                if is_note_cell:
                    continue
                if is_header:
                    continue  # _style_header_row จัดการไปแล้วตอนสร้างชีต
                horiz = "center" if col_letter in center_set else "left"
                cell.alignment = Alignment(horizontal=horiz, vertical="top", wrap_text=True)
                if cell.border.top.style is None:
                    cell.border = THIN_BORDER

        # ความสูงแถว: แถว note ที่ merge เต็มความกว้างก่อน (ใช้ผลรวมความกว้างทุกคอลัมน์)
        note_rows = _merged_full_width_note_rows(ws)
        min_height = SHEET_MIN_HEIGHT_PT.get(name, DEFAULT_MIN_HEIGHT_PT)

        # รูปที่ฝังไว้ (เช่น Test Photo) เป็น floating object ไม่ใช่เนื้อหาเซลล์ — WRAP_DRIVER_COLS/
        # _est_lines ที่คำนวณความสูงแถวจาก "ข้อความ" ล้วนๆ ด้านล่างไม่รู้จักมันเลย ถ้าไม่เผื่อไว้ตรงนี้
        # แถวที่มีรูปฝังอยู่จะโดนคำนวณความสูงจากข้อความอย่างเดียว ซึ่งอาจเตี้ยกว่ารูปจริง ทำให้รูปโดนตัด/
        # ทับกับแถวถัดไปเวลาเรียก finalize-layout ซ้ำ (เจอบั๊กนี้จริงตอนผู้ใช้ทดสอบรอบแรก — ตอนนั้นรอด
        # มาได้เพราะ SHEET_MIN_HEIGHT_PT ที่ตั้งไว้ล่วงหน้าบังเอิญพอดีกับ thumbnail เล็กๆ เท่านั้น พอขยาย
        # thumbnail ให้ใหญ่ขึ้นตามที่ผู้ใช้ขอ จะพึ่งพาความบังเอิญแบบนั้นต่อไปไม่ได้แล้ว) จึงต้องเก็บ
        # ความสูงที่รูปต้องการไว้ล่วงหน้าต่อแถว แล้วเอาไปรวมกับ max_lines ด้านล่างเป็น max เสมอ
        image_height_pt_by_row = {}
        for im in getattr(ws, "_images", []):
            try:
                im_row = im.anchor._from.row + 1  # anchor เก็บแบบ 0-based, แถวอื่นในฟังก์ชันนี้ 1-based
                im_h_px = im.height
            except Exception:
                continue
            needed_pt = im_h_px * PX_TO_PT + PHOTO_ROW_PADDING_PT
            image_height_pt_by_row[im_row] = max(image_height_pt_by_row.get(im_row, 0), needed_pt)
        for r, total_width in note_rows.items():
            text = ws.cell(row=r, column=1).value
            lines = _est_lines(text, total_width)
            text_height = max(min_height, lines * LINE_HEIGHT_PT + ROW_PADDING_PT)
            height = min(MAX_ROW_HEIGHT_PT, max(text_height, image_height_pt_by_row.get(r, 0)))
            ws.row_dimensions[r].height = height

        # note ที่เป็น "เซลล์เดี่ยว" ไม่ได้ merge เต็มความกว้าง (เช่น Requirement Matrix's F2 —
        # caption วางข้างตาราง ไม่ได้ merge กับอะไรเลย) ก็ต้องมีความกว้างคอลัมน์ของตัวเองมาเป็นตัวกำหนด
        # จำนวนบรรทัดด้วย ไม่งั้นแถวนั้นจะถูกคำนวณความสูงจากแค่คอลัมน์ข้อมูลตาราง (WRAP_DRIVER_COLS)
        # เท่านั้น ซึ่งมักสั้นกว่า caption มาก — ทำให้ทุกครั้งที่เรียก finalize-layout ซ้ำ แถวนี้จะถูก
        # บีบเตี้ยลงเรื่อยๆ (บั๊กที่เจอจริง: รันซ้ำหนึ่งครั้งแล้ว caption ที่เคยสูงพอดีถูกบีบจนข้อความ
        # โดนตัดในโปรแกรม Excel จริง) จึงต้อง fold เข้าไปในการคำนวณ max_lines ของแถวนั้นด้วยเสมอ
        single_note_cols_by_row = {}
        for (rr, cc) in protected_note_cells:
            if rr in note_rows:
                continue  # full-width merge จัดการไปแล้วด้านบน
            single_note_cols_by_row.setdefault(rr, []).append(cc)

        cols = WRAP_DRIVER_COLS.get(name, {})
        for r in range(1, max_row + 1):
            if r in note_rows:
                continue
            if nonempty_per_row.get(r, 0) == 0:
                continue
            max_lines = 1
            for col_letter, width in cols.items():
                val = ws[f"{col_letter}{r}"].value
                max_lines = max(max_lines, _est_lines(val, width))
            for cc in single_note_cols_by_row.get(r, []):
                col_letter = get_column_letter(cc)
                dim = ws.column_dimensions.get(col_letter)
                width = dim.width if dim and dim.width else 8.43
                val = ws.cell(row=r, column=cc).value
                max_lines = max(max_lines, _est_lines(val, width))
            text_height = max(min_height, max_lines * LINE_HEIGHT_PT + ROW_PADDING_PT)
            height = min(MAX_ROW_HEIGHT_PT, max(text_height, image_height_pt_by_row.get(r, 0)))
            ws.row_dimensions[r].height = height

        # page setup: ทุกชีต landscape + fit ความกว้าง 1 หน้าเสมอ; ความสูงปล่อยหลายหน้าได้เฉพาะ
        # ชีตที่อยู่ใน UNLIMITED_HEIGHT_SHEETS (Test Case) เพราะคอลัมน์เยอะ+แถวสูง บีบให้พอดี
        # 1 หน้าจะเล็กจนอ่านไม่ออก
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0 if name in UNLIMITED_HEIGHT_SHEETS else 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_margins.left = 0.4
        ws.page_margins.right = 0.4
        ws.page_margins.top = 0.5
        ws.page_margins.bottom = 0.5
        ws.page_margins.header = 0.2
        ws.page_margins.footer = 0.2
        if max_row > 1:
            ws.print_title_rows = "1:1"
            ws.freeze_panes = "A2"

    wb.save(path)


# ---------------------------------------------------------------------------
# Sheet builders
# ---------------------------------------------------------------------------

def _build_document_control(wb, feature_name):
    ws = wb.create_sheet("Document Control")
    ws["A1"] = "Document Control"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A3"] = "Feature"
    ws["B3"] = feature_name
    ws["A4"] = "Current Version"
    ws["B4"] = 1
    ws["A5"] = "Last Updated"
    ws["B5"] = datetime.date.today().isoformat()

    headers = ["Version", "Date", "Edited By (Skill)", "Change Note"]
    ws.append([])
    header_row = 7
    for i, h in enumerate(headers, start=1):
        ws.cell(row=header_row, column=i, value=h)
    _style_header_row(ws, header_row, len(headers))
    ws.cell(row=header_row + 1, column=1, value=1)
    ws.cell(row=header_row + 1, column=2, value=datetime.date.today().isoformat())
    ws.cell(row=header_row + 1, column=3, value="test-case-generator")
    ws.cell(row=header_row + 1, column=4, value="สร้าง Workbook ครั้งแรก")
    # A=20/B=26 (เดิม 10/14 แคบเกินไปจนป้าย "Current Version"/"Last Updated" และค่า Feature
    # ต้อง wrap แล้วโดนตัดในไฟล์ Excel จริง — ดูหมายเหตุที่ WRAP_DRIVER_COLS ด้านบน)
    _autosize(ws, [20, 26, 24, 50])
    return ws


def _build_dashboard(wb):
    """หน้าสรุปภาพรวม (dashboard-style) — note/caption คงตำแหน่งเดิม (แถว 3 คั่นด้วยแถวว่าง)
    แค่ตัวอักษรแดงครอบด้วย * และไม่มีกรอบ (ต่างจาก Requirement Matrix ที่เป็น table-style —
    ดูหมายเหตุใน _build_requirement_matrix)"""
    ws = wb.create_sheet("Executive Dashboard", 0)
    ws["A1"] = "Executive Dashboard"
    ws["A1"].font = Font(bold=True, size=16)

    note_text = "สรุปนี้จะถูกคำนวณอัตโนมัติจากชีต Test Case (สูตร COUNTIF อ้างอิงชีต \"Test Case\")"
    ws.merge_cells("A3:G3")
    note_cell = ws["A3"]
    note_cell.value = f"*{note_text}*"
    note_cell.font = NOTE_FONT
    note_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    labels = [
        ("Total Test Cases", "=COUNTA('Test Case'!A2:A100000)"),
        ("Pass", "=COUNTIF('Test Case'!L2:L100000,\"Pass\")"),
        ("Fail", "=COUNTIF('Test Case'!L2:L100000,\"Fail\")"),
        ("Not Start", "=COUNTIF('Test Case'!L2:L100000,\"not start\")"),
        ("Rejected / Not a Bug", "=COUNTIF('Test Case'!L2:L100000,\"Rejected / Not a Bug\")"),
        ("P0 Count", "=COUNTIF('Test Case'!E2:E100000,\"P0\")"),
        ("P1 Count", "=COUNTIF('Test Case'!E2:E100000,\"P1\")"),
    ]
    row = 5
    for label, formula in labels:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=formula)
        row += 1

    # Status Pie chart
    from openpyxl.chart import BarChart, PieChart, Reference

    chart_data_row = row + 2
    ws.cell(row=chart_data_row, column=1, value="Status")
    ws.cell(row=chart_data_row, column=2, value="Count")
    ws.cell(row=chart_data_row + 1, column=1, value="Pass")
    ws.cell(row=chart_data_row + 1, column=2, value="=B6")
    ws.cell(row=chart_data_row + 2, column=1, value="Fail")
    ws.cell(row=chart_data_row + 2, column=2, value="=B7")
    ws.cell(row=chart_data_row + 3, column=1, value="Not Start")
    ws.cell(row=chart_data_row + 3, column=2, value="=B8")
    ws.cell(row=chart_data_row + 4, column=1, value="Rejected / Not a Bug")
    ws.cell(row=chart_data_row + 4, column=2, value="=B9")

    pie = PieChart()
    pie.title = "Test Case Status"
    data = Reference(ws, min_col=2, min_row=chart_data_row, max_row=chart_data_row + 4)
    cats = Reference(ws, min_col=1, min_row=chart_data_row + 1, max_row=chart_data_row + 4)
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(cats)
    ws.add_chart(pie, f"D{chart_data_row}")

    bar = BarChart()
    bar.title = "Priority Breakdown"
    bar_row = chart_data_row
    ws.cell(row=bar_row, column=6, value="Priority")
    ws.cell(row=bar_row, column=7, value="Count")
    for i, p in enumerate(PRIORITY_OPTIONS, start=1):
        ws.cell(row=bar_row + i, column=6, value=p)
        ws.cell(row=bar_row + i, column=7, value=f"=COUNTIF('Test Case'!E2:E100000,\"{p}\")")
    bar_data = Reference(ws, min_col=7, min_row=bar_row, max_row=bar_row + len(PRIORITY_OPTIONS))
    bar_cats = Reference(ws, min_col=6, min_row=bar_row + 1, max_row=bar_row + len(PRIORITY_OPTIONS))
    bar.add_data(bar_data, titles_from_data=True)
    bar.set_categories(bar_cats)
    ws.add_chart(bar, f"D{bar_row + 16}")

    _autosize(ws, [24, 40])
    return ws


def _build_requirement_matrix(wb):
    """ชีตแบบตาราง (table-style) — header อยู่แถว 1 ตามปกติ ไม่มีแถวว่างคั่น ข้อมูลเริ่มแถว 2 ทันที
    ส่วน note/caption ย้ายไปอยู่ "ข้างขวา" ของตาราง บรรทัดเดียวกับแถวข้อมูลแถวแรก (คอลัมน์ E เว้นว่าง
    เป็นช่องไฟ คอลัมน์ F คือ note) — ต่างจาก _build_dashboard ที่เป็น dashboard-style (คงตำแหน่งเดิม
    มีแถวว่างคั่น) เพราะชีตนี้มีตารางที่มีกรอบจริงๆ การเอา note ไปแทรกกลางๆ ตารางจะดูสะดุด"""
    ws = wb.create_sheet("Requirement Matrix")
    headers = ["Requirement / Business Rule ID", "รายละเอียด", "Test Case ID ที่ครอบคลุม", "Coverage Status"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=1, column=i, value=h)
    _style_header_row(ws, 1, len(headers))

    note_text = (
        "(เติมโดยอ้างอิงจาก 01-requirement-review.md และ 02-e2e-flow.md — 1 แถวต่อ 1 Business "
        "Rule/Flow — Skill coverage-review (04) จะใช้ชีตนี้ตรวจ Coverage)"
    )
    note_cell = ws.cell(row=2, column=6)  # แถว 2 = แถวข้อมูลแถวแรกที่จะถูกเติมทีหลัง (ขั้นตอนที่ 4)
    note_cell.value = f"*{note_text}*"
    note_cell.font = NOTE_FONT
    note_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.row_dimensions[2].height = 70  # เผื่อพอสำหรับ note ที่ความกว้างคอลัมน์ F=45 — _finalize_layout
    # จะคำนวณใหม่ให้สูงขึ้นอีกถ้าข้อมูลจริงในแถว 2 (B/C/D) ต้องการมากกว่านี้ (ไม่มีวันลดลงต่ำกว่านี้)

    _autosize(ws, [28, 55, 28, 30, 3, 45])
    ws.freeze_panes = "A2"
    return ws


def _build_env_config(wb):
    ws = wb.create_sheet("Env & Config")
    rows = [
        ["Environment", ""],
        ["URL", ""],
        ["Test Account(s)", ""],
        ["Browser(s) ที่ต้องเทส", ""],
        ["Device(s) ที่ต้องเทส", ""],
        ["หมายเหตุ Config อื่นๆ", ""],
    ]
    ws.append(["Key", "Value"])
    _style_header_row(ws, 1, 2)
    for r in rows:
        ws.append(r)
    _autosize(ws, [26, 60])
    return ws


def _build_priority_risk_matrix(wb):
    ws = wb.create_sheet("Priority & Risk Matrix")
    headers = ["Priority", "นิยาม", "ตัวอย่าง"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=1, column=i, value=h)
    _style_header_row(ws, 1, len(headers))
    defs = [
        ["P0", "ระบบใช้งานไม่ได้เลย / ข้อมูล/เงิน/ความปลอดภัยเสียหาย", "Login ไม่ได้เลย, ข้อมูลบัตรเครดิตรั่วไหล"],
        ["P1", "ฟีเจอร์หลักใช้งานไม่ได้ตามที่ออกแบบ แต่ยังมีทางเลี่ยง", "Resend OTP ไม่ทำงาน แต่ยัง Login รอบแรกได้"],
        ["P2", "บั๊กที่กระทบ UX แต่ไม่ block การใช้งานหลัก", "ข้อความ error ไม่ชัดเจน"],
        ["P3", "ปัญหาเล็กน้อย/ความสวยงาม", "จัดวาง UI เพี้ยนเล็กน้อย"],
    ]
    for row_i, d in enumerate(defs, start=2):
        for col_i, val in enumerate(d, start=1):
            c = ws.cell(row=row_i, column=col_i, value=val)
            if col_i == 1:
                c.fill = PatternFill(start_color=PRIORITY_COLORS[val], end_color=PRIORITY_COLORS[val], fill_type="solid")
    _autosize(ws, [10, 55, 45])
    return ws


def _build_glossary(wb):
    """คำศัพท์ทั่วไปของ QA Pipeline นี้เท่านั้น (ใช้ได้ทุก Feature) — ไม่ใส่คำที่ไม่เกี่ยวกับ Pipeline นี้
    โดยตรง (เช่น OTP, RTM เคยอยู่ในเวอร์ชันก่อนหน้าแต่ถูกตัดออกเพราะไม่ปรากฏการใช้งานจริงในเอกสาร/
    ชีตไหนของ Workbook เลย ใส่ไว้จะเสี่ยงทำให้คนอ่านเข้าใจผิดว่าฟีเจอร์เกี่ยวข้องกับคำนั้น) ถ้า Feature
    ไหนมีศัพท์เฉพาะเพิ่มเติมนอกเหนือจากนี้ ให้ต่อท้ายรายการนี้ได้ แต่ห้ามลบของเดิมออก"""
    ws = wb.create_sheet("Glossary")
    ws.append(["คำศัพท์ / รหัส", "ความหมาย"])
    _style_header_row(ws, 1, 2)
    entries = [
        ["P0-P3", "ระดับความรุนแรง/ความสำคัญ ดูรายละเอียดที่ชีต Priority & Risk Matrix"],
        ["REQ-F-xxx", "Functional Requirement — ความต้องการเชิงฟังก์ชันที่ระบบต้องทำได้ ระบุไว้ใน 01-requirement-review.md"],
        ["REQ-NF-xxx", "Non-Functional Requirement — ความต้องการเชิงคุณภาพที่ไม่ใช่ฟีเจอร์ตรงๆ เช่น Security, Reliability, Usability ระบุไว้ใน 01-requirement-review.md"],
        ["BR-xxx", "Business Rule — กฎทางธุรกิจที่ระบบต้องยึดตามเสมอ ระบุไว้ใน 01-requirement-review.md"],
        ["AC-xxx", "Acceptance Criteria — เกณฑ์ยอมรับรูปแบบ Given/When/Then ที่ใช้ตัดสินว่า Requirement ข้อนั้นผ่านหรือไม่ ระบุไว้ใน 01-requirement-review.md"],
        ["FLOW-xxx", "หมายเลข Flow ที่ออกแบบไว้ใน 02-e2e-flow.md เช่น Happy Path, Alternate Path, Error Path"],
        ["DP-xxx", "Decision Point — จุดตัดสินใจในผังงาน (Flow) ที่ระบบต้องเลือกเส้นทางถัดไปตามเงื่อนไข ระบุไว้ใน 02-e2e-flow.md"],
        ["RISK-xxx", "ความเสี่ยงที่พบระหว่างการวิเคราะห์ Requirement/Flow พร้อมระดับความรุนแรง (High/Medium/Low) ระบุไว้ใน 01-requirement-review.md หรือ 02-e2e-flow.md"],
        ["TC-xxx", "Test Case — รหัสของ Test Case แต่ละรายการในชีต Test Case (เรียงตามลำดับต่อเนื่องภายใน Feature เดียวกัน)"],
    ]
    for e in entries:
        ws.append(e)
    _autosize(ws, [24, 60])
    return ws


def _build_test_case_sheet(wb):
    ws = wb.create_sheet("Test Case")
    for i, h in enumerate(TC_COLUMNS, start=1):
        ws.cell(row=1, column=i, value=h)
    _style_header_row(ws, 1, len(TC_COLUMNS))
    _autosize(ws, [12, 18, 25, 12, 10, 40, 30, 70, 60, 45, 45, 14, 35, 12, 14, 45, 71])

    max_row = 2000
    dv_type = DataValidation(type="list", formula1=f'"{",".join(TEST_TYPE_OPTIONS)}"', allow_blank=True)
    dv_priority = DataValidation(type="list", formula1=f'"{",".join(PRIORITY_OPTIONS)}"', allow_blank=True)
    dv_status = DataValidation(type="list", formula1=f'"{",".join(STATUS_OPTIONS)}"', allow_blank=True)
    ws.add_data_validation(dv_type)
    ws.add_data_validation(dv_priority)
    ws.add_data_validation(dv_status)
    dv_type.add(f"D2:D{max_row}")
    dv_priority.add(f"E2:E{max_row}")
    dv_status.add(f"L2:L{max_row}")
    return ws


def create_workbook(feature_name, path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    _build_dashboard(wb)
    _build_document_control(wb, feature_name)
    _build_requirement_matrix(wb)
    _build_env_config(wb)
    _build_priority_risk_matrix(wb)
    _build_glossary(wb)
    _build_test_case_sheet(wb)
    wb.save(path)
    _finalize_layout(path)
    return path


# ---------------------------------------------------------------------------
# Document Control versioning
# ---------------------------------------------------------------------------

def bump_version(path, editor, note):
    wb = openpyxl.load_workbook(path)
    ws = wb["Document Control"]
    current = ws["B4"].value or 1
    new_version = int(current) + 1
    ws["B4"] = new_version
    ws["B5"] = datetime.date.today().isoformat()

    # find first empty row after header (row 7) in history table
    r = 8
    while ws.cell(row=r, column=1).value not in (None, ""):
        r += 1
    ws.cell(row=r, column=1, value=new_version)
    ws.cell(row=r, column=2, value=datetime.date.today().isoformat())
    ws.cell(row=r, column=3, value=editor)
    ws.cell(row=r, column=4, value=note)
    wb.save(path)
    return new_version


# ---------------------------------------------------------------------------
# Test Case row operations
# ---------------------------------------------------------------------------

def _apply_row_colors(ws, row_idx, values_by_col):
    if values_by_col.get("Test Type") in TEST_TYPE_COLORS:
        color = TEST_TYPE_COLORS[values_by_col["Test Type"]]
        ws.cell(row=row_idx, column=4).fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    if values_by_col.get("Priority") in PRIORITY_COLORS:
        color = PRIORITY_COLORS[values_by_col["Priority"]]
        cell = ws.cell(row=row_idx, column=5)
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        if values_by_col["Priority"] == "P0":
            cell.font = Font(color="FFFFFF", bold=True)
    status = values_by_col.get("Status", "not start")
    if status in STATUS_COLORS:
        color = STATUS_COLORS[status]
        ws.cell(row=row_idx, column=12).fill = PatternFill(start_color=color, end_color=color, fill_type="solid")


def add_test_cases(path, cases, editor="test-case-generator", note="เพิ่ม Test Case"):
    """cases: list[dict] โดยแต่ละ dict มี key ตรงกับ TC_COLUMNS (key ที่ไม่ระบุจะเว้นว่าง)

    Test Step / Test Data จะถูกแยกบรรทัดอัตโนมัติ (ดู _split_test_step / _split_test_data) —
    เขียนเป็นข้อความปกติ "1) ... 2) ..." หรือ "key1=val1, key2=val2" มาได้เลย ไม่ต้องใส่ \\n เอง
    """
    wb = openpyxl.load_workbook(path)
    ws = wb["Test Case"]
    last_row = ws.max_row
    while last_row > 1 and all(ws.cell(row=last_row, column=c).value in (None, "") for c in range(1, len(TC_COLUMNS) + 1)):
        last_row -= 1

    for offset, case in enumerate(cases, start=1):
        r = last_row + offset
        case.setdefault("Status", "not start")
        for c, col_name in enumerate(TC_COLUMNS, start=1):
            value = case.get(col_name, "")
            if col_name == "Test Step":
                value = _split_test_step(value)
            elif col_name == "Test Data":
                value = _split_test_data(value)
            value = _normalize_quotes(value)
            ws.cell(row=r, column=c, value=value)
        _apply_row_colors(ws, r, case)
    wb.save(path)
    _finalize_layout(path)
    new_version = bump_version(path, editor, note)
    return {"added": len(cases), "version": new_version}


def read_test_cases(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Test Case"]
    rows = []
    for r in range(2, ws.max_row + 1):
        vals = [ws.cell(row=r, column=c).value for c in range(1, len(TC_COLUMNS) + 1)]
        if not any(vals):
            continue
        rows.append(dict(zip(TC_COLUMNS, vals)))
    return rows


def _resolve_photo_path(workbook_path, value):
    """แปลง path รูป (มักเป็น relative path เช่น 'screenshots/Chromium/TC-017.png') ให้เป็น absolute
    path ที่เปิดไฟล์ได้จริง — ลองเทียบกับโฟลเดอร์ของ Workbook เองก่อน (กรณีสคริปต์ที่เรียกอยู่คนละ
    working directory กับ Workbook) แล้วค่อย fallback ไปเทียบกับ working directory ปัจจุบัน
    """
    if not isinstance(value, str) or not value:
        return None
    if os.path.isabs(value):
        return value if os.path.isfile(value) else None
    wb_dir = os.path.dirname(os.path.abspath(workbook_path))
    candidate = os.path.join(wb_dir, value)
    if os.path.isfile(candidate):
        return candidate
    candidate_cwd = os.path.abspath(value)
    if os.path.isfile(candidate_cwd):
        return candidate_cwd
    return None


def update_fields_batch(path, updates, editor="risk-analysis", note="อัปเดตหลาย Test Case พร้อมกัน"):
    """updates: list[dict] แต่ละ dict มี keys: tc_id, field, value
    ใช้เมื่อต้องแก้ไขหลาย Test Case ในรอบเดียว (เช่น risk-analysis กำหนด Priority ให้ทุกแถว)
    เพื่อให้ bump Version แค่ครั้งเดียวต่อรอบ แทนที่จะ bump ทีละแถว (ป้องกัน Document Control History ท่วมด้วยบรรทัดย่อยจำนวนมาก)
    """
    wb = openpyxl.load_workbook(path)
    ws = wb["Test Case"]
    col_idx = TC_COLUMNS.index("Test Case ID") + 1
    id_to_row = {}
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=col_idx).value
        if v:
            id_to_row[v] = r

    not_found = []
    applied = 0
    for u in updates:
        tc_id, field, value = u["tc_id"], u["field"], u["value"]
        if field not in TC_COLUMNS:
            raise ValueError(f"Unknown field: {field}")
        if tc_id not in id_to_row:
            not_found.append(tc_id)
            continue
        r = id_to_row[tc_id]
        target_col = TC_COLUMNS.index(field) + 1
        if field == PHOTO_COLUMN:
            if not value:
                # value ว่างเปล่า = ตั้งใจลบรูปเดิมออก (เช่น qa-retest เปลี่ยนผลจาก Fail เป็น Pass แล้ว)
                _remove_photo_at(ws, r, target_col)
            else:
                resolved = _resolve_photo_path(path, value)
                embedded = _embed_photo(ws, r, target_col, resolved) if resolved else False
                if not embedded:
                    # หาไฟล์รูปไม่เจอ (path ผิด/ยังไม่มีไฟล์จริง) — fallback เขียน path เป็นข้อความแทน
                    # ไม่ให้ข้อมูลหายไปเงียบๆ
                    ws.cell(row=r, column=target_col, value=_normalize_quotes(value))
        elif field == "Test Step":
            value = _split_test_step(value)
            ws.cell(row=r, column=target_col, value=_normalize_quotes(value))
        elif field == "Test Data":
            value = _split_test_data(value)
            ws.cell(row=r, column=target_col, value=_normalize_quotes(value))
        else:
            ws.cell(row=r, column=target_col, value=_normalize_quotes(value))
        row_vals = {c: ws.cell(row=r, column=i + 1).value for i, c in enumerate(TC_COLUMNS)}
        _apply_row_colors(ws, r, row_vals)
        applied += 1

    wb.save(path)
    _finalize_layout(path)
    new_version = bump_version(path, editor, note)
    return {"applied": applied, "not_found": not_found, "version": new_version}


def update_field(path, tc_id, field, value, editor="risk-analysis", note=None):
    if field not in TC_COLUMNS:
        raise ValueError(f"Unknown field: {field}")
    wb = openpyxl.load_workbook(path)
    ws = wb["Test Case"]
    col_idx = TC_COLUMNS.index("Test Case ID") + 1
    target_col = TC_COLUMNS.index(field) + 1
    found = False
    for r in range(2, ws.max_row + 1):
        if ws.cell(row=r, column=col_idx).value == tc_id:
            if field == PHOTO_COLUMN:
                if not value:
                    _remove_photo_at(ws, r, target_col)
                else:
                    resolved = _resolve_photo_path(path, value)
                    embedded = _embed_photo(ws, r, target_col, resolved) if resolved else False
                    if not embedded:
                        ws.cell(row=r, column=target_col, value=_normalize_quotes(value))
            else:
                if field == "Test Step":
                    value = _split_test_step(value)
                elif field == "Test Data":
                    value = _split_test_data(value)
                value = _normalize_quotes(value)
                ws.cell(row=r, column=target_col, value=value)
            row_vals = {c: ws.cell(row=r, column=i + 1).value for i, c in enumerate(TC_COLUMNS)}
            _apply_row_colors(ws, r, row_vals)
            found = True
            break
    if not found:
        raise ValueError(f"Test Case ID not found: {tc_id}")
    wb.save(path)
    _finalize_layout(path)
    new_version = bump_version(path, editor, note or f"อัปเดต {field} ของ {tc_id} เป็น {value}")
    return {"updated": tc_id, "field": field, "value": value, "version": new_version}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    c1 = sub.add_parser("create")
    c1.add_argument("--feature", required=True)
    c1.add_argument("--out", required=True)

    c2 = sub.add_parser("add-cases")
    c2.add_argument("--path", required=True)
    c2.add_argument("--cases-json", required=True)
    c2.add_argument("--editor", default="test-case-generator")
    c2.add_argument("--note", default="เพิ่ม Test Case")

    c3 = sub.add_parser("bump")
    c3.add_argument("--path", required=True)
    c3.add_argument("--editor", required=True)
    c3.add_argument("--note", required=True)

    c4 = sub.add_parser("read-cases")
    c4.add_argument("--path", required=True)

    c5 = sub.add_parser("update-field")
    c5.add_argument("--path", required=True)
    c5.add_argument("--tc-id", required=True)
    c5.add_argument("--field", required=True)
    c5.add_argument("--value", required=True)
    c5.add_argument("--editor", required=True)
    c5.add_argument("--note", default=None)

    c6 = sub.add_parser("update-fields-batch")
    c6.add_argument("--path", required=True)
    c6.add_argument("--updates-json", required=True, help="path ไปยังไฟล์ .json ที่มี list ของ {tc_id, field, value}")
    c6.add_argument("--editor", required=True)
    c6.add_argument("--note", required=True)

    c7 = sub.add_parser("finalize-layout")
    c7.add_argument("--path", required=True)

    args = p.parse_args()

    if args.cmd == "create":
        out = create_workbook(args.feature, args.out)
        print(json.dumps({"created": out}))
    elif args.cmd == "add-cases":
        with open(args.cases_json, encoding="utf-8") as f:
            cases = json.load(f)
        result = add_test_cases(args.path, cases, args.editor, args.note)
        print(json.dumps(result, ensure_ascii=False))
    elif args.cmd == "bump":
        v = bump_version(args.path, args.editor, args.note)
        print(json.dumps({"version": v}))
    elif args.cmd == "read-cases":
        print(json.dumps(read_test_cases(args.path), ensure_ascii=False, indent=2))
    elif args.cmd == "update-field":
        result = update_field(args.path, args.tc_id, args.field, args.value, args.editor, args.note)
        print(json.dumps(result, ensure_ascii=False))
    elif args.cmd == "update-fields-batch":
        with open(args.updates_json, encoding="utf-8") as f:
            updates = json.load(f)
        result = update_fields_batch(args.path, updates, args.editor, args.note)
        print(json.dumps(result, ensure_ascii=False))
    elif args.cmd == "finalize-layout":
        _finalize_layout(args.path)
        print(json.dumps({"finalized": args.path}))


if __name__ == "__main__":
    main()
