import requests
import datetime
import os
import json

# ============================================================
# CẤU HÌNH
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# File lưu giá lần trước
DATA_FILE = "gold_previous.json"


# ============================================================
# ĐỊNH DẠNG SỐ
# ============================================================

def format_number(num):
    return f"{num:,.0f}".replace(",", ".")


def get_icon(value):
    if value > 0:
        return "📈 +"
    elif value < 0:
        return "📉 "
    else:
        return "➖ "


# ============================================================
# LƯU GIÁ LẦN TRƯỚC
# ============================================================

def load_previous_prices():

    default_data = {
        "sjc_buy": 0,
        "sjc_sell": 0,
        "ring_buy": 0,
        "ring_sell": 0,
        "xau": 0,
        "xag": 0,
        "time": ""
    }

    try:
        if os.path.exists(DATA_FILE):

            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]

                return data

    except Exception as e:
        print(f"⚠️ Không đọc được file giá cũ: {e}")

    return default_data


def save_previous_prices(prices):

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prices, f, ensure_ascii=False, indent=4)

        print("💾 Đã lưu giá hiện tại")

    except Exception as e:
        print(f"⚠️ Không lưu được giá: {e}")


# ============================================================
# LẤY GIÁ TỪ VANG.TODAY
# ============================================================

def get_vang_today(type_code):

    try:

        url = (
            "https://www.vang.today/api/prices"
            f"?type={type_code}"
            "&action=current"
        )

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print(
            f"🌐 API {type_code}: "
            f"HTTP {response.status_code}"
        )

        if response.status_code != 200:
            return None

        data = response.json()

        # ----------------------------------------------------
        # API hiện tại:
        #
        # {
        #   "success": true,
        #   "data": [
        #       {
        #           "type_code": "SJL1L10",
        #           "buy": 147000000,
        #           "sell": 150000000
        #       }
        #   ]
        # }
        # ----------------------------------------------------

        if isinstance(data, dict):

            if isinstance(data.get("data"), list):

                if len(data["data"]) > 0:

                    item = data["data"][0]

                    if (
                        "buy" in item
                        and "sell" in item
                    ):
                        return item

            # Trường hợp API trả trực tiếp object
            if (
                "buy" in data
                and "sell" in data
            ):
                return data

        # Trường hợp API trả trực tiếp list
        if isinstance(data, list):

            if len(data) > 0:
                return data[0]

        print(f"⚠️ Không tìm thấy giá {type_code}")

        return None

    except Exception as e:

        print(
            f"❌ Lỗi API {type_code}: {e}"
        )

        return None


# ============================================================
# LẤY GIÁ VÀNG
# ============================================================

def get_gold_prices():

    print("\n==============================")
    print("🔄 ĐANG LẤY GIÁ VÀNG")
    print("==============================")

    previous = load_previous_prices()

    # --------------------------------------------------------
    # 1. VÀNG MIẾNG SJC
    # --------------------------------------------------------

    sjc = get_vang_today("SJL1L10")

    if sjc:

        sjc_buy = int(
            float(sjc.get("buy", 0)) / 10
        )

        sjc_sell = int(
            float(sjc.get("sell", 0)) / 10
        )

        print(
            f"🇻🇳 SJC 9999:"
            f" Mua {format_number(sjc_buy)}"
            f" - Bán {format_number(sjc_sell)} đ/chỉ"
        )

    else:

        sjc_buy = previous["sjc_buy"]
        sjc_sell = previous["sjc_sell"]

        print("⚠️ SJC lỗi → giữ giá lần trước")


    # --------------------------------------------------------
    # 2. VÀNG NHẪN SJC
    # --------------------------------------------------------

    ring = get_vang_today("SJ9999")

    if ring:

        ring_buy = int(
            float(ring.get("buy", 0)) / 10
        )

        ring_sell = int(
            float(ring.get("sell", 0)) / 10
        )

        print(
            f"💍 Nhẫn SJC:"
            f" Mua {format_number(ring_buy)}"
            f" - Bán {format_number(ring_sell)} đ/chỉ"
        )

    else:

        ring_buy = previous["ring_buy"]
        ring_sell = previous["ring_sell"]

        print("⚠️ Nhẫn SJC lỗi → giữ giá lần trước")


    # --------------------------------------------------------
    # 3. VÀNG THẾ GIỚI XAU/USD
    # --------------------------------------------------------

    xau_data = get_vang_today("XAUUSD")

    if xau_data:

        xau_price = float(
            xau_data.get(
                "buy",
                xau_data.get("sell", 0)
            )
        )

        print(
            f"🌎 XAU/USD: "
            f"{xau_price:.2f} USD/oz"
        )

    else:

        xau_price = previous["xau"]

        print(
            "⚠️ XAU lỗi → giữ giá lần trước"
        )


    # --------------------------------------------------------
    # 4. BẠC THẾ GIỚI
    # --------------------------------------------------------

    xag_price = 0

    try:

        response = requests.get(
            "https://api.gold-api.com/price/XAG",
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            xag_price = float(
                data.get("price", 0)
            )

        print(
            f"🥈 XAG/USD: "
            f"{xag_price:.2f} USD/oz"
        )

    except Exception as e:

        print(
            f"⚠️ Lỗi lấy bạc: {e}"
        )


    if xag_price == 0:

        xag_price = previous["xag"]


    # --------------------------------------------------------
    # KIỂM TRA
    # --------------------------------------------------------

    if sjc_buy <= 0 or sjc_sell <= 0:

        print("❌ Không có giá SJC hợp lệ")

        return None


    if ring_buy <= 0 or ring_sell <= 0:

        print("❌ Không có giá nhẫn hợp lệ")

        return None


    return {
        "sjc_buy": sjc_buy,
        "sjc_sell": sjc_sell,

        "ring_buy": ring_buy,
        "ring_sell": ring_sell,

        "xau": round(xau_price, 2),
        "xag": round(xag_price, 2)
    }


# ============================================================
# TÍNH TĂNG GIẢM
# ============================================================

def calc_change(current, previous):

    if previous <= 0:
        return 0, 0

    change = current - previous

    percent = (
        change / previous
    ) * 100

    return change, percent


# ============================================================
# GỬI TELEGRAM
# ============================================================

def send_telegram_message(text):

    if not BOT_TOKEN:
        print("❌ Chưa có BOT_TOKEN")
        return False

    if not CHAT_ID:
        print("❌ Chưa có CHAT_ID")
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=20
        )

        result = response.json()

        if result.get("ok"):

            print("✅ Telegram gửi thành công")

            return True

        print(
            f"❌ Telegram lỗi: {result}"
        )

        return False

    except Exception as e:

        print(
            f"❌ Lỗi gửi Telegram: {e}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("====================================")
    print("       GIÁ VÀNG TỰ ĐỘNG")
    print("====================================")

    prices = get_gold_prices()

    if not prices:

        send_telegram_message(
            "⚠️ <b>GIÁ VÀNG</b>\n\n"
            "❌ Không lấy được dữ liệu giá."
        )

        return


    # --------------------------------------------------------
    # GIÁ LẦN TRƯỚC
    # --------------------------------------------------------

    previous = load_previous_prices()

    has_previous = (
        previous["sjc_buy"] > 0
        and previous["sjc_sell"] > 0
    )


    # --------------------------------------------------------
    # THỜI GIAN
    # --------------------------------------------------------

    now = datetime.datetime.now()

    now_text = now.strftime(
        "%d/%m/%Y %H:%M:%S"
    )


    # --------------------------------------------------------
    # TÍNH THAY ĐỔI SJC
    # --------------------------------------------------------

    sjc_buy_change, sjc_buy_pct = calc_change(
        prices["sjc_buy"],
        previous["sjc_buy"]
    )

    sjc_sell_change, sjc_sell_pct = calc_change(
        prices["sjc_sell"],
        previous["sjc_sell"]
    )


    # --------------------------------------------------------
    # TÍNH THAY ĐỔI NHẪN
    # --------------------------------------------------------

    ring_buy_change, ring_buy_pct = calc_change(
        prices["ring_buy"],
        previous["ring_buy"]
    )

    ring_sell_change, ring_sell_pct = calc_change(
        prices["ring_sell"],
        previous["ring_sell"]
    )


    # --------------------------------------------------------
    # TÍNH THAY ĐỔI XAU
    # --------------------------------------------------------

    xau_change, xau_pct = calc_change(
        prices["xau"],
        previous["xau"]
    )


    # --------------------------------------------------------
    # TÍNH THAY ĐỔI XAG
    # --------------------------------------------------------

    xag_change, xag_pct = calc_change(
        prices["xag"],
        previous["xag"]
    )


    # ========================================================
    # TẠO TIN NHẮN
    # ========================================================

    msg = (
        "🌍 <b>GIÁ VÀNG & BẠC HÀNG NGÀY</b> 🌍\n"
        f"🕒 {now_text}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )


    # ========================================================
    # SJC
    # ========================================================

    msg += (
        "🇻🇳 <b>VÀNG MIẾNG SJC 9999</b>\n"
        f"💰 Giá Mua Vào: "
        f"<b>{format_number(prices['sjc_buy'])}</b> VNĐ/chỉ\n"
    )

    if has_previous:

        msg += (
            f"{get_icon(sjc_buy_change)}"
            f"{format_number(sjc_buy_change)} VNĐ "
            f"({sjc_buy_pct:+.2f}%)\n"
        )


    msg += (
        f"💰 Giá Bán Ra: "
        f"<b>{format_number(prices['sjc_sell'])}</b> VNĐ/chỉ\n"
    )

    if has_previous:

        msg += (
            f"{get_icon(sjc_sell_change)}"
            f"{format_number(sjc_sell_change)} VNĐ "
            f"({sjc_sell_pct:+.2f}%)\n"
        )


    msg += (
        "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    )


    # ========================================================
    # NHẪN SJC
    # ========================================================

    msg += (
        "💍 <b>VÀNG NHẪN SJC 9999</b>\n"
        f"💰 Giá Mua Vào: "
        f"<b>{format_number(prices['ring_buy'])}</b> VNĐ/chỉ\n"
    )

    if has_previous:

        msg += (
            f"{get_icon(ring_buy_change)}"
            f"{format_number(ring_buy_change)} VNĐ "
            f"({ring_buy_pct:+.2f}%)\n"
        )


    msg += (
        f"💰 Giá Bán Ra: "
        f"<b>{format_number(prices['ring_sell'])}</b> VNĐ/chỉ\n"
    )

    if has_previous:

        msg += (
            f"{get_icon(ring_sell_change)}"
            f"{format_number(ring_sell_change)} VNĐ "
            f"({ring_sell_pct:+.2f}%)\n"
        )


    msg += (
        "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    )


    # ========================================================
    # THỊ TRƯỜNG THẾ GIỚI
    # ========================================================

    msg += (
        "🌐 <b>THỊ TRƯỜNG THẾ GIỚI</b>\n"
        f"📊 Vàng XAU/USD: "
        f"<b>{prices['xau']:.2f}</b> USD/oz\n"
    )

    if has_previous:

        msg += (
            f"{get_icon(xau_change)}"
            f"{xau_change:+.2f} USD "
            f"({xau_pct:+.2f}%)\n"
        )


    msg += (
        f"📊 Bạc XAG/USD: "
        f"<b>{prices['xag']:.2f}</b> USD/oz\n"
    )

    if has_previous:

        msg += (
            f"{get_icon(xag_change)}"
            f"{xag_change:+.2f} USD "
            f"({xag_pct:+.2f}%)\n"
        )


    msg += (
        "\n━━━━━━━━━━━━━━━━━━━━\n"
        "🔄 <b>Cập nhật mỗi 1 giờ</b>\n"
        "📡 Nguồn: Vang.Today API\n"
    )


    # ========================================================
    # GỬI TELEGRAM
    # ========================================================

    send_telegram_message(msg)


    # ========================================================
    # LƯU GIÁ
    # ========================================================

    prices_to_save = {
        "sjc_buy": prices["sjc_buy"],
        "sjc_sell": prices["sjc_sell"],

        "ring_buy": prices["ring_buy"],
        "ring_sell": prices["ring_sell"],

        "xau": prices["xau"],
        "xag": prices["xag"],

        "time": now_text
    }

    save_previous_prices(
        prices_to_save
    )


    print("\n====================================")
    print("✅ HOÀN TẤT")
    print("====================================")


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()
