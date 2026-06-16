import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 1. ฟังก์ชันจัดการฐานข้อมูล (ปรับโครงสร้างเพื่อรองรับฟิลด์ใหม่)
def init_db():
    conn = sqlite3.connect('document_checklist_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_place TEXT,
            doc_id_text TEXT,
            fullname TEXT,
            doc_type TEXT,
            doc1_status TEXT,
            doc2_status TEXT,
            doc3_status TEXT,
            doc4_status TEXT,
            doc5_status TEXT,
            doc6_status TEXT,
            inspector TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสารบรรณ & Dashboard", layout="wide")
st.title("📑 ระบบบันทึกและตรวจเช็คสถานะเอกสารสารบรรณ")

# สร้างเมนูแท็บ (Tabs) แยกหน้าจอออกจากกัน
tab_form, tab_dashboard = st.tabs(["✍️ บันทึกข้อมูลเอกสาร", "📊 Dashboard & รายการทั้งหมด"])

# ==========================================
# 🟢 แท็บที่ 1: หน้าฟอร์มบันทึกข้อมูล (ปรับปรุงใหม่)
# ==========================================
with tab_form:
    st.subheader("กรอกข้อมูลการตรวจสอบเอกสาร")
    with st.form(key='checklist_form', clear_on_submit=True):
        
        st.write("**✍️ ส่วนที่ 1: ข้อมูลทั่วไปของเอกสาร**")
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่, หน่วยงานภายนอก")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
        with col2:
            fullname = st.text_input("ชื่อ - นามสกุล (ผู้ยื่นเอกสาร) *", placeholder="ระบุชื่อ-นามสกุล")
            doc_type = st.selectbox("ประเภทหนังสือ *", ["หนังสือภายนอก", "หนังสือภายใน", "หนังสือประทับตรา", "คำสั่ง/ประกาศ", "อื่นๆ"])
            
        st.write("---")
        st.write("**🔍 ส่วนที่ 2: ผลการตรวจสอบเอกสาร (ผ่าน / ไม่ผ่าน)**")
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
        st.write("**👤 ส่วนที่ 3: ข้อมูลผู้ตรวจสอบ**")
        inspector = st.text_input("ชื่อผู้ตรวจ *", placeholder="ระบุชื่อเจ้าหน้าที่ผู้ตรวจเช็ค")

        st.write("---")
        # ปุ่มบันทึกข้อมูล
        submit_button = st.form_submit_button(label='💾 บันทึกข้อมูล')

    if submit_button:
        # ตรวจสอบว่ากรอกข้อมูลจำเป็นครบถ้วนหรือไม่
        if not source_place or not doc_id_text or not fullname or not inspector:
            st.error("❌ กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วนก่อนทำการบันทึก")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_checklist_v2.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO checklists (source_place, doc_id_text, fullname, doc_type, doc1_status, doc2_status, doc3_status, doc4_status, doc5_status, doc6_status, inspector, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (source_place, doc_id_text, fullname, doc_type, doc1, doc2, doc3, doc4, doc5, doc6, inspector, current_time))
            conn.commit()
            conn.close()
            st.success(f"🎉 บันทึกข้อมูลของ คุณ {fullname} เรียบร้อยแล้ว! สามารถตรวจสอบรายงานได้ที่แท็บด้านบน")


# ==========================================
# 🔵 แท็บที่ 2: หน้า Dashboard & รายการแสดงข้อมูล
# ==========================================
with tab_dashboard:
    st.subheader("📊 สรุปผลภาพรวมและรายการข้อมูลทั้งหมด")
    
    # ดึงข้อมูลมาแสดงผล
    conn = sqlite3.connect('document_checklist_v2.db')
    df = pd.read_sql_query('''
        SELECT 
            source_place as 'แหล่งที่มา',
            doc_id_text as 'เลขหนังสือ', 
            fullname as 'ชื่อ-นามสกุล', 
            doc_type as 'ประเภท',
            doc1_status as 'เอกสาร 1', 
            doc2_status as 'เอกสาร 2', 
            doc3_status as 'เอกสาร 3', 
            doc4_status as 'เอกสาร 4', 
            doc5_status as 'เอกสาร 5', 
            doc6_status as 'เอกสาร 6',
            inspector as 'ชื่อผู้ตรวจ',
            timestamp as 'วันเวลาที่บันทึก'
        FROM checklists 
        ORDER BY id DESC
    ''', conn)
    conn.close()

    if not df.empty:
        # --- CARD สรุปสถิติด้านบน (KPI Metrics) ---
        total_records = len(df)
        
        # ค้นหาเคสที่ไม่ผ่าน (ตรวจสอบเอกสาร 1-6 ว่ามีแถวไหนมีคำว่า "ไม่ผ่าน" ไหม)
        failed_rows = df[df[['เอกสาร 1', 'เอกสาร 2', 'เอกสาร 3', 'เอกสาร 4', 'เอกสาร 5', 'เอกสาร 6']].eq('ไม่ผ่าน').any(axis=1)]
        total_failed = len(failed_rows)
        total_passed = total_records - total_failed

        m1, m2, m3 = st.columns(3)
        m1.metric(label="📈 จำนวนรายการที่บันทึกทั้งหมด", value=f"{total_records} รายการ")
        m2.metric(label="✅ ผ่านทุกเอกสาร", value=f"{total_passed} เคส")
        m3.metric(label="❌ มีเอกสารไม่ผ่าน", value=f"{total_failed} เคส")
        
        st.write("---")
        
        # --- ตารางแสดงข้อมูลและการค้นหา ---
        st.write("**📋 ตารางรายการแสดงข้อมูลทั้งหมด**")
        
        # กล่องค้นหาข้อมูลแบบครอบจักรวาล (ค้นหาตาม ชื่อ, เลขหนังสือ, หรือ แหล่งที่มาได้หมด)
        search_query = st.text_input("🔍 ค้นหาข้อมูล (ระบุ แหล่งที่มา / เลขหนังสือ / ชื่อ-นามสกุล / ชื่อผู้ตรวจ)")
        if search_query:
            filtered_df = df[
                df['แหล่งที่มา'].str.contains(search_query, case=False, na=False) | 
                df['เลขหนังสือ'].str.contains(search_query, case=False, na=False) | 
                df['ชื่อ-นามสกุล'].str.contains(search_query, case=False, na=False) |
                df['ชื่อผู้ตรวจ'].str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_df = df

        # แสดงตารางข้อมูลแบบเต็มจอ
        st.dataframe(filtered_df, use_container_width=True)
        
        # ปุ่มดาวน์โหลดไฟล์ CSV
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็นไฟล์ CSV (สำหรับเปิดใน Excel)",
            data=csv,
            file_name=f"รายงานสรุประบบเอกสารสารบรรณ_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    else:
        st.info("💡 ยังไม่มีข้อมูลในระบบ กรุณากรอกและบันทึกข้อมูลในแท็บ 'บันทึกข้อมูลเอกสาร' ก่อนครับ")
