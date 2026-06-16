import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 1. จัดการฐานข้อมูล (ปรับโครงสร้างให้เก็บสถานะและหมายเหตุแยกแต่ละเอกสาร)
def init_db():
    conn = sqlite3.connect('document_management_v3.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS docs_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_place TEXT,
            doc_id_text TEXT,
            fullname TEXT,
            doc_type TEXT,
            doc1_status TEXT, doc1_note TEXT,
            doc2_status TEXT, doc2_note TEXT,
            doc3_status TEXT, doc3_note TEXT,
            doc4_status TEXT, doc4_note TEXT,
            doc5_status TEXT, doc5_note TEXT,
            doc6_status TEXT, doc6_note TEXT,
            inspector_name TEXT DEFAULT 'ยังไม่ได้ตรวจ',
            check_status TEXT DEFAULT 'รอตรวจยืนยัน',
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

# ==========================================
# 🟢 ส่วนของ: 📝 ผู้บันทึกข้อมูล
# ==========================================
if user_role == "📝 ผู้บันทึกข้อมูล":
    st.header("✍️ ฟอร์มบันทึกข้อมูลและตรวจสอบเอกสารเบื้องต้น")
    
    with st.form(key='creator_form_v3'):
        st.subheader("1. ข้อมูลทั่วไป")
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่, หน่วยงานภายนอก")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="เช่น ขออนุมัติโครงการ, ขอย้ายตำแหน่ง")
            
        st.write("---")
        st.subheader("2. ตรวจสอบเอกสารแนบ 1 - 6")
        
        # ฟังก์ชันช่วยสร้างแถวตรวจเอกสาร (มีปุ่มผ่าน/ไม่ผ่าน + ช่องหมายเหตุขนานกันไป)
        def render_doc_row(label):
            c_status, c_note = st.columns([1, 2])
            with c_status:
                status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
            with c_note:
                note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียดของ {label} (ถ้ามี)", key=f"note_{label}")
            return status, note

        doc1_status, doc1_note = render_doc_row("📄 เอกสาร 1")
        doc2_status, doc2_note = render_doc_row("📄 เอกสาร 2")
        doc3_status, doc3_note = render_doc_row("📄 เอกสาร 3")
        doc4_status, doc4_note = render_doc_row("📄 เอกสาร 4")
        doc5_status, doc5_note = render_doc_row("📄 เอกสาร 5")
        doc6_status, doc6_note = render_doc_row("📄 เอกสาร 6")
        
        st.write("---")
        submit_button = st.form_submit_button(label='💾 บันทึกและส่งข้อมูลให้ผู้ตรวจ')

    if submit_button:
        if not source_place or not doc_id_text or not fullname or not doc_type:
            st.error("❌ กรุณากรอกข้อมูลทั่วไปที่มีเครื่องหมาย * ให้ครบถ้วนก่อนบันทึก")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_management_v3.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO docs_pool (
                    source_place, doc_id_text, fullname, doc_type,
                    doc1_status, doc1_note, doc2_status, doc2_note,
                    doc3_status, doc3_note, doc4_status, doc4_note,
                    doc5_status, doc5_note, doc6_status, doc6_note,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_place, doc_id_text, fullname, doc_type,
                doc1_status, doc1_note, doc2_status, doc2_note,
                doc3_status, doc3_note, doc4_status, doc4_note,
                doc5_status, doc5_note, doc6_status, doc6_note,
                current_time
            ))
            conn.commit()
            conn.close()
            st.success(f"🎉 บันทึกข้อมูลและสถานะเอกสารของ คุณ {fullname} เรียบร้อยแล้ว! ส่งต่อให้ผู้ตรวจพิจารณาสำเร็จ")


# ==========================================
# 🔵 ส่วนของ: 🔍 ผู้ตรวจสอบเอกสาร
# ==========================================
else:
    st.header("🔍 เมนูสำหรับผู้ตรวจสอบ (ลงชื่อตรวจยืนยัน)")
    
    conn = sqlite3.connect('document_management_v3.db')
    df_all = pd.read_sql_query("SELECT * FROM docs_pool ORDER BY id DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบ")
    else:
        col_action, col_table = st.columns([1, 2])
        
        # ฝั่งซ้าย: เลือกรายการเพื่อลงชื่อผู้ตรวจ
        with col_action:
            st.subheader("✍️ ลงชื่อตรวจรับรอง")
            
            # ดึงเฉพาะรายการที่สถานะยังไม่ได้ตรวจเสร็จสิ้นขึ้นมาให้เลือกเป็นอันดับแรก
            doc_list = [f"{row['id']} - เลขหนังสือ: {row['doc_id_text']} ({row['fullname']})" for _, row in df_all.iterrows()]
            selected_doc = st.selectbox("เลือกรายการที่จะเซ็นชื่อตรวจ:", doc_list)
            
            selected_id = int(selected_doc.split(" - ")[0])
            doc_data = df_all[df_all['id'] == selected_id].iloc[0]
            
            st.write("---")
            st.markdown(f"📁 **รายละเอียด:** {doc_data['doc_id_text']} | **ประเภท:** {doc_data['doc_type']}")
            st.markdown(f"👤 **ผู้ยื่นคำขอ:** {doc_data['fullname']} | **แหล่งที่มา:** {doc_data['source_place']}")
            
            # แสดงผลการตรวจเบื้องต้นที่ผู้บันทึกกรอกมา
            st.write("**📋 ผลตรวจเบื้องต้นจากผู้บันทึก:**")
            for i in range(1, 7):
                status = doc_data[f'doc{i}_status']
                note = doc_data[f'doc{i}_note']
                note_text = f" (หมายเหตุ: {note})" if note else ""
                icon = "✅" if status == "ผ่าน" else "❌"
                st.write(f"{icon} เอกสาร {i}: **{status}**{note_text}")
            
            st.write("---")
            
            # ฟอร์มลงชื่อผู้ตรวจ
            with st.form(key='approval_form'):
                inspector_input = st.text_input("ชื่อผู้ตรวจสอบ / ลงชื่อผู้ตรวจ *", value="" if doc_data['inspector_name'] == "ยังไม่ได้ตรวจ" else doc_data['inspector_name'])
                approve_button = st.form_submit_button(label="✒️ ยืนยันและลงชื่อผู้ตรวจ")
                
            if approve_button:
                if not inspector_input:
                    st.error("❌ กรุณากรอกชื่อผู้ตรวจเพื่อใช้ในการยืนยัน")
                else:
                    conn = sqlite3.connect('document_management_v3.db')
                    c = conn.cursor()
                    c.execute('''
                        UPDATE docs_pool 
                        SET inspector_name=?, check_status='ตรวจแล้ว'
                        WHERE id=?
                    ''', (inspector_input, selected_id))
                    conn.commit()
                    conn.close()
                    st.success("🎉 ลงชื่อผู้ตรวจรับรองเอกสารชุดนี้สำเร็จเรียบร้อย!")
                    st.rerun()

        # ฝั่งขวา: แดชบอร์ดแสดงผลตารางรายการทั้งหมด
        with col_table:
            st.subheader("📋 รายการและสถานะทั้งหมดในระบบ")
            
            # ทำฟิลเตอร์ค้นหาอย่างง่าย
            search_query = st.text_input("🔍 พิมพ์คำค้นหา (ชื่อผู้ยื่น / เลขหนังสือ / ประเภทคำขอ)")
            
            # เลือกคอลัมน์ที่จะแสดงบนตารางให้กระชับและตรงตามความต้องการ
            display_df = df_all[[
                'source_place', 'doc_id_text', 'fullname', 'doc_type',
                'doc1_status', 'doc1_note', 'doc2_status', 'doc2_note',
                'doc3_status', 'doc3_note', 'doc4_status', 'doc4_note',
                'doc5_status', 'doc5_note', 'doc6_status', 'doc6_note',
                'inspector_name', 'check_status', 'timestamp'
            ]].copy()
            
            display_df.columns = [
                'แหล่งที่มา', 'เลขหนังสือ', 'ชื่อ-สกุลผู้ยื่น', 'ประเภทคำขอ',
                'เอกสาร 1', 'หมายเหตุ 1', 'เอกสาร 2', 'หมายเหตุ 2',
                'เอกสาร 3', 'หมายเหตุ 3', 'เอกสาร 4', 'หมายเหตุ 4',
                'เอกสาร 5', 'หมายเหตุ 5', 'เอกสาร 6', 'หมายเหตุ 6',
                'ชื่อผู้ตรวจ', 'สถานะตรวจสอบ', 'วันเวลาที่บันทึก'
            ]
            
            if search_query:
                filtered_df = display_df[
                    display_df['ชื่อ-สกุลผู้ยื่น'].str.contains(search_query, case=False, na=False) |
                    display_df['เลขหนังสือ'].str.contains(search_query, case=False, na=False) |
                    display_df['ประเภทคำขอ'].str.contains(search_query, case=False, na=False)
                ]
            else:
                filtered_df = display_df
                
            st.dataframe(filtered_df, use_container_width=True)
            
            # ปุ่ม Export ไปเปิดใน Excel
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดรายการทั้งหมดเป็นไฟล์ CSV",
                data=csv,
                file_name=f"รายงานระบบสารบรรณ_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
