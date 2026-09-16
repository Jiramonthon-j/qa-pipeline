#!/usr/bin/env python3
"""
run_automation.py — runner กลางสำหรับ qa-automation-script (Skill 06a)

รันไฟล์ automation/<TC ID>.py ทีละไฟล์ด้วย Playwright จริง, ถ่ายภาพหน้าจอ + วาดไฮไลท์,
สแกน Accessibility ด้วย axe-core, แยก Fail จริง vs Script/Environment Error (Blocked),
แล้ว print ผลรวมเป็น JSON (ให้ skill เรียกต่อด้วย qa_workbook.py update-fields-batch)

วิธีใช้:
  python3 run_automation.py --automation-dir "<Feature>/automation" \
      --base-url "http://localhost:8931" \
      --screenshots-dir "<Feature>/screenshots/chromium" \
      --browser chromium \
      --tc TC-001 TC-002 TC-003   (ไม่ใส่ --tc = รันทุกไฟล์ในโฟลเดอร์)
"""
import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

try:
    from axe_playwright_python.sync_playwright import Axe
except ImportError:
    Axe = None


def load_tc_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def draw_highlight(screenshot_path, box, color):
    if not box:
        return
    img = Image.open(screenshot_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    pad = 8
    x0, y0 = box["x"] - pad, box["y"] - pad
    x1, y1 = box["x"] + box["width"] + pad, box["y"] + box["height"] + pad
    draw.ellipse([x0, y0, x1, y1], outline=color, width=4)
    img.save(screenshot_path)


def run_one(page, base_url, mod, screenshot_path, axe, tc_id=None):
    result = {"status": None, "actual_result": "", "remarks": "", "a11y_issues": []}
    try:
        r = mod.run(page, base_url)
        result["status"] = "Pass" if r.get("passed") else "Fail"
        result["actual_result"] = r.get("actual_result", "")
        highlight_selector = r.get("highlight_selector")

        # หมายเหตุ: ต้องรัน axe scan ให้เสร็จ (ซึ่งอาจ downgrade Pass -> Fail) ก่อนค่อยตัดสินใจสีวงไฮไลท์
        # และก่อนถ่ายภาพ/วาดภาพ — ถ้าวาดวงไฮไลท์ตามสถานะ "ก่อน" ผลสแกน a11y จะได้วงสีเขียว (ดูเหมือน Pass)
        # ทั้งที่ผลสุดท้ายเป็น Fail จาก a11y ซึ่งจะทำให้หลักฐานภาพสื่อผิด (พบบั๊กนี้จริงระหว่างทดสอบ Skill)
        if axe is not None:
            axe_results = axe.run(page)
            violations = axe_results.response.get("violations", [])
            if violations:
                # axe-core ให้ระดับ impact มาเสมอ: critical/serious/moderate/minor
                # critical+serious = กระทบผู้ใช้จริง เทียบเท่าบั๊ก functional -> downgrade ได้
                # moderate/minor = ข้อสังเกต best-practice ทั่วไป (เช่น ไม่มี <main> landmark)
                # ที่หน้าเว็บทั่วไปมักติดอยู่แล้วโดยไม่เกี่ยวกับ Test Case นี้เลย -> ห้าม downgrade
                # (พบจริงระหว่างทดสอบ Skill นี้ — ดู BUG-09 ใน Test Report: ถ้าไม่กรอง severity
                # ทุก Test Case จะถูกเปลี่ยนเป็น Fail หมดเพราะ noise ระดับ moderate)
                blocking = [v for v in violations if v.get("impact") in ("critical", "serious")]
                nonblocking = [v for v in violations if v.get("impact") not in ("critical", "serious")]
                all_issues = [f"{v['id']} ({v.get('impact')}): {v['help']}" for v in violations]
                result["a11y_issues"] = all_issues

                if blocking:
                    blocking_issues = [f"{v['id']} ({v.get('impact')}): {v['help']}" for v in blocking]
                    if result["status"] == "Pass":
                        result["status"] = "Fail"
                        result["remarks"] = "Functional ผ่าน แต่พบปัญหา Accessibility ระดับ critical/serious: " + "; ".join(blocking_issues)
                    else:
                        result["remarks"] = (result["remarks"] + " | " if result["remarks"] else "") + \
                            "พบปัญหา Accessibility ระดับ critical/serious เพิ่มเติม: " + "; ".join(blocking_issues)

                if nonblocking:
                    nonblocking_issues = [f"{v['id']} ({v.get('impact')}): {v['help']}" for v in nonblocking]
                    note = "พบข้อสังเกต Accessibility ระดับ moderate/minor (ไม่กระทบ Status): " + "; ".join(nonblocking_issues)
                    result["remarks"] = (result["remarks"] + " | " if result["remarks"] else "") + note

        # ถ่ายภาพ + วาดวงไฮไลท์หลังทราบสถานะสุดท้าย (รวมผลจาก a11y scan แล้ว) เพื่อให้สีวงตรงกับ Status จริง
        page.screenshot(path=str(screenshot_path))
        box = None
        if highlight_selector:
            try:
                box = page.locator(highlight_selector).first.bounding_box()
            except Exception:
                box = None
        color = "green" if result["status"] == "Pass" else "red"
        draw_highlight(screenshot_path, box, color)

    except AssertionError as e:
        # convention: raise AssertionError("message") หรือ raise AssertionError("message", "#selector") —
        # ทุก Test Case ควรระบุ selector ที่มีความหมายเสมอ (แม้จุดที่ผิดจริงจะเป็นสถานะฝั่ง backend ที่ไม่
        # แสดงผลบนหน้าจอ ก็ยังเลือก element ที่เกี่ยวข้องที่สุด ณ ตอนตรวจสอบมาวงไว้ ดีกว่าไม่มีวงเลย) —
        # ไม่ใส่ selector ก็ยังรันได้ (จะไม่มีวงไฮไลท์) แต่ควรเลี่ยงถ้าเป็นไปได้
        msg = e.args[0] if e.args else str(e)
        selector = e.args[1] if len(e.args) > 1 else None
        result["status"] = "Fail"
        result["actual_result"] = str(msg)
        result["remarks"] = f"Test Case Fail จริง: {msg}"
        try:
            page.screenshot(path=str(screenshot_path))
            box = None
            if selector:
                try:
                    box = page.locator(selector).first.bounding_box()
                except Exception:
                    box = None
            draw_highlight(screenshot_path, box, "red")
        except Exception:
            pass
    except Exception as e:
        # convention: raise RuntimeError("message") หรือ raise RuntimeError("message", "#selector") — ใช้
        # เหมือนกันกับ AssertionError (ดู comment ด้านบน) สำหรับ Test Case ที่จงใจ raise Exception ธรรมดา
        # (ไม่ใช่ AssertionError) เพื่อให้ runner ตั้ง Status เป็น Blocked แทนการเดา Pass/Fail (เช่น
        # TC-009/TC-021 ที่ Expected Result ขึ้นกับ Open Question ที่ยังไม่มีคำตอบ) — วงไฮไลท์สีส้ม
        # (ไม่ใช่เขียว/แดง) ให้ต่างจาก Pass/Fail ชัดเจนว่านี่คือ Blocked ไม่ใช่ผลตัดสินจริง
        # ใช้ e.args[0] เป็นข้อความเสมอ (ไม่ใช่ str(e) ตรงๆ) เพราะพอ exception มี 2 args (message, selector)
        # str(e) จะ print ออกมาเป็น repr ของทั้ง tuple (เช่น "('ข้อความ...', '#selector')") ซึ่งดูแปลกและ
        # เอา selector ที่เป็นรายละเอียดภายในไปปนกับข้อความที่ควรอ่านง่ายสำหรับ Actual Result/Remarks
        msg = e.args[0] if e.args else str(e)
        result["status"] = "Blocked"
        result["actual_result"] = f"Script/Environment Error: {type(e).__name__}: {msg}"
        result["remarks"] = f"[SCRIPT/ENV ERROR — ไม่ใช่ Test Case Fail จริง] {type(e).__name__}: {msg}"
        selector = e.args[1] if len(e.args) > 1 else None
        try:
            page.screenshot(path=str(screenshot_path))
            box = None
            if selector:
                try:
                    box = page.locator(selector).first.bounding_box()
                except Exception:
                    box = None
            draw_highlight(screenshot_path, box, "orange")
        except Exception:
            pass

    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--automation-dir", required=True)
    p.add_argument("--base-url", required=True)
    p.add_argument("--screenshots-dir", required=True)
    p.add_argument("--browser", default="chromium")
    p.add_argument("--tc", nargs="*", default=None)
    args = p.parse_args()

    automation_dir = Path(args.automation_dir)
    screenshots_dir = Path(args.screenshots_dir)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    tc_files = sorted(automation_dir.glob("TC-*.py"))
    if args.tc:
        wanted = set(args.tc)
        tc_files = [f for f in tc_files if f.stem in wanted]

    axe = Axe() if Axe is not None else None
    results = {}

    with sync_playwright() as pw:
        browser_launcher = getattr(pw, args.browser)
        browser = browser_launcher.launch()
        for tc_file in tc_files:
            tc_id = tc_file.stem
            mod = load_tc_module(tc_file)
            page = browser.new_page()
            screenshot_path = screenshots_dir / f"{tc_id}.png"
            res = run_one(page, args.base_url, mod, screenshot_path, axe, tc_id=tc_id)
            res["execution_date"] = date.today().isoformat()
            res["screenshot"] = str(screenshot_path)
            results[tc_id] = res
            page.close()
        browser.close()

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
