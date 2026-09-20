"""TC-007: กดปุ่มสมัครโดยไม่กรอกอีเมลเลย (ช่องว่าง)"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    # ไม่กรอกอะไรในช่องอีเมลเลย กดปุ่มตรงๆ
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดง error ใดๆ ภายใน 5 วินาทีเมื่อกดปุ่มโดยไม่กรอกอีเมล: {e}", "#newsletter-email")

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "error" not in classes or "กรุณากรอกอีเมลให้ถูกต้อง" not in text:
        raise AssertionError(
            f"คาดว่าจะเห็น error 'กรุณากรอกอีเมลให้ถูกต้อง' แบบ inline แต่ได้ class='{classes}' ข้อความ='{text}'",
            "#newsletter-email",
        )

    return {
        "passed": True,
        "actual_result": f"ระบบแสดง error '{text}' แบบ inline เมื่อกดปุ่มโดยไม่กรอกอีเมล",
        "highlight_selector": "#newsletter-email",
    }
