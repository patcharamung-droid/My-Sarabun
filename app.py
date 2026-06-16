import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 1. ฟังก์ชันจัดการฐานข้อมูล (รองรับการเก็บผลตรวจ ผ่าน/ไม่ผ่าน ทั้ง 6 เอกสาร)
def init_db():
    conn = sqlite3.connect('document_checklist.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id_text TEXT,
            fullname TEXT,
            doc1_status TEXT,
            doc2_status TEXT,
            doc3_status TEXT,
            doc4_status TEXT,
            doc5_status TEXT,
            doc6_status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ส่วนหัวของระบบ
st.set_page_config(page_title="ระบบตรวจเช็คเอกสารสารบรรณ", layout="wide")
st.title("📑 ระบบบันทึกและตรวจเช็คสถานะเอกสาร")
st.write("กรุณากรอกข้อมูลเลขหนังสือ ชื่อ-นามสกุล และเลือกสถานะการตรวจสอบเอกสารให้ครบถ้วน")

# 2. ฟอร์มสำหรับบันทึกข้อมูล
with st.form(key='checklist_form', clear_on_submit=True):
    st.subheader("✍️ ส่วนที่ 1: ข้อมูลทั่วไป")
    col1, col2 = st.columns(2)
    with col1:
        doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
    with col2:
        fullname = st.text_input("ชื่อ - นามสกุล *", placeholder="ชื่อผู้ยื่นเอกสาร")
        
    st.write("---")
    st.subheader("🔍 ส่วนที่ 2: ผลการตรวจสอบเอกสาร")
    
    # สร้างแถวสำหรับการเลือก ผ่าน / ไม่ผ่าน ของเอกสารทั้ง 6 ฉบับ
    # ใช้ st.radio แนวราบ (horizontal) เพื่อประหยัดพื้นที่และเลือกได้แค่อย่างใดอย่างหนึ่ง
    status_options = ["ผ่าน", "ไม่ผ่าน"]
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        doc1 = st.radio("📄 เอกสาร 1", status_options, index=0, horizontal=True)
        doc2 = st.radio("📄 เอกสาร 2", status_options, index=0, horizontal=True)
        doc3 = st.radio("📄 เอกสาร 3", status_options, index=0, horizontal=True)
        
    with col_b:
        doc4 = st.radio("📄 เอกสาร 4", status_options, index=0, horizontal=True)
        doc5 = st.radio("📄 เอกสาร 5", status_options, index=0, horizontal=True)
        doc6 = st.radio("📄 เอกสาร 6", status_options, index=0, horizontal=True)

    st.write("---")
    # 3. ปุ่มบันทึกข้อมูลด้านล่างสุด
    submit_button = st.form_submit_button(label='💾 บันทึกข้อมูล')

# กระบวนการหลังกดปุ่มบันทึก
if submit_button:
    if not doc_id_text or not fullname:
        st.error("❌ กรุณากรอกเลขหนังสือและชื่อ-นามสกุลก่อนทำการบันทึก")
    else:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # บันทึกลงฐานข้อมูล SQLite
        conn = sqlite3.connect('document_checklist.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO checklists (doc_id_text, fullname, doc1_status, doc2_status, doc3_status, doc4_status, doc5_status, doc6_status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (doc_id_text, fullname, doc1, doc2, doc3, doc4, doc5, doc6, current_time))
        conn.commit()
        conn.close()
        
        st.success(f"🎉 บันทึกข้อมูลของ คุณ {fullname} (เลขหนังสือ: {doc_id_text}) เรียบร้อยแล้ว!")

# --- ส่วนแสดงผลตารางข้อมูลที่บันทึกแล้วด้านล่างระบบ ---
st.write("---")
st.subheader("📋 รายงานข้อมูลที่บันทึกแล้ว")

conn = sqlite3.connect('document_checklist.db')
# ดึงข้อมูลมาแสดงผลในรูปแบบตารางที่ดูง่าย
df = pd.read_sql_query('''
    SELECT 
        doc_id_text as 'เลขหนังสือ', 
        fullname as 'ชื่อ-นามสกุล', 
        doc1_status as 'เอกสาร 1', 
        doc2_status as 'เอกสาร 2', 
        doc3_status as 'เอกสาร 3', 
        doc4_status as 'เอกสาร 4', 
        doc5_status as 'เอกสาร 5', 
        doc6_status as 'เอกสาร 6',
        timestamp as 'วันเวลาที่บันทึก'
    FROM checklists 
    ORDER BY id DESC
''', conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # แถมปุ่มดาวน์โหลดเป็นไฟล์ Excel/CSV เผื่อนำไปส่งต่อให้หัวหน้างาน
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดรายงานทั้งหมดเป็นไฟล์ CSV (เปิดใน Excel ได้)",
        data=csv,
        file_name=f"รายงานตรวจเช็คเอกสาร_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )
else:
    st.info("ยังไม่มีข้อมูลการบันทึกในระบบ")
