import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from streamlit_signature_pad import st_signature_pad

# 1. จัดการฐานข้อมูล (ปรับโครงสร้างเพื่อรองรับสถานะการตรวจและลายเซ็น)
def init_db():
    conn = sqlite3.connect('document_flow_system.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_place TEXT,
            doc_id_text TEXT,
            fullname TEXT,
            doc_type TEXT,
            creator_signature TEXT, -- เก็บภาพลายเซ็นผู้บันทึกเป็น Base64
            doc1_status TEXT DEFAULT 'รอการตรวจ',
            doc2_status TEXT DEFAULT 'รอการตรวจ',
            doc3_status TEXT DEFAULT 'รอการตรวจ',
            doc4_status TEXT DEFAULT 'รอการตรวจ',
            doc5_status TEXT DEFAULT 'รอการตรวจ',
            doc6_status TEXT DEFAULT 'รอการตรวจ',
            inspector TEXT DEFAULT 'ยังไม่ได้ตรวจ',
            check_status TEXT DEFAULT 'รอดำเนินการ', -- รอดำเนินการ / ตรวจเสร็จแล้ว
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="ระบบสารบรรณแยกสิทธิ์", layout="wide")
st.title("📑 ระบบบันทึกและตรวจเช็คเอกสารสารบรรณ (แยกสิทธิ์ผู้ใช้)")

# 2. แถบเลือกสิทธิ์ผู้ใช้งานที่แถบข้าง (Sidebar) เพื่อจำลองการเข้าระบบ
st.sidebar.title("🔐 เลือกสถานะผู้ใช้งาน")
user_role = st.sidebar.radio("ตำแหน่งของคุณ:", ["📝 ผู้บันทึกข้อมูล", "🔍 ผู้ตรวจสอบเอกสาร"])

# ==========================================
# 🟢 ส่วนของ: 📝 ผู้บันทึกข้อมูล
# ==========================================
if user_role == "📝 ผู้บันทึกข้อมูล":
    st.header("✍️ ฟอร์มบันทึกข้อมูลเอกสารเข้าใหม่")
    
    with st.form(key='creator_form'):
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่, หน่วยงานภายนอก")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
        with col2:
            fullname = st.text_input("ชื่อ - นามสกุล (ผู้ยื่นเอกสาร) *", placeholder="ระบุชื่อ-นามสกุล")
            doc_type = st.selectbox("ประเภทหนังสือ *", ["หนังสือภายนอก", "หนังสือภายใน", "หนังสือประทับตรา", "คำสั่ง/ประกาศ", "อื่นๆ"])
            
        st.write("---")
        st.write("✍️ **ลงลายมือชื่อผู้บันทึกด้านล่างนี้ (ใช้เมาส์หรือนิ้วลากเซ็นได้เลย):**")
        
        # กล่องสำหรับเซ็นลายเซ็น
        signature = st_signature_pad(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_color="black",
            scale=1,
            key="creator_sig",
            height=150
        )
        
        st.write("---")
        submit_button = st.form_submit_button(label='💾 บันทึกและส่งตรวจ')

    if submit_button:
        if not source_place or not doc_id_text or not fullname:
            st.error("❌ กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบถ้วน")
        elif signature is None:
            st.error("❌ กรุณาเซ็นลายมือชื่อผู้บันทึกก่อนกดบันทึก")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_flow_system.db')
            c = conn.cursor()
            
            # บันทึกข้อมูลเริ่มต้น เอกสาร 1-6 จะถูกเซ็ตค่าเริ่มต้นเป็น 'รอการตรวจ'
            c.execute('''
                INSERT INTO documents (source_place, doc_id_text, fullname, doc_type, creator_signature, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source_place, doc_id_text, fullname, doc_type, signature, current_time))
            conn.commit()
            conn.close()
            st.success(f"🎉 บันทึกหนังสือเลขที่ {doc_id_text} และส่งไปยังผู้ตรวจเรียบร้อยแล้ว!")


# ==========================================
# 🔵 ส่วนของ: 🔍 ผู้ตรวจสอบเอกสาร
# ==========================================
else:
    st.header("📊 เมนูรายการทั้งหมดและการตรวจประเมิน")
    
    conn = sqlite3.connect('document_flow_system.db')
    df_all = pd.read_sql_query("SELECT * FROM documents ORDER BY id DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีเอกสารที่ถูกบันทึกเข้ามาในระบบ")
    else:
        # แบ่งสัดส่วนหน้าจอ: ซ้ายเลือกรายการตรวจ / ขวาแสดงตารางแดชบอร์ด
        col_action, col_table = st.columns([1, 2])
        
        with col_action:
            st.subheader("🔍 เลือกรายการเพื่อทำการตรวจ")
            
            # ดึงรายการเลขหนังสือที่ยังไม่ตรวจ หรือ ตรวจแล้ว มาให้เลือกใน Dropdown
            doc_list = [f"{row['id']} - {row['doc_id_text']} ({row['fullname']})" for _, row in df_all.iterrows()]
            selected_doc = st.selectbox("เลือกเอกสารที่ต้องการตรวจ:", doc_list)
            
            # ดึง ID ออกมาจากข้อความที่เลือก
            selected_id = int(selected_doc.split(" - ")[0])
            doc_data = df_all[df_all['id'] == selected_id].iloc[0]
            
            st.write("---")
            st.info(f"📁 **รายละเอียดหนังสือ:** {doc_data['doc_id_text']} \n\n👤 **ผู้ยื่น:** {doc_data['fullname']}")
            
            # แสดงลายเซ็นผู้บันทึกให้ผู้ตรวจเห็น
            if doc_data['creator_signature']:
                st.write("**🖋️ ลายเซ็นผู้บันทึก:**")
                st.image(doc_data['creator_signature'], width=200)
            
            st.write("---")
            st.write("**⚙️ ประเมินผลเอกสาร 1-6:**")
            
            # ฟอร์มทำรับผลการตรวจ ผ่าน/ไม่ผ่าน
            with st.form(key='inspector_form'):
                status_options = ["ผ่าน", "ไม่ผ่าน"]
                
                # ดึงค่าเดิมมาเป็น Default ถ้าเคยตรวจแล้ว
                d1 = st.radio("เอกสาร 1", status_options, index=0 if doc_data['doc1_status'] == 'ผ่าน' else 1, horizontal=True)
                d2 = st.radio("เอกสาร 2", status_options, index=0 if doc_data['doc2_status'] == 'ผ่าน' else 1, horizontal=True)
                d3 = st.radio("เอกสาร 3", status_options, index=0 if doc_data['doc3_status'] == 'ผ่าน' else 1, horizontal=True)
                d4 = st.radio("เอกสาร 4", status_options, index=0 if doc_data['doc4_status'] == 'ผ่าน' else 1, horizontal=True)
                d5 = st.radio("เอกสาร 5", status_options, index=0 if doc_data['doc5_status'] == 'ผ่าน' else 1, horizontal=True)
                d6 = st.radio("เอกสาร 6", status_options, index=0 if doc_data['doc6_status'] == 'ผ่าน' else 1, horizontal=True)
                
                inspector_name = st.text_input("ชื่อผู้ตรวจสอบ *", value="" if doc_data['inspector'] == "ยังไม่ได้ตรวจ" else doc_data['inspector'])
                
                save_inspection = st.form_submit_button(label="💾 บันทึกผลการตรวจ")
                
            if save_inspection:
                if not inspector_name:
                    st.error("❌ กรุณาระบุชื่อผู้ตรวจสอบก่อนบันทึกผล")
                else:
                    conn = sqlite3.connect('document_flow_system.db')
                    c = conn.cursor()
                    c.execute('''
                        UPDATE documents 
                        SET doc1_status=?, doc2_status=?, doc3_status=?, doc4_status=?, doc5_status=?, doc6_status=?, inspector=?, check_status='ตรวจเสร็จแล้ว'
                        WHERE id=?
                    ''', (d1, d2, d3, d4, d5, d6, inspector_name, selected_id))
                    conn.commit()
                    conn.close()
                    st.success("🎉 บันทึกผลการตรวจสอบเรียบร้อยแล้ว!")
                    st.rerun() # รีเฟรชหน้าจอเพื่ออัปเดตตารางทันที

        # ส่วนของตารางแดชบอร์ดด้านขวา
        with col_table:
            st.subheader("📋 รายการข้อมูลสถานะทั้งหมด")
            
            # ปรับแต่งการแสดงผลตารางให้สวยงาม
            display_df = df_all[[
                'source_place', 'doc_id_text', 'fullname', 'doc_type',
                'doc1_status', 'doc2_status', 'doc3_status', 'doc4_status', 'doc5_status', 'doc6_status',
                'inspector', 'check_status', 'timestamp'
            ]].copy()
            
            display_df.columns = [
                'แหล่งที่มา', 'เลขหนังสือ', 'ชื่อ-นามสกุล', 'ประเภท',
                'เอกสาร 1', 'เอกสาร 2', 'เอกสาร 3', 'เอกสาร 4', 'เอกสาร 5', 'เอกสาร 6',
                'ผู้ตรวจ', 'สถานะรวม', 'วันเวลาที่บันทึก'
            ]
            
            st.dataframe(display_df, use_container_width=True)
            
            # ปุ่มดาวน์โหลดรายงาน
            csv = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดตารางนี้เป็นไฟล์ CSV",
                data=csv,
                file_name=f"รายงานสถานะสารบรรณ_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )
