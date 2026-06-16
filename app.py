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

# บัญชีผู้ใช้งานทดสอบ
USERS = {
    "user1": {"password": "1234", "role": "creator", "name": "สมชาย ใจดี (เจ้าหน้าที่บันทึก)"},
    "admin1": {"password": "1234", "role": "inspector", "name": "หัวหน้าสมศักดิ์ (ผู้ตรวจสอบ)"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_fullname" not in st.session_state:
    st.session_state.user_fullname = None

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบงานสารบรรณ", layout="wide")

# ==========================================
# 🎨 ปรับแต่งธีมความสวยงามด้วย CSS (โทนสีแดงเลือดหมู #800000)
# ==========================================
st.markdown("""
    <style>
        /* เปลี่ยนสีปุ่มหลัก (Primary Buttons) ให้เป็นสีแดงเลือดหมู */
        div.stButton > button:first-child {
            background-color: #800000;
            color: white;
            border-radius: 8px;
            border: 1px solid #660000;
            font-weight: bold;
            transition: 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #550000;
            color: #ffcccc;
            border-color: #550000;
        }
        /* ปรับแต่งกรอบ Form ด้านบน */
        div[data-testid="stForm"] {
            border: 2px solid #800000 !important;
            border-radius: 12px !important;
            background-color: #fffafb;
            padding: 25px !important;
        }
        /* หัวข้อสีแดงเลือดหมูขลิบทองเล็กๆ */
        h1, h2, h3 {
            color: #800000 !important;
            font-family: 'Sarabun', sans-serif;
        }
        /* ปรับแต่ง Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #4a0000;
            color: white;
        }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 🔒 ส่วนของ: หน้ากากและฟอร์มล็อกอิน
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🏛️ ระบบบันทึกและตรวจสอบเอกสารสารบรรณ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>หน่วยงานสารบรรณอิเล็กทรอนิกส์ส่วนกลาง</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        with st.form(key='login_form'):
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🔐 เข้าสู่ระบบ</h3>", unsafe_allow_html=True)
            username_input = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="user1 หรือ admin1")
            password_input = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="••••")
            login_btn = st.form_submit_button("🔓 ล็อกอินเข้าสู่ระบบ")
            
        if login_btn:
            if username_input in USERS and USERS[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_role = USERS[username_input]["role"]
                st.session_state.user_fullname = USERS[username_input]["name"]
                st.success("🎉 ล็อกอินสำเร็จ กำลังนำคุณเข้าสู่ระบบทำงาน...")
                time_lib.sleep(1)
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
        
        st.markdown("""
            <div style='background-color: #f8ecc2; padding: 15px; border-radius: 8px; border-left: 5px solid #800000; margin-top: 20px;'>
                <span style='color: #800000; font-weight: bold;'>💡 บัญชีสำหรับทดลองงาน:</span><br/>
                <span style='color: #333;'>• ฝั่งผู้บันทึก: user1 / รหัสผ่าน: 1234<br/>• ฝั่งผู้ตรวจ: admin1 / รหัสผ่าน: 1234</span>
            </div>
        """, unsafe_allow_html=True)
    st.stop()


# ==========================================
# 🚪 แถบควบคุมด้านข้าง (Sidebar) หลังล็อกอิน
# ==========================================
st.sidebar.markdown("<h2 style='text-align:center;'>🏛️ สารบรรณ</h2>", unsafe_allow_html=True)
st.sidebar.write(f"**ผู้ใช้งาน:** {st.session_state.user_fullname}")
st.sidebar.write(f"**สิทธิ์ระบบ:** {'📝 เจ้าหน้าที่บันทึก' if st.session_state.user_role == 'creator' else '🔍 ผู้ตรวจอนุมัติ'}")
st.sidebar.write("---")

if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_fullname = None
    st.rerun()

status_options = ["ผ่าน", "ไม่ผ่าน"]

def render_doc_row(label):
    c_status, c_note = st.columns([1, 2])
    with c_status:
        status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
    with c_note:
        note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียดของ {label} (ถ้ามี)", key=f"note_{label}")
    return status, note

def get_documents_dataframe():
    conn = sqlite3.connect('document_management_v10.db')
    df = pd.read_sql_query("SELECT * FROM docs_pool ORDER BY id DESC", conn)
    conn.close()
    return df

# ฟังก์ชันตกแต่งสีให้ตารางผ่านสิทธิ์ของ st.dataframe สวยงามขึ้น
def style_status_df(df_input):
    if df_input.empty:
        return df_input
    
    # กรองเอาเฉพาะคอลัมน์ที่จะโชว์ให้กระชับ
    res_df = df_input[[
        'id', 'doc_id_text', 'fullname', 'doc_type', 'creator_name', 
        'created_date_text', 'inspector_name', 'inspected_date_text', 'check_status'
    ]].copy()
    
    res_df.columns = [
        'ID', 'เลขหนังสือ', 'ชื่อ-สกุลผู้ยื่น', 'ประเภทคำขอ', 
        'ผู้บันทึก', 'วันที่บันทึก', 'ผู้ตรวจรับรอง', 'วันที่ตรวจ', 'สถานะปัจจุบัน'
    ]
    return res_df


# ==========================================
# 🟢 หน้าจอเฉพาะสำหรับ: 📝 ผู้บันทึกข้อมูล (role == 'creator')
# ==========================================
if st.session_state.user_role == "creator":
    st.subheader("📝 ระบบบันทึกข้อมูลและตรวจสอบเอกสารสารบรรณเบื้องต้น")
    
    if 'visible_docs' not in st.session_state:
        st.session_state.visible_docs = 3

    with st.form(key='creator_form_v14'):
        st.markdown("<h4 style='color:#800000;'>1. ข้อมูลทั่วไปของเอกสาร</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *", placeholder="เช่น กองการเจ้าหน้าที่")
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
            creator_name = st.text_input("ชื่อผู้บันทึกข้อมูล", value=st.session_state.user_fullname, disabled=True)
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="เช่น ขออนุมัติโครงการ")
            created_date = st.date_input("วันที่บันทึกเอกสาร *", datetime.now().date())
            
        st.write("---")
        st.markdown("<h4 style='color:#800000;'>2. รายการตรวจสอบเอกสารแนบ</h4>", unsafe_allow_html=True)
        
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
        submit_button = st.form_submit_button(label='💾 บันทึกและจัดส่งข้อมูลเข้าคลังเอกสาร')

    if st.session_state.visible_docs < 6:
        if st.button("➕ เพิ่มช่องตรวจเอกสารลำดับถัดไป"):
            st.session_state.visible_docs += 1
            st.rerun()

    if submit_button:
        if not source_place or not doc_id_text or not fullname or not doc_type:
            st.error("❌ กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
        else:
            with st.spinner("⏳ ระบบกำลังจัดเก็บข้อมูลลงฐานข้อมูลส่วนกลางภาพรวม..."):
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
            st.success(f"🎉 บันทึกแฟ้มข้อมูลสำเร็จเรียบร้อย!")
            st.rerun()

    # ตารางแบบสวยงามฝั่งผู้บันทึก
    st.write("---")
    st.markdown("<h3 style='color:#800000;'>📋 คลังประวัติรายการเอกสารทั้งหมดในระบบ</h3>", unsafe_allow_html=True)
    df_raw = get_documents_dataframe()
    if not df_raw.empty:
        df_clean = style_status_df(df_raw)
        
        # ค้นหาในตาราง
        sq = st.text_input("🔍 ค้นหาเอกสารด่วน (เลขหนังสือ / ชื่อผู้ยื่น)")
        if sq:
            df_clean = df_clean[df_clean['เลขหนังสือ'].str.contains(sq, case=False, na=False) | 
                                df_clean['ชื่อ-สกุลผู้ยื่น'].str.contains(sq, case=False, na=False)]
                                
        # ใช้อินเตอร์เฟสยืดหยุ่นของ st.dataframe เพื่อแสดงแถบสีสถานะสวยงาม
        st.dataframe(df_clean, use_container_width=True, hide_index=True)
    else:
        st.info("💡 ยังไม่มีแฟ้มข้อมูลสะสมในคลังระบบ")


# ==========================================
# 🔵 หน้าจอเฉพาะสำหรับ: 🔍 ผู้ตรวจสอบเอกสาร (role == 'inspector')
# ==========================================
else:
    st.subheader("🔍 ศูนย์ควบคุมผู้ตรวจสอบและลงนามรับรอง")
    
    @st.dialog("🖊️ ฟอร์มลงชื่อตรวจรับรองเอกสารส่วนกลาง", width="large")
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
        
        st.markdown(f"<h5>📦 ตรวจรับรองรายงานทะเบียนที่: <span style='color:#800000;'>{data['doc_id_text']}</span></h5>", unsafe_allow_html=True)
        st.write(f"**ผู้ยื่นคำขอ:** {data['fullname']} | **ประเภทงาน:** {data['doc_type']} | **ผู้จัดบันทึกข้อมูล:** {data['creator_name']} ({data['created_date_text']})")
        st.write("---")
        
        col_detail, col_form = st.columns([1, 1])
        with col_detail:
            st.markdown("<h5 style='color:#800000;'>📋 ประวัติการตรวจสอบเช็คไฟล์แนบ:</h5>", unsafe_allow_html=True)
            for i in range(1, 7):
                status = data[f'doc{i}_status']
                note = data[f'doc{i}_note']
                if status != "ไม่ได้ระบุ":
                    note_text = f" -> [หมายเหตุ: {note}]" if note else ""
                    icon = "✅" if status == "ผ่าน" else "❌"
                    st.write(f"{icon} เอกสาร {i}: **{status}** {note_text}")
                    
        with col_form:
            with st.form(key=f'modal_form_{doc_id}'):
                st.markdown("<h5 style='color:#800000;'>🖋️ พิจารณาสถานะภาพรวมหน่วยงาน</h5>", unsafe_allow_html=True)
                status_list = ["รอตรวจเอกสาร", "อนุมัติ", "ไม่อนุมัติ", "ยกเลิก"]
                try:
                    def_index = status_list.index(data['check_status'])
                except:
                    def_index = 0
                    
                final_status = st.selectbox("ลงมติสถานะหนังสือภาพรวม *", status_list, index=def_index)
                inspector_input = st.text_input("ลายมือชื่อผู้ลงนามตรวจสอบ", value=st.session_state.user_fullname, disabled=True)
                inspected_date = st.date_input("วันที่ลงนามรับรองเอกสาร *", datetime.now().date())
                
                submit_modal = st.form_submit_button("💾 ยืนยันผลตรวจประเมิน")
                
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
                st.success("🎉 บันทึกสถิติมติที่ประชุมและอัปเดตระบบสำเร็จ!")
                st.rerun()

    df_all = get_documents_dataframe()
    
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบคลัง")
    else:
        # --- แดชบอร์ดคุมโทนพรีเมียม สไตล์สีแดงเลือดหมูสลับมิติ ---
        st.markdown("<h4 style='color:#800000; margin-bottom:15px;'>📊 แดชบอร์ดสรุปสถิติทะเบียนสิทธิ์รวม</h4>", unsafe_allow_html=True)
        count_waiting = len(df_all[df_all['check_status'] == 'รอตรวจเอกสาร'])
        count_approved = len(df_all[df_all['check_status'] == 'อนุมัติ'])
        count_rejected = len(df_all[df_all['check_status'] == 'ไม่อนุมัติ'])
        count_canceled = len(df_all[df_all['check_status'] == 'ยกเลิก'])
        
        # แสดงกล่องสรุปสไตล์โมเดิร์น
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div style='background-color:#fff5f5; padding:15px; border-radius:8px; border-left:5px solid orange; text-align:center;'><span style='color:#555;font-weight:bold;'>⏳ รอตรวจเอกสาร</span><br/><h2 style='color:orange;margin:5px;'>{count_waiting}</h2></div>", unsafe_allow_html=True)
        m2.markdown(f"<div style='background-color:#f5fff5; padding:15px; border-radius:8px; border-left:5px solid green; text-align:center;'><span style='color:#555;font-weight:bold;'>🟢 อนุมัติแล้ว</span><br/><h2 style='color:green;margin:5px;'>{count_approved}</h2></div>", unsafe_allow_html=True)
        m3.markdown(f"<div style='background-color:#fff0f0; padding:15px; border-radius:8px; border-left:5px solid #800000; text-align:center;'><span style='color:#555;font-weight:bold;'>🔴 ไม่อนุมัติ</span><br/><h2 style='color:#800000;margin:5px;'>{count_rejected}</h2></div>", unsafe_allow_html=True)
        m4.markdown(f"<div style='background-color:#f5f5f5; padding:15px; border-radius:8px; border-left:5px solid gray; text-align:center;'><span style='color:#555;font-weight:bold;'>⚪ ยกเลิก</span><br/><h2 style='color:gray;margin:5px;'>{count_canceled}</h2></div>", unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("<h3 style='color:#800000;'>📋 รายการข้อมูลเอกสารทุกลำดับชั้นในระบบ</h3>", unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 ค้นหาด่วนในระบบคลัง (แหล่งที่มา / เลขหนังสือ / ชื่อผู้ยื่น)")
        if search_query:
            df_filtered = df_all[
                df_all['source_place'].str.contains(search_query, case=False, na=False) |
                df_all['doc_id_text'].str.contains(search_query, case=False, na=False) |
                df_all['fullname'].str.contains(search_query, case=False, na=False)
            ]
        else:
            df_filtered = df_all

        # หัวข้อตารางหลักแนวคิดประหยัดเนื้อที่ คุมโทนสีทอง/แดงเลือดหมู
        st.markdown("<div style='background-color:#800000; padding:10px; border-radius:8px 8px 0px 0px; color:white; font-weight:bold;'><div style='display:flex; text-align:left;'><div style='flex:0.6;'>ID</div><div style='flex:1.4;'>เลขหนังสือ</div><div style='flex:1.6;'>ชื่อ-สกุลผู้ยื่น</div><div style='flex:1.6;'>ประเภทคำขอ</div><div style='flex:1.8;'>ผู้บันทึก (วันที่)</div><div style='flex:1.8;'>ผู้ตรวจ (วันที่)</div><div style='flex:2.0;'>สถานะรวม</div><div style='flex:1.2;'>การจัดการ</div></div></div>", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            st.markdown("<div style='padding:12px 10px; border-bottom:1px solid #eee; display:flex; align-items:center; background-color:white;'>", unsafe_allow_html=True)
            
            c_id, c_no, c_name, c_type, c_user, c_admin, c_status, c_act = st.columns([0.6, 1.4, 1.6, 1.6, 1.8, 1.8, 2.0, 1.2])
            
            c_id.write(f"{row['id']}")
            c_no.write(f"{row['doc_id_text']}")
            c_name.write(f"{row['fullname']}")
            c_type.write(f"{row['doc_type']}")
            c_user.write(f"{row['creator_name']} ({row['created_date_text']})")
            c_admin.write("-" if row['inspector_name'] == 'ยังไม่ได้ตรวจ' else f"{row['inspector_name']} ({row['inspected_date_text']})")
            
            # แต่งสี Badge ตัวอักษรสถานะปัจจุบัน
            if row['check_status'] == 'รอตรวจเอกสาร':
                c_status.markdown("⏳ <span style='color:orange; font-weight:bold;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'อนุมัติ':
                c_status.markdown("🟢 <span style='color:green; font-weight:bold;'>อนุมัติ</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'ไม่อนุมัติ':
                c_status.markdown("🔴 <span style='color:#800000; font-weight:bold;'>ไม่อนุมัติ</span>", unsafe_allow_html=True)
            else:
                c_status.markdown("⚪ <span style='color:gray;'>ยกเลิก</span>", unsafe_allow_html=True)
            
            # ปุ่มกดยิง Modal ลอยขึ้นมาตรงกลางจอตามบรีฟเดนเดิม
            if c_act.button("🔍 ตรวจ", key=f"btn_{row['id']}"):
                show_inspection_modal(row['id'])
                
            st.markdown("</div>", unsafe_allow_html=True)
