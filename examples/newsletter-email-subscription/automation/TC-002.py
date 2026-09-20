"""TC-002: กรอกอีเมลรูปแบบไม่ถูกต้อง (ไม่มี @)"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill("newuserexample.com")
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดง error ใดๆ ภายใน 5 วินาทีสำหรับอีเมลที่ไม่มี @: {e}", "#newsletter-email")

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "error" not in classes:
        raise AssertionError(
            f"คาดว่าจะเห็น error แบบ inline แต่ได้ class='{classes}' ข้อความ='{text}'",
            "#newsletter-email",
        )
    if "กรุณากรอกอีเมลให้ถูกต้อง" not in text:
        raise AssertionError(f"ข้อความ error ไม่ตรงตามที่คาดหวัง: '{text}'", "#newsletter-email")

    state = requests.get(f"{base_url}/__test__/state", timeout=5).json()
    if state["subscribers"]:
        raise AssertionError("ไม่ควรมีการบันทึกข้อมูลลง subscriber แต่พบข้อมูลถูกบันทึก", "#newsletter-email")

    return {
        "passed": True,
        "actual_result": f"ระบบแสดง error '{text}' แบบ inline และไม่มีการบันทึกข้อมูล",
        "highlight_selector": "#newsletter-email",
    }
