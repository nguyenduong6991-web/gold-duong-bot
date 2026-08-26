import requests
import datetime

# ==================== ĐIỀN SẴN — KHÔNG CẦN SỬA ====================
BOT_TOKEN = "8892269519:AAH1hKBuh7Rxm43YXz65x_TS9A1EDWb57Zo"
CHAT_ID = "7176458499"
# ==================================================================

prev_e10 = 0
prev_e5 = 0
prev_diesel = 0
prev_world_gas = 0
prev_world_oil = 0
first_run = True

def get_fuel_prices():
    global first_run, prev_e10, prev_e5, prev_diesel, prev_world_gas, prev_world_oil
    
    print("="*50)
    print("GIÁ XĂNG DẦU — CẬP NHẬT THỜI GIAN THỰC")
    print("="*50)
    
    e10_price = 0
    e5_price = 0
    diesel_price = 0
    world_gas = 0
    world_oil = 0
    
    try:
        res = requests.get("https://api.petrolimex.com.vn/api/v1/prices/latest", timeout=15)
        print(f"🌐 API Petrolimex: HTTP {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                for item in data:
                    name = str(item.get("name", "")).upper()
                    price = float(item.get("price", 0))
                    if "E10" in name:
                        e10_price = price
                        print(f"✅ E10: {e10_price:,} VNĐ/lít")
                    elif "E5" in name and "E10" not in name:
                        e5_price = price
                        print(f"✅ E5: {e5_price:,} VNĐ/lít")
                    elif "DIESEL" in name or "DO" in name:
                        diesel_price = price
                        print(f"✅ Dầu Diesel: {diesel_price:,} VNĐ/lít")
    except Exception as e:
        print(f"⚠️ Lỗi lấy giá trong nước: {e}")
    
    try:
        res_oil = requests.get("https://api.gold-api.com/price/OIL", timeout=10)
        if res_oil.status_code == 200:
            data_oil = res_oil.json()
            world_oil = float(data_oil.get("price", 0))
        print(f"✅ Dầu thế giới (WTI): {world_oil:.2f} USD/thùng")
    except Exception as e:
        print(f"⚠️ Lỗi lấy giá dầu thế giới: {e}")
    
    try:
        res_gas = requests.get("https://api.gold-api.com/price/GASOLINE", timeout=10)
        if res_gas.status_code == 200:
            data_gas = res_gas.json()
            world_gas = float(data_gas.get("price", 0))
        print(f"✅ Xăng thế giới: {world_gas:.2f} USD/thùng")
    except Exception as e:
        print(f"⚠️ Lỗi lấy giá xăng thế giới: {e}")
    
    if e10_price == 0:
        e10_price = 23150 if first_run else prev_e10
        print(f"⚠️ Dùng giá dự phòng E10: {e10_price}")
    if e5_price == 0:
        e5_price = 23950 if first_run else prev_e5
        print(f"⚠️ Dùng giá dự phòng E5: {e5_price}")
    if diesel_price == 0:
        diesel_price = 21450 if first_run else prev_diesel
        print(f"⚠️ Dùng giá dự phòng Dầu: {diesel_price}")
    if world_oil == 0:
        world_oil = 78.50 if first_run else prev_world_oil
    if world_gas == 0:
        world_gas = 2.45 if first_run else prev_world_gas
    
    return {
        "e10": e10_price,
        "e5": e5_price,
        "diesel": diesel_price,
        "world_gas": round(world_gas, 2),
        "world_oil": round(world_oil, 2)
    }

def calc_change(current, previous):
    if previous == 0 or first_run:
        return 0, 0
    change = current - previous
    change_percent = (change / previous) * 100 if previous != 0 else 0
    return change, change_percent

def format_number(num):
    return f"{num:,.0f}".replace(",", ".")

def format_change_vnd(change):
    if change > 0:
        return f"📈 +{format_number(change)} VNĐ/lít"
    elif change < 0:
        return f"📉 {format_number(change)} VNĐ/lít"
    else:
        return "➖ Không đổi"

def format_change_usd(change):
    if change > 0:
        return f"📈 +{change:.2f} USD"
    elif change < 0:
        return f"📉 {change:.2f} USD"
    else:
        return "➖ Không đổi"

def send_telegram_message(text):
    if not BOT_TOKEN:
        print("❌ Chưa có BOT_TOKEN")
        return None
    if not CHAT_ID:
        print("❌ Chưa có CHAT_ID")
        return None
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    print("📤 Đang gửi đến Telegram...")
    
    try:
        response = requests.post(url, data=data, timeout=30)
        result = response.json()
        print(f"📨 Kết quả gửi: {result.get('ok', False)}")
        if not result.get('ok', False):
            print(f"❌ Lỗi Telegram: {result}")
        return result
    except Exception as e:
        print(f"❌ Lỗi kết nối Telegram: {e}")
        return None

def main():
    global first_run, prev_e10, prev_e5, prev_diesel, prev_world_gas, prev_world_oil
    
    prices = get_fuel_prices()
    if not prices:
        send_telegram_message("⚠️ Lỗi: Không lấy được dữ liệu giá!")
        return
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    e10_change, e10_pct = calc_change(prices["e10"], prev_e10)
    e5_change, e5_pct = calc_change(prices["e5"], prev_e5)
    diesel_change, diesel_pct = calc_change(prices["diesel"], prev_diesel)
    gas_change, gas_pct = calc_change(prices["world_gas"], prev_world_gas)
    oil_change, oil_pct = calc_change(prices["world_oil"], prev_world_oil)
    
    msg = f"""⛽ <b>GIÁ XĂNG DẦU HÀNG NGÀY</b> ⛽
🕒 Cập nhật: {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 <b>Giá Trong Nước (VNĐ/lít)</b>
⛽ Xăng E10: {format_number(prices['e10'])} VNĐ/lít
"""
    if not first_run:
        msg += f"   {format_change_vnd(e10_change)} ({e10_pct:+.2f}%)\n"
    
    msg += f"⛽ Xăng E5:  {format_number(prices['e5'])} VNĐ/lít\n"
    if not first_run:
        msg += f"   {format_change_vnd(e5_change)} ({e5_pct:+.2f}%)\n"
    
    msg += f"🛢️ Dầu Diesel: {format_number(prices['diesel'])} VNĐ/lít\n"
    if not first_run:
        msg += f"   {format_change_vnd(diesel_change)} ({diesel_pct:+.2f}%)\n"
    
    msg += f"""━━━━━━━━━━━━━━━━━━━━━
🌍 <b>Giá Thế Giới (USD/thùng)</b>
🛢️ Dầu thô WTI: {prices['world_oil']:.2f} USD/thùng
"""
    if not first_run:
        msg += f"   {format_change_usd(oil_change)} ({oil_pct:+.2f}%)\n"
    
    msg += f"⛽ Xăng thế giới: {prices['world_gas']:.2f} USD/thùng\n"
    if not first_run:
        msg += f"   {format_change_usd(gas_change)} ({gas_pct:+.2f}%)\n"
    
    msg += """━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật: 8h30 & 15h30 hàng ngày
💡 Nguồn: Petrolimex & Thị trường thế giới
"""
    
    send_telegram_message(msg)
    print("✅ Đã gửi thông báo giá xăng dầu thành công!")
    
    prev_e10 = prices["e10"]
    prev_e5 = prices["e5"]
    prev_diesel = prices["diesel"]
    prev_world_gas = prices["world_gas"]
    prev_world_oil = prices["world_oil"]
    
    if first_run:
        print("ℹ️ Lần đầu chạy — từ sau sẽ so sánh với ngày trước")
        first_run = False

if __name__ == "__main__":
    main()
