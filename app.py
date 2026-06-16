import streamlit as st
import sqlite3
from datetime import datetime

# 1. ฟังก์ชันจัดการฐานข้อมูล (SQLite)
def init_db():
    conn = sqlite3.connect('saraban.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS inbound_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receive_no TEXT,
            receive_date TEXT,
            doc_no TEXT,
            doc_date TEXT,
            title TEXT,
            source_org TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 2. ฟังก์ชันคำนวณและรันเลขรับอัตโนมัติ
def generate_receive_no():
    current_year_th = datetime.now().year + 543
    conn = sqlite3.connect('saraban.db')
    c = conn.cursor()
    
    # ค้นหาเลขรับล่าสุดของปีปัจจุบัน
    c.execute("SELECT receive_no FROM inbound_docs WHERE receive_no LIKE ? ORDER BY id DESC LIMIT 1", (f"%/{current_year_th}",))
    row = c.fetchone()
    
    next_num = 1
    if row:
        last_receive_no = row[0]
        last_num = int(last_receive_no.split('/')[0])
        next_num = last_num + 1
        
    conn.close()
    return f"{str(next_num).zfill(4)}/{current_year_th}"

# เริ่มต้นระบบฐานข้อมูล
init_db()

# 3. ส่วนหน้าตาเว็บ (UI ด้วย Streamlit)
st.title("📝 ระบบลงทะเบียนรับเอกสารสารบรรณ")
st.subheader("เวอร์ชัน Streamlit")

# สร้างฟอร์มรับข้อมูล
with st.form(key='saraban_form', clear_on_submit=True):
    doc_no = st.text_input("เลขที่หนังสือภายนอก (ที่ระบุบนหัวกระดาษ) *")
    doc_date = st.date_input("วันที่ในหนังสือ")
    title = st.text_input("เรื่อง / ชื่อหนังสือ *")
    source_org = st.text_input("จากหน่วยงาน *")
    
    submit_button = st.form_submit_submit_button(label='ลงรับเอกสาร')

# เมื่อผู้ใช้กดปุ่มส่งฟอร์ม
if submit_button:
    if not doc_no or not title or not source_org:
        st.error("❌ กรุณากรอกข้อมูลช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
    else:
        # เจนเลขรับและบันทึกข้อมูล
        rec_no = generate_receive_no()
        rec_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('saraban.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO inbound_docs (receive_no, receive_date, doc_no, doc_date, title, source_org)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (rec_no, rec_date, doc_no, str(doc_date), title, source_org))
        conn.commit()
        conn.close()
        
        st.success(f"🎉 ลงรับเอกสารสำเร็จ! เลขรับของคุณคือ: **{rec_no}**")

# --- ส่วนแสดงผลตารางข้อมูลที่รับแล้ว ---
st.write("---")
st.subheader("📋 รายการหนังสือที่ลงรับแล้ว")
conn = sqlite3.connect('saraban.db')
import pandas as pd
df = pd.read_sql_query("SELECT receive_no as 'เลขรับ', receive_date as 'วันเวลาที่รับ', doc_no as 'เลขที่หนังสือ', title as 'เรื่อง', source_org as 'จากหน่วยงาน' FROM inbound_docs ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลการลงรับเอกสารในระบบ")
