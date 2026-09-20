"""TC-005: สมัครซ้ำด้วยอีเมลเดิมแต่ตัวพิมพ์เล็ก-ใหญ่ต่างกัน
Pre-condition: อีเมล dup02@example.com (ตัวพิมพ์เล็กทั้งหมด) เคยสมัครสำเร็จไปแล้วในระบบ

หมายเหตุ: Expected Result ของเคสนี้อ้างอิงตาม RISK-001 (สมมติฐานพฤติกรรมที่ผู้ใช้ทั่วไปคาดหวัง —
case-insensitive) ซึ่งขัดกับ BR-002 ที่ระบุพฤติกรรมปัจจุบันของระบบไว้ตามตัวอักษร (exact-match/
case-sensitive) โดยตั้งใจ ตามที่ยืนยันไว้แล้วใน 04-coverage-review.md — เคสนี้จึงมีโอกาสสูงที่จะ
Fail จริงเมื่อรันกับระบบปัจจุบัน ซึ่งเป็นผลลัพธ์ที่คาดหวังไว้แล้ว (ไม่ใช่ข้อผิดพลาดของ Automation Script)
"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)
    requests.post(f"{base_url}/__test__/seed", json={"email": "dup02@example.com"}, timeout=5)

    page.goto(base_url)
    page.locator(".newsletter-widget").scroll_into_view_if_needed()
    email_input = page.locator("#newsletter-email")
    submit_btn = page.locator("#newsletter-submit")
    message_el = page.locator("#newsletter-message")

    email_input.fill("Dup02@Example.com")
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

    # Expected (ตาม RISK-001 / ความคาดหวังผู้ใช้ทั่วไป): ควรถือว่าเป็นอีเมลเดียวกัน (case-insensitive)
    # และต้องแสดง error "สมัครรับข่าวสารไปแล้ว" เหมือน TC-004
    if "error" not in classes or "สมัครรับข่าวสารไปแล้ว" not in text:
        raise AssertionError(
            (
                "ระบบควรถือว่า 'Dup02@Example.com' เป็นอีเมลเดียวกับ 'dup02@example.com' ที่สมัครไปแล้ว "
                "(case-insensitive ตามความคาดหวังผู้ใช้ทั่วไป และตาม RISK-001) และแสดง error "
                f"'สมัครรับข่าวสารไปแล้ว' แต่ระบบกลับแสดง class='{classes}' ข้อความ='{text}' "
                "แทน — สอดคล้องกับ BR-002 ที่ระบุพฤติกรรมปัจจุบันเป็น exact-match (case-sensitive) "
                "ซึ่งเป็นบั๊กเชิงคุณภาพข้อมูลตาม RISK-001 (High)"
            ),
            "#newsletter-message",
        )

    return {
        "passed": True,
        "actual_result": f"ระบบแสดง error '{text}' แบบ inline และปฏิบัติกับอีเมลแบบ case-insensitive ถูกต้อง",
        "highlight_selector": "#newsletter-message",
    }
