"""TC-004: สมัครซ้ำด้วยอีเมลเดิมทุกตัวอักษร (exact match)
Pre-condition: อีเมล dup01@example.com เคยสมัครสำเร็จไปแล้วในระบบ (seed ผ่าน /__test__/seed
ตามวิธีที่ระบุใน 06-test-data.md — ใช้ endpoint ทดสอบแทนการรัน UI ซ้ำเพื่อความเสถียรของ Automation)
"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)
    requests.post(f"{base_url}/__test__/seed", json={"email": "dup01@example.com"}, timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill("dup01@example.com")
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดง error ใดๆ ภายใน 5 วินาทีสำหรับอีเมลที่สมัครซ้ำ (exact match): {e}", "#newsletter-email")

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "error" not in classes:
        raise AssertionError(
            f"คาดว่าจะเห็น error แบบ inline แต่ได้ class='{classes}' ข้อความ='{text}'",
            "#newsletter-email",
        )
    if "สมัครรับข่าวสารไปแล้ว" not in text:
        raise AssertionError(f"ข้อความ error ไม่ตรงตามที่คาดหวัง: '{text}'", "#newsletter-email")

    return {
        "passed": True,
        "actual_result": f"ระบบแสดง error '{text}' แบบ inline และไม่ยอมให้สมัครซ้ำด้วยอีเมลเดิมทุกตัวอักษร",
        "highlight_selector": "#newsletter-email",
    }
