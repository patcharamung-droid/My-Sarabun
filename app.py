import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 1. จัดการฐานข้อมูล (ปรับรองรับสถานะการตรวจรวม: รอตรวจยืนยัน / อนุมัติ / ไม่อนุมัติ / ยกเลิก)
def init_db():
    conn = sqlite3.connect('document_management_v5.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS docs_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_place TEXT,
            doc_id_text TEXT,
            fullname TEXT,
            doc_type TEXT,
            creator_name TEXT,
            doc1_status TEXT, doc1_note TEXT,
            doc2_status TEXT, doc2_note TEXT,
            doc3_status TEXT, doc3_note TEXT,
            doc4_status TEXT, doc4_note TEXT,
            doc5_status TEXT, doc5_note TEXT,
            doc6_status TEXT, doc6_note TEXT,
            inspector_name TEXT DEFAULT 'ยังไม่ได้ตรวจ',
            check_status TEXT DEFAULT 'รอตรวจเอกสาร', -- รอตรวจเอกสาร / อนุมัติ / ไม่อนุมัติ / ยกเลิก
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="ระบบงานสารบรรณ", layout="wide")
st.title("📑 ระบบบันทึกและตรวจสอบเอกสารสารบรรณ")

# แถบ sidebar สำหรับสลับหน้าผู้ใช้งาน
st.sidebar.title("🔐 สิทธิ์การใช้งานระบบ")
user_role = st.sidebar.radio("เลือกสถานะของคุณ:", ["📝 ผู้บันทึกข้อมูล", "🔍 ผู้ตรวจสอบเอกสาร"])

status_options = ["ผ่าน", "ไม่ผ่าน"]

# ฟังก์ชันสำหรับช่วยเจนช่องตรวจเอกสารแนวนอน (ฝั่งผู้บันทึก)
def render_doc_row(label):
    c_status, c_note = st.columns([1, 2])
    with c_status:
        status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
    with c_note:
        note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียดของ {label} (ถ้ามี)", key=f"note_{label}")
    return status, note


# ==========================================
# 🟢 ส่วนของ: 📝 ผู้บันทึกข้อมูล
# ==========================================
if user_role == "📝 ผู้บันทึกข้อมูล":
    st.header("✍ *ฝั่งผู้บันทึกข้อมูล*")
    
    if 'visible_docs' not in st.session_state:
        st.session_state.visible_docs = 3

    with st.form(key='creator_form_v5'):
        st.subheader("1. ข้อมูลทั่วไป")
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่, หน่วยงานภายนอก")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
            creator_name = st.text_input("ชื่อผู้บันทึกข้อมูล *", placeholder="ระบุชื่อเจ้าหน้าที่ผู้บันทึก")
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="เช่น ขออนุมัติโครงการ, ขอย้ายตำแหน่ง")
            
        st.write("---")
        st.subheader("2. ตรวจสอบเอกสารแนบ")
        
        doc1_status, doc1_note = render_doc_row("📄 เอกสาร 1")
        doc2_status, doc2_note = render_doc_row("📄 เอกสาร 2")
        doc3_status, doc3_note = render_doc_row("📄 เอกสาร 3")
        
        doc4_status, doc4_note = "ไม่ได้ระบุ", ""
        doc5_status, doc5_note = "ไม่ได้ระบุ", ""
        doc6_status, doc6_note = "ไม่ได้ระบุ", ""
        
        if st.session_state.visible_docs >= 4:
            doc4_status, doc4_note = render_doc_row("📄 เอกสาร 4")
        if st.session_state.visible_docs >= 5:
            doc5_status, doc5_note = render_doc_row("📄 เอกสาร 5")
        if st.session_state.visible_docs == 6:
            doc6_status, doc6_note = render_doc_row("📄 เอกสาร 6")
            
        st.write("---")
        submit_button = st.form_submit_button(label='💾 บันทึกและส่งข้อมูลให้ผู้ตรวจ')

    if st.session_state.visible_docs < 6:
        if st.button("➕ เพิ่มช่องตรวจเอกสารลำดับถัดไป"):
            st.session_state.visible_docs += 1
            st.rerun()

    if submit_button:
        if not source_place or not doc_id_text or not fullname or not doc_type or not creator_name:
            st.error("❌ กรุณากรอกข้อมูลทั่วไปและชื่อผู้บันทึกให้ครบถ้วน")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_management_v5.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO docs_pool (
                    source_place, doc_id_text, fullname, doc_type, creator_name,
                    doc1_status, doc1_note, doc2_status, doc2_note,
                    doc3_status, doc3_note, doc4_status, doc4_note,
                    doc5_status, doc5_note, doc6_status, doc6_note,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_place, doc_id_text, fullname, doc_type, creator_name,
                doc1_status, doc1_note, doc2_status, doc2_note,
                doc3_status, doc3_note, doc4_status, doc4_note,
                doc5_status, doc5_note, doc6_status, doc6_note,
                current_time
            ))
            conn.commit()
            conn.close()
            
            st.session_state.visible_docs = 3
            st.success(f"🎉 บันทึกข้อมูลส่งต่อเรียบร้อยแล้ว!")
            st.rerun()


# ==========================================
# 🔵 ส่วนของ: 🔍 ผู้ตรวจสอบเอกสาร (อัปเกรดใหม่ยกชุด)
# ==========================================
else:
    st.header("🔍 *ฝั่งผู้ตรวจสอบเอกสารและลงนาม*")
    
    # ดึงข้อมูลล่าสุดจาก DB
    conn = sqlite3.connect('document_management_v5.db')
    df_all = pd.read_sql_query("SELECT * FROM docs_pool ORDER BY id DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบ")
    else:
        # --- 1. ส่วนของ DASHBOARD แสดงผลสถิติแยกสถานะ ---
        st.subheader("📊 Dashboard สถานะการตรวจสอบภาพรวม")
        
        # คำนวณยอดรวมของแต่ละสถานะตามโจทย์
        count_waiting = len(df_all[df_all['check_status'] == 'รอตรวจเอกสาร'])
        count_approved = len(df_all[df_all['check_status'] == 'อนุมัติ'])
        count_rejected = len(df_all[df_all['check_status'] == 'ไม่อนุมัติ'])
        count_canceled = len(df_all[df_all['check_status'] == 'ยกเลิก'])
        
        # วางกล่องสถิติเรียงแนวนอน 4 กล่องสวยงาม
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="⏳ รอตรวจเอกสาร", value=f"{count_waiting} รายการ")
        m2.metric(label="🟢 อนุมัติแล้ว", value=f"{count_approved} รายการ")
        m3.metric(label="🔴 ไม่อนุมัติ", value=f"{count_rejected} รายการ")
        m4.metric(label="⚪ ยกเลิก", value=f"{count_canceled} รายการ")
        
        st.write("---")
        
        # --- 2. แสดงรายการทั้งหมดเป็นตารางตรงกลางหน้าจอตามโจทย์ข้อ 1 ---
        st.subheader("📋 รายการข้อมูลเอกสารทั้งหมดในระบบ")
        
        # คัดและแต่งชื่อคอลัมน์ให้อ่านง่าย
        display_df = df_all[[
            'id', 'source_place', 'doc_id_text', 'fullname', 'doc_type', 'creator_name',
            'inspector_name', 'check_status', 'timestamp'
        ]].copy()
        display_df.columns = [
            'ID', 'แหล่งที่มา', 'เลขหนังสือ', 'ชื่อ-สกุลผู้ยื่น', 'ประเภทคำขอ', 'ผู้บันทึก',
            'ผู้ตรวจรับรอง', 'สถานะปัจจุบัน', 'วันเวลาที่บันทึก'
        ]
        
        # โชว์ตารางแบบกว้างเต็มหน้าจอ
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.write("---")
        
        # --- 3. ฟอร์มตรวจรับรองด้านล่างเมื่อคลิกเลือกตามโจทย์ข้อ 3 ---
        st.subheader("✒️ ทำการตรวจสอบและลงชื่อรับรองเอกสาร")
        
        # ตัวเลือกงานโดยอิงจาก ID และเลขหนังสือในตารางด้านบน
        doc_list = [f"{row['id']} - เลขหนังสือ: {row['doc_id_text']} ({row['fullname']})" for _, row in df_all.iterrows()]
        selected_doc = st.selectbox("เลือกรายการที่ต้องการคลิกตรวจประเมิน/ลงชื่อบันทึก:", doc_list)
        
        # แกะข้อมูลชิ้นที่เลือกออกมาแสดงผล
        selected_id = int(selected_doc.split(" - ")[0])
        doc_data = df_all[df_all['id'] == selected_id].iloc[0]
        
        # แบ่งหน้าจอแสดงผลดีเทลเอกสาร 1-6 และฟอร์มเซ็นชื่อ
        col_detail, col_form = st.columns([1, 1])
        
        with col_detail:
            st.markdown(f"**📄 ผลการตรวจเช็คไฟล์แนบ (จากผู้บันทึก):**")
            for i in range(1, 7):
                status = doc_data[f'doc{i}_status']
                note = doc_data[f'doc{i}_note']
                if status != "ไม่ได้ระบุ":
                    note_text = f" (หมายเหตุ: {note})" if note else ""
                    icon = "✅" if status == "ผ่าน" else "❌"
                    st.write(f"{icon} เอกสาร {i}: **{status}**{note_text}")
                    
        with col_form:
            # ฟอร์มลงชื่อและปรับสถานะภาพรวมของหนังสือ
            with st.form(key='approval_form_v5'):
                st.markdown("**✍️ บันทึกผลตรวจรับรอง:**")
                
                # ตั้งค่า Default Index ของปุ่มตามค่าเดิมในฐานข้อมูล
                current_status = doc_data['check_status']
                status_list = ["รอตรวจเอกสาร", "อนุมัติ", "ไม่อนุมัติ", "ยกเลิก"]
                try:
                    def_index = status_list.index(current_status)
                except:
                    def_index = 0
                    
                # ส่วนปรับสถานะภาพรวม
                final_status = st.selectbox("ปรับสถานะเอกสารภาพรวม *", status_list, index=def_index)
                
                # ส่วนกรอกชื่อผู้ตรวจ
                inspector_input = st.text_input(
                    "ชื่อผู้ตรวจสอบ / ลงชื่อผู้ตรวจรับรอง *", 
                    value="" if doc_data['inspector_name'] == "ยังไม่ได้ตรวจ" else doc_data['inspector_name']
                )
                
                approve_button = st.form_submit_button(label="💾 บันทึกผลและลงชื่อรับรอง")
                
            if approve_button:
                if not inspector_input:
                    st.error("❌ กรุณากรอกชื่อผู้ตรวจรับรองเพื่อบันทึกข้อมูลเข้าสู่ระบบ")
                else:
                    conn = sqlite3.connect('document_management_v5.db')
                    c = conn.cursor()
                    c.execute('''
                        UPDATE docs_pool 
                        SET inspector_name=?, check_status=? 
                        WHERE id=?
                    ''', (inspector_input, final_status, selected_id))
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 อัปเดตสถานะของหนังสือเป็น '{final_status}' และบันทึกชื่อผู้ตรวจเรียบร้อยแล้ว!")
                    st.rerun()
