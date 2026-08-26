import requests
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================================
# CẤU HÌNH
# =====================================================

BOT_TOKEN = os.getenv("8611119308:AAHWk73wYo0-fdzSDSQi7gNeybr6ShMgbws")
CHAT_ID = os.getenv("7176458499")

# API key giá dầu thế giới
# Đăng ký API Ninjas rồi đặt biến môi trường API_NINJAS_KEY
API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")

# Giá USD/VND
USD_VND = 26000

DATA_FILE = "gia_xang_previous.json"

TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

# =====================================================
# TELEGRAM
# =====================================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        r = requests.post(url, data=data, timeout=20)

        if r.status_code == 200:
            print("Telegram: OK")
        else:
            print("Telegram lỗi:", r.text)

    except Exception as e:
        print("Lỗi Telegram:", e)


# =====================================================
# ĐỌC GIÁ KỲ TRƯỚC
# =====================================================

def load_previous():

    if not os.path.exists(DATA_FILE):
        return None

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return None


# =====================================================
# LƯU GIÁ KỲ HIỆN TẠI
# =====================================================

def save_current(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================================================
# TÍNH TĂNG GIẢM
# =====================================================

def change(current, previous):

    if previous is None or previous == 0:
        return 0, 0

    diff = current - previous
    percent = (diff / previous) * 100

    return diff, percent


def format_change(diff, percent):

    if diff > 0:
        return f"🔺 +{diff:,.0f} đ (+{percent:.2f}%)"

    elif diff < 0:
        return f"🔻 {diff:,.0f} đ ({percent:.2f}%)"

    else:
        return "➡️ 0 đ (0.00%)"


# =====================================================
# LẤY GIÁ XĂNG DẦU TRONG NƯỚC
# =====================================================

def get_domestic_prices():

    # Nguồn dữ liệu
    url = "https://www.pvoil.com.vn/tin-gia-xang-dau"

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36"
    }

    try:

        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        html = r.text

        # Tìm giá dựa trên tên sản phẩm
        import re

        def find_price(keyword):

            pattern = rf"{keyword}.*?([\d,.]+)\s*(?:đ|VNĐ)"
            match = re.search(
                pattern,
                html,
                re.IGNORECASE | re.DOTALL
            )

            if not match:
                return None

            value = match.group(1)

            value = value.replace(".", "")
            value = value.replace(",", "")

            try:
                return float(value)
            except:
                return None

        e10 = find_price("E10 RON 95")
        e5 = find_price("E5 RON 92")
        diesel = find_price("DO 0,05S")

        # Nếu PVOIL thay đổi giao diện,
        # dùng giá dự phòng từ nguồn công khai.
        if not e10:
            e10 = get_from_vnexpress("E10")

        if not e5:
            e5 = get_from_vnexpress("E5")

        if not diesel:
            diesel = get_from_vnexpress("Diesel")

        if not e10 or not e5 or not diesel:
            raise Exception("Không lấy được đủ giá xăng dầu")

        return {
            "e10": e10,
            "e5": e5,
            "diesel": diesel
        }

    except Exception as e:

        print("Lỗi lấy giá trong nước:", e)

        return get_backup_prices()


# =====================================================
# NGUỒN DỰ PHÒNG
# =====================================================

def get_from_vnexpress(keyword):

    try:

        url = "https://vnexpress.net/chu-de/gia-xang-dau-3026"

        headers = {
            "User-Agent":
            "Mozilla/5.0 (Android 10) AppleWebKit/537.36 Chrome/120"
        }

        html = requests.get(
            url,
            headers=headers,
            timeout=20
        ).text

        import re

        if keyword == "E10":
            pattern = r"E10.*?([\d.]{4,7})"

        elif keyword == "E5":
            pattern = r"E5.*?([\d.]{4,7})"

        else:
            pattern = r"Diesel.*?([\d.]{4,7})"

        m = re.search(
            pattern,
            html,
            re.IGNORECASE | re.DOTALL
        )

        if m:

            value = m.group(1)

            value = value.replace(".", "")

            return float(value)

    except:
        pass

    return None


def get_backup_prices():

    # Không tự ý dùng giá cũ nếu API lỗi.
    # Trả về None để bot báo lỗi rõ ràng.
    return {
        "e10": None,
        "e5": None,
        "diesel": None
    }


# =====================================================
# GIÁ DẦU THẾ GIỚI
# =====================================================

def get_oil_price(name):

    if not API_NINJAS_KEY:
        return None

    url = (
        "https://api.api-ninjas.com/v1/commodityprice"
        f"?name={name}"
    )

    headers = {
        "X-Api-Key": API_NINJAS_KEY
    }

    try:

        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if r.status_code != 200:
            print("Oil API:", r.text)
            return None

        data = r.json()

        return float(data["price"])

    except Exception as e:

        print("Lỗi giá dầu:", e)

        return None


# =====================================================
# TẠO TIN NHẮN
# =====================================================

def make_message():

    now = datetime.now(TIMEZONE)

    domestic = get_domestic_prices()

    previous = load_previous()

    # -------------------------------
    # GIÁ TRONG NƯỚC
    # -------------------------------

    e10 = domestic["e10"]
    e5 = domestic["e5"]
    diesel = domestic["diesel"]

    text = (
        "⛽ GIÁ XĂNG DẦU\n"
        f"📅 {now.strftime('%d/%m/%Y %H:%M')}\n\n"
        "🇻🇳 GIÁ TRONG NƯỚC\n"
    )

    if e10:

        old = previous.get("e10") if previous else None
        diff, pct = change(e10, old)

        text += (
            f"⛽ E10 RON95: {e10:,.0f} đ/lít\n"
            f"   {format_change(diff, pct)}\n\n"
        )

    else:
        text += "⛽ E10 RON95: ❌ Không lấy được giá\n\n"

    if e5:

        old = previous.get("e5") if previous else None
        diff, pct = change(e5, old)

        text += (
            f"⛽ E5 RON92: {e5:,.0f} đ/lít\n"
            f"   {format_change(diff, pct)}\n\n"
        )

    else:
        text += "⛽ E5 RON92: ❌ Không lấy được giá\n\n"

    if diesel:

        old = previous.get("diesel") if previous else None
        diff, pct = change(diesel, old)

        text += (
            f"🛢️ Dầu Diesel: {diesel:,.0f} đ/lít\n"
            f"   {format_change(diff, pct)}\n\n"
        )

    else:
        text += "🛢️ Dầu Diesel: ❌ Không lấy được giá\n\n"

    # -------------------------------
    # DẦU THẾ GIỚI
    # -------------------------------

    brent = get_oil_price("brent_crude_oil")
    wti = get_oil_price("crude_oil")

    text += "🌎 DẦU THẾ GIỚI\n"

    if brent:

        brent_vnd = brent * USD_VND

        old = previous.get("brent") if previous else None

        if old:
            diff, pct = change(brent, old)

            text += (
                f"Brent: ${brent:.2f}/thùng\n"
                f"≈ {brent_vnd:,.0f} đ/thùng\n"
                f"   {format_change(diff * USD_VND, pct)}\n\n"
            )

        else:

            text += (
                f"Brent: ${brent:.2f}/thùng\n"
                f"≈ {brent_vnd:,.0f} đ/thùng\n\n"
            )

    else:
        text += "Brent: ❌ Không lấy được giá\n\n"

    if wti:

        wti_vnd = wti * USD_VND

        old = previous.get("wti") if previous else None

        if old:
            diff, pct = change(wti, old)

            text += (
                f"WTI: ${wti:.2f}/thùng\n"
                f"≈ {wti_vnd:,.0f} đ/thùng\n"
                f"   {format_change(diff * USD_VND, pct)}\n\n"
            )

        else:

            text += (
                f"WTI: ${wti:.2f}/thùng\n"
                f"≈ {wti_vnd:,.0f} đ/thùng\n\n"
            )

    else:
        text += "WTI: ❌ Không lấy được giá\n\n"

    # -------------------------------
    # THÔNG TIN KỲ
    # -------------------------------

    if now.hour < 12:
        period = "KỲ 08:30"
    else:
        period = "KỲ 15:30"

    text += (
        "━━━━━━━━━━━━━━\n"
        f"🕐 {period}\n"
        "📊 So sánh với kỳ cập nhật trước\n"
    )

    # -------------------------------
    # LƯU GIÁ
    # -------------------------------

    save_data = {
        "time": now.isoformat(),
        "e10": e10,
        "e5": e5,
        "diesel": diesel,
        "brent": brent,
        "wti": wti
    }

    save_current(save_data)

    return text


# =====================================================
# CHẠY BOT
# =====================================================

def run_bot():

    print("Đang cập nhật giá...")

    if not BOT_TOKEN or not CHAT_ID:

        print("❌ Chưa cấu hình BOT_TOKEN hoặc CHAT_ID")

        return

    message = make_message()

    print(message)

    send_telegram(message)


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    run_bot()
