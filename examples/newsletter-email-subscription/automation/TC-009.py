"""TC-009: กรอกอีเมลที่ยาวผิดปกติ (local-part ~250 ตัวอักษร) — ต้องไม่ error/crash และแสดง error
รูปแบบไม่ถูกต้องตามมาตรฐาน RFC (local-part ไม่เกิน 64 ตัวอักษร)
ตาม 06-test-data.md ให้ generate สตริงตอนรัน ไม่ hardcode ในเอกสาร
"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    long_email = ("a" * 250) + "@example.com"

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill(long_email)
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(
            f"ระบบไม่แสดงผลลัพธ์ใดๆ ภายใน 5 วินาที (อาจค้าง/crash) สำหรับอีเมลยาวผิดปกติ: {e}",
            "#newsletter-email",
        )

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "error" not in classes or "กรุณากรอกอีเมลให้ถูกต้อง" not in text:
        raise AssertionError(
            f"คาดว่าจะเห็น error รูปแบบไม่ถูกต้องแบบ inline (local-part เกิน 64 ตัวอักษรตาม RFC) แต่ได้ class='{classes}' ข้อความ='{text}'",
            "#newsletter-email",
        )

    return {
        "passed": True,
        "actual_result": f"ระบบจัดการอีเมลยาวผิดปกติได้โดยไม่ error/crash และแสดง '{text}' ตามมาตรฐาน RFC (local-part ไม่เกิน 64 ตัวอักษร)",
        "highlight_selector": "#newsletter-email",
    }
