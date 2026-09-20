"""TC-011: ระบบบันทึกอีเมลลง subscriber ล้มเหลวจากสาเหตุฝั่งระบบเอง (จำลอง subscriber DB unavailable)
เปิด fail-mode ผ่าน endpoint ทดสอบ /__test__/fail-mode (จำลอง environment ตามที่ 06-test-data.md ระบุไว้ว่า
ต้อง mock/stub ที่ระดับ environment ไม่ใช่ค่าที่ป้อนผ่านฟอร์ม) แล้วตรวจว่า UI แสดง error กลางๆ ที่สื่อว่า
ระบบมีปัญหาชั่วคราว ไม่ใช่ error ที่สื่อว่าเป็นความผิดของผู้ใช้ และหน้าเว็บต้องไม่ค้าง/crash
"""
import requests


def run(page, base_url):
    requests.post(f"{base_url}/__test__/reset", timeout=5)
    requests.post(f"{base_url}/__test__/fail-mode", json={"on": True}, timeout=5)

    try:
        page.goto(base_url)
        page.locator(".newsletter-widget").scroll_into_view_if_needed()
        email_input = page.locator("#newsletter-email")
        submit_btn = page.locator("#newsletter-submit")
        message_el = page.locator("#newsletter-message")

        email_input.fill("infrafail01@example.com")
        submit_btn.click()

        try:
            page.wait_for_function(
                "document.getElementById('newsletter-message').textContent.trim().length > 0",
                timeout=5000,
            )
        except Exception as e:
            raise AssertionError(
                f"หน้าเว็บค้าง/ไม่ตอบสนองภายใน 5 วินาทีเมื่อ subscriber DB unavailable: {e}",
                "#newsletter-message",
            )

        text = message_el.text_content().strip()
        classes = message_el.get_attribute("class") or ""

        if "error" not in classes:
            raise AssertionError(
                f"คาดว่าจะเห็น error แบบ inline เมื่อระบบบันทึกล้มเหลว แต่ได้ class='{classes}' ข้อความ='{text}'",
                "#newsletter-message",
            )

        # ต้องเป็น error กลางๆ ของระบบ ไม่ใช่ error ที่สื่อว่าผู้ใช้กรอกผิด (เช่นข้อความของ validation)
        if "กรุณากรอกอีเมลให้ถูกต้อง" in text or "สมัครรับข่าวสารไปแล้ว" in text:
            raise AssertionError(
                f"ข้อความ error ที่แสดง ('{text}') สื่อว่าเป็นความผิดของผู้ใช้ ทั้งที่สาเหตุจริงคือระบบฝั่งเซิร์ฟเวอร์มีปัญหา ทำให้ผู้ใช้เข้าใจผิดได้",
                "#newsletter-message",
            )

        # ตรวจว่าหน้าเว็บยังใช้งานได้ต่อ ไม่ crash — ปุ่มต้องกลับมากดได้
        if submit_btn.is_disabled():
            raise AssertionError("หลังเกิด error ฝั่งระบบแล้ว ปุ่มควรกลับมาใช้งานได้ตามปกติ แต่ยังคง disabled อยู่ (อาจเป็นสัญญาณของหน้าค้าง)", "#newsletter-submit")

        return {
            "passed": True,
            "actual_result": f"ระบบแสดง error กลางๆ '{text}' แบบ inline โดยไม่ค้าง/crash และปุ่มกลับมาใช้งานได้ปกติ",
            "highlight_selector": "#newsletter-message",
        }
    finally:
        # เคลียร์ fail-mode เสมอไม่ว่าผลจะเป็นอย่างไร กันไม่ให้ค้าง fail มาถึง Test Case ถัดไป
        requests.post(f"{base_url}/__test__/fail-mode", json={"on": False}, timeout=5)
