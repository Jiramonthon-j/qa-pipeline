#!/usr/bin/env python3
"""
server.py — Demo target web app สำหรับ Newsletter Email Subscription
(ใช้เป็นเป้าหมายจริงให้ Playwright Automation ใน Stage 06a รันทดสอบด้วย)

หมายเหตุความโปร่งใส: Env & Config ของฟีเจอร์นี้ระบุ Staging URL เป็น
https://staging.example-shop.test/ ซึ่งเป็น URL สมมติที่ไม่มีอยู่จริง (ตั้งใจให้เป็นแบบนั้น
เพราะเป็นตัวอย่างประกอบ Skill ไม่ใช่ระบบจริง) — ไฟล์นี้จึงเป็น "หน้าเว็บจำลอง" ที่ implement
ตาม Business Rule ใน 01-requirement-review.md จริง เพื่อให้ Automation รันเจอผลจริง (Pass/Fail จริง)
ไม่ใช่ mock ที่ hardcode ผลลัพธ์ไว้ล่วงหน้า

Implement ตาม Business Rule:
  BR-001: อีเมลต้องมีรูปแบบถูกต้อง (มี @ และมีโดเมนตามหลัง) + local-part ต้องไม่เกิน 64
          ตัวอักษรตามมาตรฐาน RFC 5321 (เกินกว่านี้ถือเป็นรูปแบบไม่ถูกต้อง)
  BR-002: เช็คอีเมลซ้ำแบบ case-insensitive (แก้ไขแล้วตาม Redmine Ticket #9 / RISK-001 —
          เดิมเป็น exact-match/case-sensitive ตามการตัดสินใจชั่วคราวใน Slack (SRC-002) ซึ่งเป็น
          บั๊กที่ตั้งใจปลูกไว้ตอนแรกเพื่อให้ TC-005 จับได้ ตอนนี้ Dev แก้ตามที่ QA รายงานแล้ว —
          ดู 10-qa-retest.md สำหรับรายละเอียดการ Retest)
  BR-003: แสดงผลลัพธ์ (success/error) แบบ inline ใต้ปุ่ม ไม่ reload หน้า
  BR-004: ปุ่ม "สมัครรับข่าวสาร" ต้อง disable ทันทีหลังกดครั้งแรกจนกว่าจะได้รับผลลัพธ์
          (ป้องกันกดซ้ำ/double-submit)

Endpoint พิเศษสำหรับ Automation (ไม่ใช่ endpoint ของฟีเจอร์จริง — ใช้จำลอง environment เท่านั้น):
  POST /__test__/reset       — เคลียร์ subscriber ทั้งหมด กลับสู่สถานะเริ่มต้น
  POST /__test__/seed        — เพิ่มอีเมลเข้า subscriber list ตรงๆ (ใช้ pre-seed ก่อนรัน TC-004/TC-005)
  POST /__test__/fail-mode   — เปิด/ปิด "จำลอง subscriber DB unavailable" สำหรับ TC-011 (body: {"on": true/false})
"""
from flask import Flask, request, jsonify, Response
import re

app = Flask(__name__)

# --- In-memory "database" -------------------------------------------------
subscribers = []          # เก็บอีเมลตามที่กรอกมาเป๊ะๆ (ไม่ lower-case) — เทียบซ้ำแบบ case-insensitive ตอนอ่าน (ดู subscribe())
fail_mode = {"on": False}  # จำลอง subscriber DB unavailable (คุมโดย automation script เท่านั้น)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_LOCAL_PART = 64  # RFC 5321


def validate_email(raw: str):
    """คืน (is_valid, cleaned_email, error_message)"""
    if raw is None:
        return False, "", "กรุณากรอกอีเมลให้ถูกต้อง"
    cleaned = raw.strip()  # BR-001/TC-008: ต้อง trim ช่องว่างนำหน้า/ตามหลังก่อนตรวจรูปแบบ
    if cleaned == "":
        return False, cleaned, "กรุณากรอกอีเมลให้ถูกต้อง"
    if not EMAIL_RE.match(cleaned):
        return False, cleaned, "กรุณากรอกอีเมลให้ถูกต้อง"
    local_part = cleaned.split("@", 1)[0]
    if len(local_part) > MAX_LOCAL_PART:
        return False, cleaned, "กรุณากรอกอีเมลให้ถูกต้อง"
    return True, cleaned, ""


INDEX_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>Example Shop — Demo Store</title>
<style>
  body { font-family: -apple-system, "Segoe UI", Arial, sans-serif; margin: 0; background: #f7f7f5; color: #222; }
  header { background: #1b1b1b; color: #fff; padding: 24px 32px; }
  main { max-width: 900px; margin: 40px auto; padding: 0 16px; min-height: 300px; }
  footer { background: #1b1b1b; color: #ddd; padding: 40px 32px; margin-top: 80px; }
  .newsletter-widget { max-width: 420px; }
  .newsletter-widget h3 { margin: 0 0 8px; font-size: 18px; color: #fff; }
  .newsletter-widget p { margin: 0 0 16px; color: #aaa; font-size: 14px; }
  .newsletter-form { display: flex; gap: 8px; }
  #newsletter-email {
    flex: 1; padding: 10px 12px; border-radius: 4px; border: 1px solid #555;
    font-size: 14px; background: #2a2a2a; color: #fff;
  }
  #newsletter-email:focus { outline: 2px solid #6cb4ff; }
  #newsletter-submit {
    padding: 10px 18px; border-radius: 4px; border: none; background: #e0a527;
    color: #1b1b1b; font-weight: 600; cursor: pointer; font-size: 14px;
  }
  #newsletter-submit:disabled { opacity: 0.6; cursor: not-allowed; }
  #newsletter-message { margin-top: 10px; font-size: 14px; min-height: 20px; }
  #newsletter-message.success { color: #7CFC9A; }
  #newsletter-message.error { color: #ff8a8a; }
  label { color: #ddd; font-size: 13px; display: block; margin-bottom: 6px; }
</style>
</head>
<body>
<header><h1>Example Shop</h1></header>
<main>
  <h2>สินค้าขายดี</h2>
  <p>หน้าเดโมสำหรับทดสอบฟีเจอร์ Newsletter Email Subscription (ดู footer ด้านล่าง)</p>
</main>
<footer>
  <div class="newsletter-widget">
    <h3>สมัครรับข่าวสาร</h3>
    <p>รับโปรโมชั่นและข่าวสารใหม่ล่าสุดจากเราทางอีเมล</p>
    <form class="newsletter-form" id="newsletter-form" novalidate>
      <label for="newsletter-email" class="visually-hidden-label">อีเมลของคุณ</label>
      <input type="text" id="newsletter-email" name="email" placeholder="อีเมลของคุณ" aria-label="อีเมลของคุณ">
      <button type="submit" id="newsletter-submit">สมัครรับข่าวสาร</button>
    </form>
    <div id="newsletter-message" role="status" aria-live="polite"></div>
  </div>
</footer>
<script>
  const form = document.getElementById('newsletter-form');
  const emailInput = document.getElementById('newsletter-email');
  const submitBtn = document.getElementById('newsletter-submit');
  const messageEl = document.getElementById('newsletter-message');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    // BR-004: disable ปุ่มทันทีหลังกดครั้งแรกจนกว่าจะได้ผลลัพธ์ (กันกดซ้ำ/double-submit)
    if (submitBtn.disabled) return;
    submitBtn.disabled = true;
    messageEl.textContent = '';
    messageEl.className = '';

    fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailInput.value })
    })
      .then(function (res) { return res.json().then(function (data) { return { status: res.status, data: data }; }); })
      .then(function (result) {
        if (result.data.ok) {
          messageEl.textContent = 'สมัครรับข่าวสารสำเร็จ ขอบคุณที่ติดตามเรา';
          messageEl.className = 'success';
          emailInput.value = '';
        } else {
          messageEl.textContent = result.data.error || 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง';
          messageEl.className = 'error';
        }
      })
      .catch(function () {
        messageEl.textContent = 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง';
        messageEl.className = 'error';
      })
      .finally(function () {
        submitBtn.disabled = false;
      });
  });
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")


@app.post("/api/subscribe")
def subscribe():
    if fail_mode["on"]:
        # TC-011: จำลอง subscriber DB unavailable — ต้อง reset ตัวเองหลังยิง fail 1 ครั้ง
        # เพื่อไม่ให้ค้าง fail ตลอดไปถ้า automation ลืม reset (กันปัญหาทดสอบครั้งถัดไปพังตาม)
        fail_mode["on"] = False
        return jsonify({"ok": False, "error": "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง"}), 500

    body = request.get_json(silent=True) or {}
    raw_email = body.get("email", "")
    is_valid, cleaned, err = validate_email(raw_email)
    if not is_valid:
        return jsonify({"ok": False, "error": err}), 400

    # BR-002 (แก้ไขแล้วตาม Ticket #9 / RISK-001): เช็คอีเมลซ้ำแบบ case-insensitive
    # (เดิมเป็น exact-match case-sensitive ซึ่งเป็นบั๊กที่ TC-005 จับได้ — Dev แก้โดยเทียบแบบ
    # .lower() ทั้งสองฝั่ง แต่ยังคงเก็บอีเมลตามที่ผู้ใช้กรอกมาเป๊ะๆ ไว้ใน subscribers เหมือนเดิม
    # ไม่กระทบ Business Rule อื่น)
    if any(cleaned.lower() == existing.lower() for existing in subscribers):
        return jsonify({"ok": False, "error": "อีเมลนี้สมัครรับข่าวสารไปแล้ว"}), 409

    subscribers.append(cleaned)
    return jsonify({"ok": True, "message": "สมัครรับข่าวสารสำเร็จ ขอบคุณที่ติดตามเรา"}), 200


# --- Test-only control endpoints (ไม่ใช่ส่วนหนึ่งของฟีเจอร์จริง) -------------
@app.post("/__test__/reset")
def test_reset():
    subscribers.clear()
    fail_mode["on"] = False
    return jsonify({"ok": True, "subscribers": list(subscribers)})


@app.post("/__test__/seed")
def test_seed():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "")
    if email and email not in subscribers:
        subscribers.append(email)
    return jsonify({"ok": True, "subscribers": list(subscribers)})


@app.post("/__test__/fail-mode")
def test_fail_mode():
    body = request.get_json(silent=True) or {}
    fail_mode["on"] = bool(body.get("on", False))
    return jsonify({"ok": True, "fail_mode": fail_mode["on"]})


@app.get("/__test__/state")
def test_state():
    return jsonify({"subscribers": list(subscribers), "fail_mode": fail_mode["on"]})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8931, debug=False)
