import streamlit as st
import sqlite3
from datetime import datetime
import time as time_lib  # เปลี่ยนชื่อเพื่อไม่ให้ซ้ำกับตัวแปรอื่น
import pandas as pd

# 1. จัดการฐานข้อมูล (เอาฟิลด์เวลาออก เหลือเฉพาะวันที่)
def init_db():
    conn = sqlite3.connect('document_management_v10.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS docs_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_place TEXT,
            doc_id_text TEXT,
            fullname TEXT,
            doc_type TEXT,
            creator_name TEXT,
            created_date_text TEXT,     -- เก็บคงเหลือเฉพาะวันที่บันทึก
            doc1_status TEXT, doc1_note TEXT,
            doc2_status TEXT, doc2_note TEXT,
            doc3_status TEXT, doc3_note TEXT,
            doc4_status TEXT, doc4_note TEXT,
            doc5_status TEXT, doc5_note TEXT,
            doc6_status TEXT, doc6_note TEXT,
            inspector_name TEXT DEFAULT 'ยังไม่ได้ตรวจ',
            inspected_date_text TEXT DEFAULT '-',   -- เก็บคงเหลือเฉพาะวันที่ตรวจ
            check_status TEXT DEFAULT 'รอตรวจเอกสาร',
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
    st.header("✍️ *ฝั่งผู้บันทึกข้อมูล*")
    
    if 'visible_docs' not in st.session_state:
        st.session_state.visible_docs = 3

    with st.form(key='creator_form_v9'):
        st.subheader("1. ข้อมูลทั่วไปและวันที่บันทึก")
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่, หน่วยงานภายนอก")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
            creator_name = st.text_input("ชื่อผู้บันทึกข้อมูล *", placeholder="ระบุชื่อเจ้าหน้าที่ผู้บันทึก")
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="เช่น ขออนุมัติโครงการ, ขอย้ายตำแหน่ง")
            
            # 1. นำอินพุตเวลาออก เหลือเฉพาะ วันที่บันทึกเอกสาร
            created_date = st.date_input("วันที่บันทึกเอกสาร *", datetime.now().date())
            
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
            # 2. แสดง Pop-up หมุนหลอดกำลังบันทึกข้อมูลหน่วงเวลา 3 วินาที
            with st.spinner("⏳ กำลังบันทึกข้อมูลลงฐานข้อมูล กรุณารอสักครู่..."):
                time_lib.sleep(3) # หน่วงเวลา 3 วินาที
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_management_v10.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO docs_pool (
                    source_place, doc_id_text, fullname, doc_type, creator_name,
                    created_date_text,
                    doc1_status, doc1_note, doc2_status, doc2_note,
                    doc3_status, doc3_note, doc4_status, doc4_note,
                    doc5_status, doc5_note, doc6_status, doc6_note,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_place, doc_id_text, fullname, doc_type, creator_name,
                str(created_date),
                doc1_status, doc1_note, doc2_status, doc2_note,
                doc3_status, doc3_note, doc4_status, doc4_note,
                doc5_status, doc5_note, doc6_status, doc6_note,
                current_time
            ))
            conn.commit()
            conn.close()
            
            st.session_state.visible_docs = 3
            st.success(f"🎉 บันทึกข้อมูลและส่งต่อเรียบร้อยแล้ว!")
            st.rerun()


# ==========================================
# 🔵 ส่วนของ: 🔍 ผู้ตรวจสอบเอกสาร
# ==========================================
else:
    st.header("🔍 *ฝั่งผู้ตรวจสอบเอกสารและลงนาม*")
    
    # ฟังก์ชันหน้าต่างลอยลอยขึ้นมาตรงกลางจอเมื่อสั่งรัน
    @st.dialog("🖊️ ฟอร์มลงชื่อตรวจรับรองเอกสาร", width="large")
    def show_inspection_modal(doc_id):
        conn = sqlite3.connect('document_management_v10.db')
        c = conn.cursor()
        c.execute("SELECT * FROM docs_pool WHERE id=?", (doc_id,))
        doc_data = c.fetchone()
        conn.close()
        
        keys = ['id', 'source_place', 'doc_id_text', 'fullname', 'doc_type', 'creator_name',
                'created_date_text',
                'doc1_status', 'doc1_note', 'doc2_status', 'doc2_note', 'doc3_status', 'doc3_note',
                'doc4_status', 'doc4_note', 'doc5_status', 'doc5_note', 'doc6_status', 'doc6_note',
                'inspector_name', 'inspected_date_text', 'check_status', 'timestamp']
        data = dict(zip(keys, doc_data))
        
        st.markdown(f"**เลขหนังสือ:** {data['doc_id_text']} | **ชื่อผู้ยื่น:** {data['fullname']}")
        st.markdown(f"**ผู้บันทึก:** {data['creator_name']} | **บันทึกเมื่อวันที่:** {data['created_date_text']}")
        st.write("---")
        
        col_detail, col_form = st.columns([1, 1])
        
        with col_detail:
            st.markdown("**📋 ผลการตรวจเช็คไฟล์แนบจากผู้บันทึก:**")
            for i in range(1, 7):
                status = data[f'doc{i}_status']
                note = data[f'doc{i}_note']
                if status != "ไม่ได้ระบุ":
                    note_text = f" ({note})" if note else ""
                    icon = "✅" if status == "ผ่าน" else "❌"
                    st.write(f"{icon} เอกสาร {i}: **{status}** {note_text}")
                    
        with col_form:
            with st.form(key=f'modal_form_{doc_id}'):
                st.markdown("**✍️ บันทึกผลตรวจและวันที่ตรวจรับรอง:**")
                status_list = ["รอตรวจเอกสาร", "อนุมัติ", "ไม่อนุมัติ", "ยกเลิก"]
                try:
                    def_index = status_list.index(data['check_status'])
                except:
                    def_index = 0
                    
                final_status = st.selectbox("ผลการพิจารณาภาพรวม *", status_list, index=def_index)
                inspector_input = st.text_input("ลงชื่อผู้ตรวจเอกสาร (ชื่อ-นามสกุล) *", value="" if data['inspector_name'] == "ยังไม่ได้ตรวจ" else data['inspector_name'])
                
                # 1. นำอินพุตเวลาออก เหลือเฉพาะ วันที่ตรวจรับรอง
                inspected_date = st.date_input("วันที่พิจารณา/ตรวจรับรอง *", datetime.now().date())
                
                submit_modal = st.form_submit_button("💾 บันทึกผลตรวจ")
                
            if submit_modal:
                if not inspector_input:
                    st.error("❌ กรุณากรอกชื่อผู้ตรวจเอกสารด้วยครับ")
                else:
                    conn = sqlite3.connect('document_management_v10.db')
                    c = conn.cursor()
                    c.execute('''
                        UPDATE docs_pool 
                        SET inspector_name=?, check_status=?, inspected_date_text=?
                        WHERE id=?
                    ''', (inspector_input, final_status, str(inspected_date), doc_id))
                    conn.commit()
                    conn.close()
                    
                    st.success("อัปเดตสถานะสำเร็จ!")
                    st.rerun()

    # --- โครงสร้างหน้าหลักฝั่งผู้ตรวจ ---
    conn = sqlite3.connect('document_management_v10.db')
    df_all = pd.read_sql_query("SELECT * FROM docs_pool ORDER BY id DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบ")
    else:
        # Dashboard สรุปด้านบน
        st.subheader("📊 Dashboard สถานะการตรวจสอบภาพรวม")
        count_waiting = len(df_all[df_all['check_status'] == 'รอตรวจเอกสาร'])
        count_approved = len(df_all[df_all['check_status'] == 'อนุมัติ'])
        count_rejected = len(df_all[df_all['check_status'] == 'ไม่อนุมัติ'])
        count_canceled = len(df_all[df_all['check_status'] == 'ยกเลิก'])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="⏳ รอตรวจเอกสาร", value=f"{count_waiting} รายการ")
        m2.metric(label="🟢 อนุมัติแล้ว", value=f"{count_approved} รายการ")
        m3.metric(label="🔴 ไม่อนุมัติ", value=f"{count_rejected} รายการ")
        m4.metric(label="⚪ ยกเลิก", value=f"{count_canceled} รายการ")
        
        st.write("---")
        st.subheader("📋 รายการข้อมูลเอกสารทั้งหมดในระบบ")
        
        search_query = st.text_input("🔍 ค้นหาในตาราง (พิมพ์ แหล่งที่มา / เลขหนังสือ / ชื่อผู้ยื่น)")
        if search_query:
            df_filtered = df_all[
                df_all['source_place'].str.contains(search_query, case=False, na=False) |
                df_all['doc_id_text'].str.contains(search_query, case=False, na=False) |
                df_all['fullname'].str.contains(search_query, case=False, na=False)
            ]
        else:
            df_filtered = df_all

        # หัวข้อตารางเหลือเฉพาะคอลัมน์ วันที่
        h1, h2, h3, h4, h5, h6, h7 = st.columns([0.8, 1.8, 1.8, 1.8, 1.8, 2.5, 1.5])
        h1.markdown("**ID**")
        h2.markdown("**เลขหนังสือ**")
        h3.markdown("**ชื่อ-สกุลผู้ยื่น**")
        h4.markdown("**ผู้บันทึก (วันที่)**")
        h5.markdown("**ผู้ตรวจรับรอง (วันที่)**")
        h6.markdown("**สถานะปัจจุบัน**")
        h7.markdown("**การจัดการ**")
        st.markdown("<hr style='margin: 5px 0px 10px 0px; border-color: #ddd;' />", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            r1, r2, r3, r4, r5, r6, r7 = st.columns([0.8, 1.8, 1.8, 1.8, 1.8, 2.5, 1.5])
            r1.write(f"{row['id']}")
            r2.write(f"{row['doc_id_text']}")
            r3.write(f"{row['fullname']}")
            
            # ตารางโชว์เฉพาะ วันที่ ของผู้บันทึก
            r4.write(f"{row['creator_name']} ({row['created_date_text']})")
            
            # ตารางโชว์เฉพาะ วันที่ ของผู้ตรวจ
            if row['inspector_name'] == 'ยังไม่ได้ตรวจ':
                r5.write("-")
            else:
                r5.write(f"{row['inspector_name']} ({row['inspected_date_text']})")
            
            if row['check_status'] == 'รอตรวจเอกสาร':
                r6.markdown("⏳ <span style='color:orange;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'อนุมัติ':
                r6.markdown("🟢 <span style='color:green; font-weight:bold;'>อนุมัติ</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'ไม่อนุมัติ':
                r6.markdown("🔴 <span style='color:red; font-weight:bold;'>ไม่อนุมัติ</span>", unsafe_allow_html=True)
            else:
                r6.markdown("⚪ <span style='color:gray;'>ยกเลิก</span>", unsafe_allow_html=True)
            
            if r7.button("🔍 ตรวจเอกสาร", key=f"btn_{row['id']}"):
                show_inspection_modal(row['id'])
