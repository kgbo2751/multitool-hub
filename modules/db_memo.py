import os
import random
import pymysql
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "todo_user"),
        password=os.getenv("DB_PASSWORD", "my_password123"),
        database=os.getenv("DB_NAME", "todo_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def init_db():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                content TEXT
            )
        """)
    conn.close()

def fetch_todos():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM todos ORDER BY id DESC")
        todos = cursor.fetchall()
    conn.close()
    return todos

def insert_todo(title, content):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO todos (title, content) VALUES (%s, %s)", (title, content))
    conn.close()

def delete_todo(todo_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.close()

def render_todo_ui():
    init_db()
    
    st.title("📝 DB 연동 메모장")
    
    with st.expander("➕ 새 메모 추가하기", expanded=False):
        with st.form("todo_input_form", clear_on_submit=True):
            new_title = st.text_input("제목")
            new_content = st.text_area("내용")
            submitted = st.form_submit_button("메모 생성")
            
            if submitted and new_title.strip():
                insert_todo(new_title, new_content)
                st.rerun()

    st.divider()
    
    todos = fetch_todos()
    pastel_colors = [
        "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", 
        "#E8BAFF", "#E0BBE4", "#957DAD", "#D291BC", "#FEC8D8"
    ]
    
    cols_per_row = 2
    for i in range(0, len(todos), cols_per_row):
        row_items = todos[i : i + cols_per_row]
        cols = st.columns(cols_per_row)
        
        for col, item in zip(cols, row_items):
            with col:
                bg_color = random.choice(pastel_colors)
                st.markdown(
                    f"""
                    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin-bottom: 10px; color: #333; min-height: 150px;">
                        <h3 style="margin-top: 0;">{item['title']}</h3>
                        <p style="white-space: pre-wrap;">{item['content']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                if st.button("🗑️ 삭제", key=f"del_{item['id']}"):
                    delete_todo(item['id'])
                    st.rerun()