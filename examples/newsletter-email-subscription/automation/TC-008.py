"""TC-008: กรอกอีเมลที่มีช่องว่างนำหน้า/ตามหลัง — ระบบควร trim ก่อนตรวจรูปแบบและควรสมัครสำเร็จ"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill(" spaced01@example.com ")
    submit_btn.click()

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดงผลลัพธ์ใดๆ ภายใน 5 วินาที: {e}", "#newsletter-email")

    text = message_el.text_content().strip()
    classes = message_el.get_attribute("class") or ""

    if "success" not in classes:
        raise AssertionError(
            (
                "คาดว่าระบบจะ trim ช่องว่างนำหน้า/ตามหลังก่อนตรวจรูปแบบ แล้วสมัครสำเร็จเหมือนอีเมลปกติที่ถูกต้อง "
                f"แต่ได้ class='{classes}' ข้อความ='{text}' แทน (ไม่ถือว่าเป็นรูปแบบผิดหรือบันทึกอีเมลที่มีช่องว่างติดไปด้วย)"
            ),
            "#newsletter-message",
        )

    state = requests.get(f"{base_url}/__test__/state", timeout=5).json()
    if "spaced01@example.com" not in state["subscribers"]:
        raise AssertionError(
            f"คาดว่าอีเมลที่บันทึกควรถูก trim เป็น 'spaced01@example.com' แต่พบข้อมูลจริงใน subscriber: {state['subscribers']}",
            "#newsletter-message",
        )

    return {
        "passed": True,
        "actual_result": f"ระบบ trim ช่องว่างก่อนตรวจรูปแบบ แสดงข้อความ '{text}' และบันทึกอีเมลแบบ trim แล้วถูกต้อง",
        "highlight_selector": "#newsletter-message",
    }
