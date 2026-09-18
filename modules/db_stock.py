import pymongo
import random
import time
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["stock_game_db"]
users_col = db["users"]
stocks_col = db["stocks"]
history_col = db["history"]

def init_game_data():
    if users_col.count_documents({"username": "player1"}) == 0:
        users_col.insert_one({
            "username": "player1",
            "balance": 10000000,
            "portfolio": {"삼성전자": 0, "테슬라": 0}
        })
    
    if stocks_col.count_documents({}) == 0:
        stocks_col.insert_many([
            {"name": "삼성전자", "price": 70000},
            {"name": "테슬라", "price": 300000}
        ])
        
        current_time = time.time()
        history_col.insert_many([
            {"name": "삼성전자", "price": 70000, "time": current_time},
            {"name": "테슬라", "price": 300000, "time": current_time}
        ])

def render_stock_game():
    init_game_data()
    
    st_autorefresh(interval=10000, key="stock_refresh")
    
    st.title("📈 DB 연동 주식")
    st.caption("MongoDB 실시간 가상 주식 거래 게임")
    
    stocks = list(stocks_col.find({}))
    
    if "last_price_update" not in st.session_state:
        st.session_state["last_price_update"] = time.time()
        
    current_time = time.time()
    if current_time - st.session_state["last_price_update"] >= 10:
        for s in stocks:
            change_rate = random.uniform(-0.05, 0.05)
            new_price = int(s['price'] * (1 + change_rate))
            stocks_col.update_one({"name": s['name']}, {"$set": {"price": new_price}})
            
            history_col.insert_one({
                "name": s['name'], 
                "price": new_price, 
                "time": current_time
            })
            
        st.session_state["last_price_update"] = current_time
        stocks = list(stocks_col.find({}))
    
    user = users_col.find_one({"username": "player1"})
    
    st.subheader(f"💰 내 잔고: {user['balance']:,} 원")
    st.write(f"💼 보유 주식: 삼성전자 {user['portfolio'].get('삼성전자', 0)}주 | 테슬라 {user['portfolio'].get('테슬라', 0)}주")
    st.divider()
    
    cols = st.columns(len(stocks))
    for col, stock in zip(cols, stocks):
        with col:
            with st.container(border=True):
                st.markdown(f"### {stock['name']}")
                st.markdown(f"현재가: **{stock['price']:,}원**")
                
                stock_history = list(history_col.find({"name": stock['name']}, {"_id": 0, "price": 1, "time": 1}))
                if stock_history:
                    df = pd.DataFrame(stock_history)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df = df.set_index('time')
                    st.line_chart(df['price'], height=150)
                
                col_buy, col_sell = st.columns(2)
                
                with col_buy:
                    buy_amount = st.number_input("매수량", min_value=1, value=1, key=f"buy_{stock['name']}")
                    if st.button("🔴 매수", key=f"btn_buy_{stock['name']}", use_container_width=True):
                        total_price = stock['price'] * buy_amount
                        if user['balance'] >= total_price:
                            users_col.update_one(
                                {"username": "player1"},
                                {"$inc": {"balance": -total_price, f"portfolio.{stock['name']}": buy_amount}}
                            )
                            st.rerun()
                        else:
                            st.error("잔고 부족")
                
                with col_sell:
                    sell_amount = st.number_input("매도량", min_value=1, value=1, key=f"sell_{stock['name']}")
                    if st.button("🔵 매도", key=f"btn_sell_{stock['name']}", use_container_width=True):
                        if user['portfolio'].get(stock['name'], 0) >= sell_amount:
                            sell_price = stock['price'] * sell_amount
                            users_col.update_one(
                                {"username": "player1"},
                                {"$inc": {"balance": sell_price, f"portfolio.{stock['name']}": -sell_amount}}
                            )
                            st.rerun()
                        else:
                            st.error("수량 부족")