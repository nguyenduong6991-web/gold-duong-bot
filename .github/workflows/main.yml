import requests
import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

prev_sjc_buy = 0
prev_sjc_sell = 0
prev_ring_buy = 0
prev_ring_sell = 0
prev_silver_buy = 52000
prev_silver_sell = 58000
prev_xau = 0
prev_xag = 0
first_run = True

def get_gold_prices():
    global first_run, prev_sjc_buy, prev_sjc_sell, prev_ring_buy, prev_ring_sell
    global prev_silver_buy, prev_silver_sell, prev_xau, prev_xag
    
    try:
        sjc_buy, sjc_sell = 0, 0
        try:
            res_sjc = requests.get("https://www.vang.today/api/prices?type=SJL1L10", timeout=15)
            if res_sjc.status_code == 200:
                data_sjc = res_sjc.json()
                if data_sjc and len(data_sjc) > 0:
                    sjc_buy = int(float(data_sjc[0].get("buy", 0)) / 10)
                    sjc_sell = int(float(data_sjc[0].get("sell", 0)) / 10)
            print(f"✅ Vàng miếng SJC: Mua={sjc_buy}, Bán={sjc_sell} VNĐ/chỉ")
        except Exception as e:
            print(f"⚠️ Lỗi lấy giá SJC miếng: {e}")
        
        ring_buy, ring_sell = 0, 0
        try:
            res_ring = requests.get("https://www.vang.today/api/prices?type=SJ9999", timeout=15)
            if res_ring.status_code == 200:
                data_ring = res_ring.json()
                if data_ring and len(data_ring) > 0:
                    ring_buy = int(float(data_ring[0].get("buy", 0)) / 10)
                    ring_sell = int(float(data_ring[0].get("sell", 0)) / 10)
            print(f"✅ Vàng nhẫn SJC: Mua={ring_buy}, Bán={ring_sell} VNĐ/chỉ")
        except Exception as e:
            print(f"⚠️ Lỗi lấy giá SJC nhẫn: {e}")
        
        xau_price, xag_price = 0, 0
        try:
            res_xau = requests.get("https://www.vang.today/api/prices?type=XAUUSD", timeout=15)
            if res_xau.status_code == 200:
                data_xau = res_xau.json()
                if data_xau and len(data_xau) > 0:
                    xau_price = float(data_xau[0].get("buy", 0))
            print(f"✅ Vàng thế giới XAU/USD: {xau_price} USD/oz")
        except Exception as e:
            print(f"⚠️ Lỗi lấy giá XAU: {e}")
        
        try:
            res_xag = requests.get("https://api.gold-api.com/price/XAG", timeout=10)
            if res_xag.status_code == 200:
                data_xag = res_xag.json()
                xag_price = float(data_xag.get("price", 0))
            print(f"✅ Bạc thế giới XAG/USD: {xag_price} USD/oz")
        except Exception as e:
            print(f"⚠️ Lỗi lấy giá XAG: {e}")
        
        if sjc_buy == 0 or sjc_sell == 0:
            if first_run:
                sjc_buy, sjc_sell = 14700000, 15000000
            else:
                sjc_buy, sjc_sell = prev_sjc_buy, prev_sjc_sell
        
        if ring_buy == 0 or ring_sell == 0:
            if first_run:
                ring_buy, ring_sell = 14850000, 15250000
            else:
                ring_buy, ring_sell = prev_ring_buy, prev_ring_sell
        
        if xau_price == 0:
            if first_run:
                xau_price = 2450.5
            else:
                xau_price = prev_xau
        
        if xag_price == 0:
            if first_run:
                xag_price = 29.5
            else:
                xag_price = prev_xag
        
        return {
            "sjc_buy": sjc_buy,
            "sjc_sell": sjc_sell,
            "ring_buy": ring_buy,
            "ring_sell": ring_sell,
            "silver_buy": prev_silver_buy,
            "silver_sell": prev_silver_sell,
            "xau": round(xau_price, 2),
            "xag": round(xag_price, 2)
        }
    except Exception as e:
        print(f"❌ Lỗi tổng thể: {e}")
        return None

def calc_change(current, previous):
    if previous == 0 or first_run:
        return 0, 0
    change = current - previous
    change_percent = (change / previous) * 100
    return change, change_percent

def format_number(num):
    return f"{num:,.0f}".replace(",", ".")

def get_icon(val):
    if val > 0: return "📈 +"
    elif val < 0: return "📉 "
    else: return "➖ "

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    return response.json()

def main():
    global first_run, prev_sjc_buy, prev_sjc_sell, prev_ring_buy, prev_ring_sell
    global prev_silver_buy, prev_silver_sell, prev_xau, prev_xag
    
    prices = get_gold_prices()
    if not prices:
        send_telegram_message("⚠️ Lỗi: Không lấy được dữ liệu giá!")
        return
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    sjc_buy_change, sjc_buy_pct = calc_change(prices["sjc_buy"], prev_sjc_buy)
    sjc_sell_change, sjc_sell_pct = calc_change(prices["sjc_sell"], prev_sjc_sell)
    ring_buy_change, ring_buy_pct = calc_change(prices["ring_buy"], prev_ring_buy)
    ring_sell_change, ring_sell_pct = calc_change(prices["ring_sell"], prev_ring_sell)
    silver_buy_change, silver_buy_pct = calc_change(prices["silver_buy"], prev_silver_buy)
    silver_sell_change, silver_sell_pct = calc_change(prices["silver_sell"], prev_silver_sell)
    xau_change, xau_pct = calc_change(prices["xau"], prev_xau)
    xag_change, xag_pct = calc_change(prices["xag"], prev_xag)
    
    msg = f"""🌍 <b>GIÁ VÀNG & BẠC HÀNG NGÀY</b> 🌍
🕒 {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 <b>Vàng Miếng SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['sjc_buy'])} VNĐ/chỉ
"""
    if not first_run:
        msg += f"{get_icon(sjc_buy_change)}{format_number(sjc_buy_change)} VNĐ ({sjc_buy_pct:+.2f}%)\n"
    
    msg += f"💰 Giá Bán Ra: {format_number(prices['sjc_sell'])} VNĐ/chỉ\n"
    if not first_run:
        msg += f"{get_icon(sjc_sell_change)}{format_number(sjc_sell_change)} VNĐ ({sjc_sell_pct:+.2f}%)\n"
    
    msg += f"""━━━━━━━━━━━━━━━━━━━━━
💍 <b>Vàng Nhẫn SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['ring_buy'])} VNĐ/chỉ
"""
    if not first_run:
        msg += f"{get_icon(ring_buy_change)}{format_number(ring_buy_change)} VNĐ ({ring_buy_pct:+.2f}%)\n"
    
    msg += f"💰 Giá Bán Ra: {format_number(prices['ring_sell'])} VNĐ/chỉ\n"
    if not first_run:
        msg += f"{get_icon(ring_sell_change)}{format_number(ring_sell_change)} VNĐ ({ring_sell_pct:+.2f}%)\n"
    
    msg += f"""━━━━━━━━━━━━━━━━━━━━━
🥈 <b>Bạc 999 (Tham khảo)</b>
💰 Giá Mua Vào: {format_number(prices['silver_buy'])} VNĐ/chỉ
"""
    if not first_run:
        msg += f"{get_icon(silver_buy_change)}{format_number(silver_buy_change)} VNĐ ({silver_buy_pct:+.2f}%)\n"
    
    msg += f"💰 Giá Bán Ra: {format_number(prices['silver_sell'])} VNĐ/chỉ\n"
    if not first_run:
        msg += f"{get_icon(silver_sell_change)}{format_number(silver_sell_change)} VNĐ ({silver_sell_pct:+.2f}%)\n"
    
    msg += f"""━━━━━━━━━━━━━━━━━━━━━
🌐 <b>Thị Trường Thế Giới</b>
📊 Vàng XAU/USD: {prices['xau']:.2f} USD/oz
"""
    if not first_run:
        msg += f"{get_icon(xau_change)}{xau_change:+.2f} USD ({xau_pct:+.2f}%)\n"
    
    msg += f"📊 Bạc XAG/USD: {prices['xag']:.2f} USD/oz\n"
    if not first_run:
        msg += f"{get_icon(xag_change)}{xag_change:+.2f} USD ({xag_pct:+.2f}%)\n"
    
    msg += """━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật mỗi 1 giờ | Nguồn: vang.today & GoldAPI
"""
    
    send_telegram_message(msg)
    print("✅ Đã gửi thông báo giá!")
    
    prev_sjc_buy = prices["sjc_buy"]
    prev_sjc_sell = prices["sjc_sell"]
    prev_ring_buy = prices["ring_buy"]
    prev_ring_sell = prices["ring_sell"]
    prev_silver_buy = prices["silver_buy"]
    prev_silver_sell = prices["silver_sell"]
    prev_xau = prices["xau"]
    prev_xag = prices["xag"]
    
    if first_run:
        print("ℹ️ Lần đầu chạy — từ giờ sẽ tự so sánh với giá giờ trước")
        first_run = False

if __name__ == "__main__":
    main()
