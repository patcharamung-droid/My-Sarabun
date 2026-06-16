import streamlit as st
import sqlite3
from datetime import datetime
import time as time_lib
import pandas as pd

# 1. จัดการฐานข้อมูล
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
            created_date_text TEXT,
            doc1_status TEXT, doc1_note TEXT,
            doc2_status TEXT, doc2_note TEXT,
            doc3_status TEXT, doc3_note TEXT,
            doc4_status TEXT, doc4_note TEXT,
            doc5_status TEXT, doc5_note TEXT,
            doc6_status TEXT, doc6_note TEXT,
            inspector_name TEXT DEFAULT 'ยังไม่ได้ตรวจ',
            inspected_date_text TEXT DEFAULT '-',
            check_status TEXT DEFAULT 'รอตรวจเอกสาร',
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ระบบจำลองฐานข้อมูลบัญชีผู้ใช้งาน (User Credentials) ---
# บัญชีสำหรับทดสอบระบบ
USERS = {
    "user1": {"password": "1234", "role": "creator", "name": "สมชาย ใจดี (เจ้าหน้าที่บันทึก)"},
    "admin1": {"password": "1234", "role": "inspector", "name": "หัวหน้าสมศักดิ์ (ผู้ตรวจสอบ)"}
}

# ใช้ session_state ของ Streamlit ในการจำสถานะว่าล็อกอินหรือยัง
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_fullname" not in st.session_state:
    st.session_state.user_fullname = None

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบงานสารบรรณ", layout="wide")


# ==========================================
# 🔒 ส่วนของ: หน้ากากและฟอร์มล็อกอิน
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 เข้าสู่ระบบสารบรรณและตรวจเช็คเอกสาร</h2>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        with st.form(key='login_form'):
            username_input = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="เช่น user1 หรือ admin1")
            password_input = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="••••")
            login_btn = st.form_submit_button("🔓 เข้าสู่ระบบ")
            
        if login_btn:
            if username_input in USERS and USERS[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_role = USERS[username_input]["role"]
                st.session_state.user_fullname = USERS[username_input]["name"]
                st.success("🎉 เข้าสู่ระบบสำเร็จ กำลังนำคุณไปยังหน้างาน...")
                time_lib.sleep(1)
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
                
        st.info("💡 บัญชีสำหรับทดสอบ:\n- ผู้บันทึก: user1 / 1234\n- ผู้ตรวจ: admin1 / 1234")
    st.stop() # หยุดการทำงานของโค้ดด้านล่างไว้ตรงนี้จนกว่าจะล็อกอินผ่าน


# ==========================================
# 🚪 เมื่อล็อกอินผ่านแล้ว แสดงแถบควบคุมด้านข้าง (Sidebar)
# ==========================================
st.sidebar.title("👤 ข้อมูลผู้ใช้งาน")
st.sidebar.write(f"**ชื่อ:** {st.session_state.user_fullname}")
st.sidebar.write(f"**สิทธิ์:** {'📝 ผู้บันทึกข้อมูล' if st.session_state.user_role == 'creator' else '🔍 ผู้ตรวจสอบเอกสาร'}")

# ปุ่มออกจากระบบ
if st.sidebar.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_fullname = None
    st.rerun()

st.title("📑 ระบบบันทึกและตรวจสอบเอกสารสารบรรณ")
status_options = ["ผ่าน", "ไม่ผ่าน"]

def render_doc_row(label):
    c_status, c_note = st.columns([1, 2])
    with c_status:
        status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
    with c_note:
        note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียดของ {label} (ถ้ามี)", key=f"note_{label}")
    return status, note


# ==========================================
# 🟢 หน้าจอเฉพาะสำหรับ: 📝 ผู้บันทึกข้อมูล (role == 'creator')
# ==========================================
if st.session_state.user_role == "creator":
    st.header("✍️ เมนูสำหรับเจ้าหน้าที่บันทึกข้อมูล")
    
    if 'visible_docs' not in st.session_state:
        st.session_state.visible_docs = 3

    with st.form(key='creator_form_v12'):
        st.subheader("1. ข้อมูลทั่วไปและวันที่บันทึก")
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่, หน่วยงานภายนอก")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
            # ดึงชื่อคนที่ล็อกอินมาใส่ในช่องชื่อผู้บันทึกให้โดยอัตโนมัติ ล็อกไม่ให้แก้เพื่อความโปร่งใส
            creator_name = st.text_input("ชื่อผู้บันทึกข้อมูล", value=st.session_state.user_fullname, disabled=True)
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="เช่น ขออนุมัติโครงการ, ขอย้ายตำแหน่ง")
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
        if not source_place or not doc_id_text or not fullname or not doc_type:
            st.error("❌ กรุณากรอกข้อมูลทั่วไปในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
        else:
            with st.spinner("⏳ กำลังบันทึกข้อมูลลงฐานข้อมูล กรุณารอสักครู่..."):
                time_lib.sleep(3)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('document_management_v10.db')
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO docs_pool (
                    source_place, doc_id_text, fullname, doc_type, creator_name, created_date_text,
                    doc1_status, doc1_note, doc2_status, doc2_note, doc3_status, doc3_note,
                    doc4_status, doc4_note, doc5_status, doc5_note, doc6_status, doc6_note,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_place, doc_id_text, fullname, doc_type, creator_name, str(created_date),
                doc1_status, doc1_note, doc2_status, doc2_note, doc3_status, doc3_note,
                doc4_status, doc4_note, doc5_status, doc5_note, doc6_status, doc6_note,
                current_time
            ))
            conn.commit()
            conn.close()
            
            st.session_state.visible_docs = 3
            st.success(f"🎉 บันทึกข้อมูลเรียบร้อยแล้ว!")
            st.rerun()


# ==========================================
# 🔵 หน้าจอเฉพาะสำหรับ: 🔍 ผู้ตรวจสอบเอกสาร (role == 'inspector')
# ==========================================
else:
    st.header("🔍 เมนูสำหรับผู้ตรวจสอบและลงนามอนุมัติ")
    
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
        
        st.markdown(f"**เลขหนังสือ:** {data['doc_id_text']} | **ชื่อผู้ยื่นคำขอ:** {data['fullname']} | **ประเภทคำขอ:** {data['doc_type']}")
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
                # ดึงชื่อผู้ตรวจที่ล็อกอินมาใส่ให้โดยอัตโนมัติ ล็อกช่องไว้เพื่อป้องกันการลงชื่อสวมรอย
                inspector_input = st.text_input("ลงชื่อผู้ตรวจเอกสาร", value=st.session_state.user_fullname, disabled=True)
                inspected_date = st.date_input("วันที่พิจารณา/ตรวจรับรอง *", datetime.now().date())
                
                submit_modal = st.form_submit_button("💾 บันทึกผลตรวจ")
                
            if submit_modal:
                conn = sqlite3.connect('document_management_v10.db')
                c = conn.cursor()
                c.execute('''
                    UPDATE docs_pool 
                    SET inspector_name=?, check_status=?, inspected_date_text=?
                    WHERE id=?
                ''', (inspector_input, final_status, str(inspected_date), doc_id))
                conn.commit()
                conn.close()
                st.success("อัปเดตสถานะและลงชื่อผู้ตรวจสำเร็จ!")
                st.rerun()

    # ดึงข้อมูลมาแสดงในหน้าแรกของผู้ตรวจ
    conn = sqlite3.connect('document_management_v10.db')
    df_all = pd.read_sql_query("SELECT * FROM docs_pool ORDER BY id DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบ")
    else:
        # Dashboard สรุปสถานะภาพรวม
        st.subheader("📊 Dashboard Status การตรวจสอบภาพรวม")
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

        # แสดงตารางรายการหลัก
        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([0.6, 1.4, 1.6, 1.6, 1.8, 1.8, 2.0, 1.2])
        h1.markdown("**ID**")
        h2.markdown("**เลขหนังสือ**")
        h3.markdown("**ชื่อ-สกุลผู้ยื่น**")
        h4.markdown("**ประเภทคำขอ**")
        h5.markdown("**ผู้บันทึก (วันที่)**")
        h6.markdown("**ผู้ตรวจรับรอง (วันที่)**")
        h7.markdown("**สถานะปัจจุบัน**")
        h8.markdown("**การจัดการ**")
        st.markdown("<hr style='margin: 5px 0px 10px 0px; border-color: #ddd;' />", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            r1, r2, r3, r4, r5, r6, r7, r8 = st.columns([0.6, 1.4, 1.6, 1.6, 1.8, 1.8, 2.0, 1.2])
            r1.write(f"{row['id']}")
            r2.write(f"{row['doc_id_text']}")
            r3.write(f"{row['fullname']}")
            r4.write(f"{row['doc_type']}")
            r5.write(f"{row['creator_name']} ({row['created_date_text']})")
            
            if row['inspector_name'] == 'ยังไม่ได้ตรวจ':
                r6.write("-")
            else:
                r6.write(f"{row['inspector_name']} ({row['inspected_date_text']})")
            
            if row['check_status'] == 'รอตรวจเอกสาร':
                r7.markdown("⏳ <span style='color:orange;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'อนุมัติ':
                r7.markdown("🟢 <span style='color:green; font-weight:bold;'>อนุมัติ</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'ไม่อนุมัติ':
                r7.markdown("🔴 <span style='color:red; font-weight:bold;'>ไม่อนุมัติ</span>", unsafe_allow_html=True)
            else:
                r7.markdown("⚪ <span style='color:gray;'>ยกเลิก</span>", unsafe_allow_html=True)
            
            if r8.button("🔍 ตรวจเอกสาร", key=f"btn_{row['id']}"):
                show_inspection_modal(row['id'])
