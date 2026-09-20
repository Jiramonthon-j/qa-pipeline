"""TC-001: สมัครรับข่าวสารสำเร็จด้วยอีเมลรูปแบบถูกต้องที่ยังไม่เคยสมัคร"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill("newuser01@example.com")
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดงผลลัพธ์ใดๆ ใต้ปุ่มภายใน 5 วินาที: {e}", "#newsletter-message")

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "success" not in classes:
        raise AssertionError(
            f"คาดว่าจะเห็นข้อความสำเร็จแบบ inline แต่ได้ class='{classes}' ข้อความ='{text}'",
            "#newsletter-message",
        )
    if "สมัครรับข่าวสารสำเร็จ" not in text:
        raise AssertionError(f"ข้อความสำเร็จไม่ตรงตามที่คาดหวัง: '{text}'", "#newsletter-message")

    return {
        "passed": True,
        "actual_result": f"ระบบแสดงข้อความ '{text}' แบบ inline ใต้ปุ่ม และบันทึกอีเมลลง subscriber สำเร็จ",
        "highlight_selector": "#newsletter-message",
    }
