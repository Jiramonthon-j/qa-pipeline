"""TC-010: ตรวจสอบว่า Footer widget แสดงผลและทำงานถูกต้องข้าม Browser หลัก
รันซ้ำ TC-001 (happy path) บน Browser ที่ระบุใน Env & Config — runner กลาง (run_automation.py)
เป็นผู้วน loop เรียกสคริปต์นี้ครั้งละ 1 Browser ตาม --browser ที่ส่งเข้ามา สคริปต์นี้จึงตรวจสอบ
เฉพาะ "widget แสดงผลและทำงานถูกต้อง" ในบราวเซอร์ปัจจุบันที่กำลังรันอยู่เท่านั้น
"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()

    # ตรวจสอบว่า widget แสดงผลครบองค์ประกอบก่อน (heading, input, button)
    heading = page.locator(".newsletter-widget h3")
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    if not heading.is_visible() or not email_input.is_visible() or not submit_btn.is_visible():
        raise AssertionError("Footer widget แสดงผลไม่ครบ (heading/input/button) ใน Browser นี้", ".newsletter-widget")

    email_input.fill("crossbrowser01@example.com")
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดงผลลัพธ์ใดๆ ภายใน 5 วินาทีใน Browser นี้: {e}", "#newsletter-message")

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "success" not in classes:
        raise AssertionError(
            f"คาดว่า TC-001 (happy path) จะสำเร็จใน Browser นี้เช่นกัน แต่ได้ class='{classes}' ข้อความ='{text}'",
            "#newsletter-message",
        )

    return {
        "passed": True,
        "actual_result": f"Footer widget แสดงผลครบและทำงานถูกต้องใน Browser นี้ — ข้อความที่ได้: '{text}'",
        "highlight_selector": "#newsletter-message",
    }
