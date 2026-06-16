import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 1. ฟังก์ชันจัดการฐานข้อมูล
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

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบสารบรรณ & Dashboard", layout="wide")
st.title("📑 ระบบบันทึกเอกสารสารบรรณ พร้อมระบบ Dashboard")

# 2. สร้างเมนูแท็บ (Tabs) แยกหน้าจอออกจากกันชัดเจน
tab_form, tab_dashboard = st.tabs(["✍️ บันทึกข้อมูลเอกสาร", "📊 Dashboard & รายการทั้งหมด"])

# ==========================================
# 🟢 แท็บที่ 1: หน้าฟอร์มบันทึกข้อมูล (ข้อมูลเดิม)
# ==========================================
with tab_form:
    st.subheader("กรอกข้อมูลการตรวจสอบเอกสาร")
    with st.form(key='checklist_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
        with col2:
            fullname = st.text_input("ชื่อ - นามสกุล *", placeholder="ชื่อผู้ยื่นเอกสาร")
            
        st.write("---")
        st.write("**ผลการตรวจสอบเอกสาร (ผ่าน / ไม่ผ่าน)**")
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
        submit_button = st.form_submit_button(label='💾 บันทึกข้อมูล')

    if submit_button:
        if not doc_id_text or not fullname:
            st.error("❌ กรุณากรอกเลขหนังสือและชื่อ-นามสกุลก่อนทำการบันทึก")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_checklist.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO checklists (doc_id_text, fullname, doc1_status, doc2_status, doc3_status, doc4_status, doc5_status, doc6_status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (doc_id_text, fullname, doc1, doc2, doc3, doc4, doc5, doc6, current_time))
            conn.commit()
            conn.close()
            st.success(f"🎉 บันทึกข้อมูลของ คุณ {fullname} เรียบร้อยแล้ว! (กรุณาไปดูที่แท็บ Dashboard เพื่อดูรายงาน)")


# ==========================================
# 🔵 แท็บที่ 2: หน้า Dashboard & รายการแสดงข้อมูล
# ==========================================
with tab_dashboard:
    st.subheader("📊 สรุปผลภาพรวมและรายการข้อมูลทั้งหมด")
    
    # ดึงข้อมูลจากฐานข้อมูลมาคำนวณ
    conn = sqlite3.connect('document_checklist.db')
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
        # --- ส่วนของ CARD สรุปสถิติด้านบน (KPI Metrics) ---
        total_records = len(df)
        
        # ค้นหาคนที่มี "ไม่ผ่าน" ในเอกสารใดๆ เลย
        # หากแถวใดมีคำว่า "ไม่ผ่าน" โผล่ขึ้นมา จะถือว่าคนนั้นไม่ผ่านภาพรวม
        failed_rows = df[df[['เอกสาร 1', 'เอกสาร 2', 'เอกสาร 3', 'เอกสาร 4', 'เอกสาร 5', 'เอกสาร 6']].eq('ไม่ผ่าน').any(axis=1)]
        total_failed = len(failed_rows)
        total_passed = total_records - total_failed

        # แสดงกล่องตัวเลขสถิติสวยๆ
        m1, m2, m3 = st.columns(3)
        m1.metric(label="📈 จำนวนรายการที่บันทึกทั้งหมด", value=f"{total_records} รายการ")
        m2.metric(label="✅ ตรวจสอบแล้ว 'ผ่านทุกเอกสาร'", value=f"{total_passed} คน", delta_color="normal")
        m3.metric(label="❌ มีเอกสาร 'ไม่ผ่าน'", value=f"{total_failed} คน")
        
        st.write("---")
        
        # --- ส่วนของกราฟสรุปสถิติแยกตามประเภทเอกสาร ---
        st.write("**📊 สถิติผลการตรวจแยกตามหัวข้อเอกสาร (จำนวนที่ผ่าน)**")
        
        # นับจำนวนคำว่า "ผ่าน" ในแต่ละคอลัมน์ของเอกสาร 1-6
        doc_cols = ['เอกสาร 1', 'เอกสาร 2', 'เอกสาร 3', 'เอกสาร 4', 'เอกสาร 5', 'เอกสาร 6']
        passed_counts = [df[col].value_counts().get('ผ่าน', 0) for col in doc_cols]
        
        # ทำมินิกราฟแท่งแสดงจำนวนที่ผ่านง่ายๆ
        chart_data = pd.DataFrame({
            'ประเภทเอกสาร': doc_cols,
            'จำนวนที่ผ่าน (คน)': passed_counts
        })
        st.bar_chart(chart_data, x='ประเภทเอกสาร', y='จำนวนที่ผ่าน (คน)')

        st.write("---")

        # --- ส่วนของตารางแสดงข้อมูล (Data Table) ---
        st.write("**📋 ตารางรายการแสดงข้อมูลทั้งหมด**")
        
        # ใส่กล่องค้นหา (Search Box) เผื่อค้นหาตามชื่อ หรือ เลขหนังสือ
        search_query = st.text_input("🔍 ค้นหาด้วย เลขหนังสือ หรือ ชื่อ-นามสกุล")
        if search_query:
            filtered_df = df[df['เลขหนังสือ'].str.contains(search_query, case=False, na=False) | 
                             df['ชื่อ-นามสกุล'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df

        # แสดงตารางข้อมูล
        st.dataframe(filtered_df, use_container_width=True)
        
        # ปุ่มดาวน์โหลดไฟล์
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็นไฟล์ CSV",
            data=csv,
            file_name=f"รายงานสรุปเอกสาร_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    else:
        st.info("💡 ยังไม่มีข้อมูลในระบบ กรุณากรอกและบันทึกข้อมูลในแท็บ 'บันทึกข้อมูลเอกสาร' ก่อนครับ")
