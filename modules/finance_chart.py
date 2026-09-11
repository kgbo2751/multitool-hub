import yfinance as yf

TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "테슬라": "TSLA",
    "엔비디아": "NVDA",
    "애플": "AAPL"
}

def get_stock_data():
    stock_results = []
    for name, ticker_name in TICKERS.items():
        try:
            stock = yf.Ticker(ticker_name)
            data = stock.history(period="2d")
            
            if len(data) >= 2:
                today = data.iloc[-1]
                yesterday = data.iloc[-2]
                current_price = today['Close']
                diff = current_price - yesterday['Close']
                change_value = (diff / yesterday['Close']) * 100
                
                stock_results.append({
                    "name": name,
                    "ticker": ticker_name,
                    "price": f"{current_price:,.2f}",
                    "delta": f"{diff:+,.2f} ({change_value:+.2f}%)",
                    "change_value": change_value
                })
            elif len(data) == 1:
                today = data.iloc[-1]
                stock_results.append({
                    "name": name,
                    "ticker": ticker_name,
                    "price": f"{today['Close']:,.2f}",
                    "delta": "0.00 (0.00%)",
                    "change_value": 0.0
                })
        except Exception:
            continue
    return stock_results