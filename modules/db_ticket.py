import time
import random
import uuid
import redis
import streamlit as st
from streamlit_autorefresh import st_autorefresh

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, protocol=2)

def reset_server(seat_count, bot_count):
    r.flushdb()
    r.set("ticket:total_seats", seat_count)
    r.set("ticket:total_bots", bot_count)
    
    pipeline = r.pipeline()
    for i in range(bot_count):
        bot_id = f"bot_{i}_{uuid.uuid4().hex[:4]}"
        target_seat = str(random.randint(1, seat_count))
        pipeline.hset("ticket:target", bot_id, target_seat)
    pipeline.execute()

def start_ticketing(my_id, my_seat):
    pipeline = r.pipeline()
    pipeline.hset("ticket:target", my_id, my_seat)
    
    now = time.time()
    my_time = now + random.uniform(0.0, 1.0)
    pipeline.zadd("ticket:queue", {my_id: my_time})
    
    all_bots = r.hkeys("ticket:target")
    all_bots = [b for b in all_bots if b != my_id]
    
    for bot_id in all_bots:
        bot_time = now + random.uniform(0.0, 1.5)
        pipeline.zadd("ticket:queue", {bot_id: bot_time})
        
    pipeline.execute()

def process_queue():
    queue_size = r.zcard("ticket:queue")
    if queue_size == 0:
        return
    
    processed = r.zpopmin("ticket:queue", count=40)
    
    for user_id, score in processed:
        target_seat = r.hget("ticket:target", user_id)
        if target_seat:
            success = r.hsetnx("ticket:seats", target_seat, user_id)
            if success:
                r.hset("ticket:result", user_id, "SUCCESS")
            else:
                r.hset("ticket:result", user_id, "SOLD_OUT")

def render_ticket_system():
    st.title("🎫 실시간 티켓팅 시뮬레이터")
    st.caption("Redis HSETNX를 이용한 원자적 동시성 제어 및 실시간 대기열 시스템")
    
    if "my_id" not in st.session_state:
        st.session_state["my_id"] = f"USER_{uuid.uuid4().hex[:4]}"
        
    my_id = st.session_state["my_id"]
    
    col1, col2 = st.columns(2)
    with col1:
        s_count = st.number_input("총 좌석 수", min_value=10, max_value=200, value=50, step=10)
    with col2:
        b_count = st.number_input("경쟁자(봇) 수", min_value=10, max_value=1000, value=200, step=50)
        
    if st.button("🔄 좌석 및 서버 초기화", use_container_width=True):
        reset_server(s_count, b_count)
        st.session_state["ticketing_started"] = False
        st.session_state["my_target"] = None
        st.rerun()
        
    st.divider()
    
    total_seats = r.get("ticket:total_seats")
    if total_seats is None:
        st.info("위 버튼을 눌러 서버를 초기화해주세요.")
        return
        
    total_seats = int(total_seats)
    is_started = st.session_state.get("ticketing_started", False)
    
    if is_started:
        st_autorefresh(interval=1000, key="queue_refresh")
        process_queue()
        
        my_rank = r.zrank("ticket:queue", my_id)
        my_result = r.hget("ticket:result", my_id)
        
        if my_result == "SUCCESS":
            st.success(f"🎉 예매 성공! [{st.session_state['my_target']}번] 좌석을 확보했습니다.")
            st.session_state["ticketing_started"] = False
        elif my_result == "SOLD_OUT":
            st.error(f"❌ 예매 실패: 앗! 대기하는 동안 누군가 [{st.session_state['my_target']}번] 좌석을 먼저 채갔습니다!")
            st.session_state["ticketing_started"] = False
        elif my_rank is not None:
            st.warning(f"⏳ 결제 서버 진입 대기 중... 내 앞에 **{my_rank}** 명 남았습니다.")
            
        queue_total = r.zcard("ticket:queue")
        total_bots = int(r.get("ticket:total_bots") or 0)
        if total_bots > 0:
            progress_val = 1 - (my_rank if my_rank else 0) / (total_bots + 1)
            progress_val = max(0.0, min(1.0, progress_val))
            st.progress(progress_val)
            
    st.subheader("💺 좌석 배치도 (초록색 클릭 시 예매 대기열 진입)")
    st.markdown("**🟩 빈 좌석** (예매 가능) &nbsp;&nbsp;|&nbsp;&nbsp; **🟥 예매된 좌석** (타인) &nbsp;&nbsp;|&nbsp;&nbsp; **🟦 내 좌석** (성공)")
    
    taken_seats = r.hgetall("ticket:seats")
    cols_per_row = 10
    
    for i in range(0, total_seats, cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            seat_num = i + j + 1
            if seat_num > total_seats:
                break
                
            seat_str = str(seat_num)
            owner = taken_seats.get(seat_str)
            
            with row_cols[j]:
                if owner == my_id:
                    st.button(f"🟦 {seat_num}", key=f"seat_{seat_num}", disabled=True)
                elif owner is not None:
                    st.button(f"🟥 {seat_num}", key=f"seat_{seat_num}", disabled=True)
                else:
                    if is_started:
                        st.button(f"🟩 {seat_num}", key=f"seat_{seat_num}", disabled=True)
                    else:
                        if st.button(f"🟩 {seat_num}", key=f"seat_{seat_num}"):
                            st.session_state["my_target"] = seat_str
                            start_ticketing(my_id, seat_str)
                            st.session_state["ticketing_started"] = True
                            st.rerun()