"""TC-006: กดปุ่ม "สมัครรับข่าวสาร" ซ้ำระหว่างระบบกำลังประมวลผล
ใช้ page.route หน่วงเวลาตอบกลับของ /api/subscribe เทียมๆ เพื่อจำลอง "ช่วงกำลังประมวลผล" ให้นานพอ
สำหรับทดสอบว่า UI ป้องกันการกดซ้ำได้จริง (ไม่ใช่แค่บังเอิญเร็วจนกดซ้ำไม่ทัน)
"""
import time


def run(page, base_url):
    import requests
    requests.post(f"{base_url}/__test__/reset", timeout=5)

    def delayed_route(route):
        time.sleep(1.2)
        route.continue_()

    page.route("**/api/subscribe", delayed_route)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill("nodouble01@example.com")
    submit_btn.click()

    # ทันทีหลังกดครั้งแรก (ระหว่างที่ response ยังถูกหน่วงอยู่) ปุ่มต้อง disable ทันที
    if not submit_btn.is_disabled():
        raise AssertionError(
            "คาดว่าปุ่ม 'สมัครรับข่าวสาร' จะ disable ทันทีหลังกดครั้งแรกระหว่างรอผลลัพธ์ แต่ปุ่มยังกดได้อยู่",
            "#newsletter-submit",
        )

    # พยายามกดซ้ำระหว่างปุ่ม disable อยู่ — ต้องไม่ทำให้มีการยิง request ที่สองออกไป
    try:
        submit_btn.click(timeout=500, force=True)
    except Exception:
        pass  # คาดว่าจะกดไม่ติดเพราะปุ่ม disabled อยู่ ถือเป็นพฤติกรรมที่ถูกต้อง

    try:
        page.wait_for_function(
            "document.getElementById('newsletter-message').textContent.trim().length > 0",
            timeout=5000,
        )
    except Exception as e:
        raise AssertionError(f"ระบบไม่แสดงผลลัพธ์ใดๆ หลังประมวลผลเสร็จภายใน 5 วินาที: {e}", "#newsletter-message")

    state = requests.get(f"{base_url}/__test__/state", timeout=5).json()
    if len(state["subscribers"]) != 1:
        raise AssertionError(
            f"คาดว่าจะมีการบันทึกอีเมลเพียง 1 ครั้งแม้กดปุ่มซ้ำ แต่พบข้อมูลใน subscriber {len(state['subscribers'])} รายการ: {state['subscribers']}",
            "#newsletter-submit",
        )

    if submit_btn.is_disabled():
        raise AssertionError("หลังได้รับผลลัพธ์แล้ว ปุ่มควรกลับมากดได้ตามปกติ แต่ยังคง disabled อยู่", "#newsletter-submit")

    return {
        "passed": True,
        "actual_result": "ปุ่ม disable ทันทีหลังกดครั้งแรก ไม่มีคำขอสมัครซ้ำถูกส่งออกไป และปุ่มกลับมาใช้งานได้หลังได้ผลลัพธ์",
        "highlight_selector": "#newsletter-submit",
    }
