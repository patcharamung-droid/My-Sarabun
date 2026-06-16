import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าเว็บและสไตล์สีแดงเลือดหมู
st.set_page_config(page_title="ระบบงานสารบรรณ Google Sheets", layout="wide")

st.markdown("""
    <style>
        div.stButton > button:first-child { background-color: #800000; color: white; border-radius: 8px; font-weight: bold; }
        div.stButton > button:first-child:hover { background-color: #550000; color: #ffcccc; }
        div[data-testid="stForm"] { border: 2px solid #800000 !important; border-radius: 12px !important; background-color: #fffafb; padding: 25px !important; }
        h1, h2, h3 { color: #800000 !important; }
        section[data-testid="stSidebar"] { background-color: #4a0000; color: white; }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันเชื่อมต่อ Google Sheets ดึงข้อมูลจากคีย์ลับ
def get_gsheet_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้ กรุณาตรวจสอบการตั้งค่าคู่สายใน Secrets")
        st.stop()

conn = get_gsheet_connection()

# บัญชีผู้ใช้งานทดสอบ
USERS = {
    "user1": {"password": "1234", "role": "creator", "name": "สมชาย ใจดี (เจ้าหน้าที่บันทึก)"},
    "admin1": {"password": "1234", "role": "inspector", "name": "หัวหน้าสมศักดิ์ (ผู้ตรวจสอบ)"}
}

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "user_fullname" not in st.session_state: st.session_state.user_fullname = None

# --- หน้าจอเลือกล็อกอิน ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🏛️ ระบบทะเบียนสารบรรณ (Google Sheets)</h1>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        with st.form(key='login_form'):
            st.markdown("<h3 style='text-align: center;'>🔐 เข้าสู่ระบบ</h3>", unsafe_allow_html=True)
            username_input = st.text_input("ชื่อผู้ใช้งาน", placeholder="user1 หรือ admin1")
            password_input = st.text_input("รหัสผ่าน", type="password", placeholder="••••")
            login_btn = st.form_submit_button("🔓 ล็อกอิน")
            
        if login_btn:
            if username_input in USERS and USERS[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_role = USERS[username_input]["role"]
                st.session_state.user_fullname = USERS[username_input]["name"]
                st.success("🎉 ล็อกอินสำเร็จ...")
                time_lib.sleep(1)
                st.rerun()
            else: st.error("❌ บัญชีไม่ถูกต้อง")
    st.stop()

# --- แถบควบคุมข้างทาง (Sidebar) ---
st.sidebar.markdown("<h2 style='text-align:center;'>🏛️ สารบรรณ</h2>", unsafe_allow_html=True)
st.sidebar.write(f"**ผู้ใช้งาน:** {st.session_state.user_fullname}")
if st.sidebar.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False; st.rerun()

status_options = ["ผ่าน", "ไม่ผ่าน"]

def render_doc_row(label):
    c_status, c_note = st.columns([1, 2])
    with c_status: status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
    with c_note: note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียด (ถ้ามี)", key=f"note_{label}")
    return status, note

# ฟังก์ชันดึงข้อมูลจาก Google Sheets แบบ Real-time
def load_data():
    try:
        # อ่านข้อมูลและข้ามหัวแถวแรกมาทำ DataFrame
        df = conn.read(ttl="0d")
        df = df.dropna(subset=['doc_id_text']) # กรองเฉพาะแถวที่มีข้อมูลเลขหนังสือ
        return df.sort_values(by="id", ascending=False)
    except:
        return pd.DataFrame()

# ==========================================
# 🟢 หน้าจอเฉพาะสำหรับ: 📝 ผู้บันทึกข้อมูล
# ==========================================
if st.session_state.user_role == "creator":
    st.subheader("📝 ฟอร์มลงทะเบียนเอกสารและตรวจสอบเบื้องต้น")
    if 'visible_docs' not in st.session_state: st.session_state.visible_docs = 3

    with st.form(key='creator_form_sheet'):
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.text_input("แหล่งที่มา *")
            doc_id_text = st.text_input("เลขหนังสือ *")
            creator_name = st.text_input("ผู้บันทึก", value=st.session_state.user_fullname, disabled=True)
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *")
            doc_type = st.text_input("ประเภทคำขอ *")
            created_date = st.date_input("วันที่บันทึก *", datetime.now().date())
            
        st.write("---")
        doc1_status, doc1_note = render_doc_row("📄 เอกสาร 1")
        doc2_status, doc2_note = render_doc_row("📄 เอกสาร 2")
        doc3_status, doc3_note = render_doc_row("📄 เอกสาร 3")
        
        doc4_status, doc4_note = "ไม่ได้ระบุ", ""; doc5_status, doc5_note = "ไม่ได้ระบุ", ""; doc6_status, doc6_note = "ไม่ได้ระบุ", ""
        if st.session_state.visible_docs >= 4: doc4_status, doc4_note = render_doc_row("📄 เอกสาร 4")
        if st.session_state.visible_docs >= 5: doc5_status, doc5_note = render_doc_row("📄 เอกสาร 5")
        if st.session_state.visible_docs == 6: doc6_status, doc6_note = render_doc_row("📄 เอกสาร 6")
            
        submit_button = st.form_submit_button(label='💾 บันทึกส่งเข้า Google Sheet ถาวร')

    if st.session_state.visible_docs < 6 and st.button("➕ เพิ่มช่องตรวจเอกสารลำดับถัดไป"):
        st.session_state.visible_docs += 1; st.rerun()

    if submit_button:
        if not source_place or not doc_id_text or not fullname or not doc_type:
            st.error("❌ กรุณากรอกข้อมูลด่านหลักให้ครบถ้วน")
        else:
            with st.spinner("⏳ กำลังเชื่อมต่อและส่งข้อมูลเข้า Google Sheet..."):
                time_lib.sleep(3)
            
            df_existing = load_data()
            next_id = 1 if df_existing.empty else int(df_existing['id'].max()) + 1
            
            # บันทึกข้อมูลเป็นแถวใหม่
            new_row = pd.DataFrame([{
                "id": next_id, "source_place": source_place, "doc_id_text": doc_id_text, "fullname": fullname, "doc_type": doc_type,
                "creator_name": creator_name, "created_date_text": str(created_date),
                "doc1_status": doc1_status, "doc1_note": doc1_note, "doc2_status": doc2_status, "doc2_note": doc2_note,
                "doc3_status": doc3_status, "doc3_note": doc3_note, "doc4_status": doc4_status, "doc4_note": doc4_note,
                "doc5_status": doc5_status, "doc5_note": doc5_note, "doc6_status": doc6_status, "doc6_note": doc6_note,
                "inspector_name": "ยังไม่ได้ตรวจ", "inspected_date_text": "-", "check_status": "รอตรวจเอกสาร"
            }])
            
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.session_state.visible_docs = 3
            st.success("🎉 บันทึกข้อมูลลง Google Sheet เรียบร้อยและถาวร!")
            st.rerun()

    st.write("---")
    st.markdown("<h3 style='color:#800000;'>📋 คลังประวัติรายการจาก Google Sheet สิทธิ์สำหรับดูเท่านั้น</h3>", unsafe_allow_html=True)
    df_raw = load_data()
    if not df_raw.empty:
        st.dataframe(df_raw[['id', 'doc_id_text', 'fullname', 'doc_type', 'creator_name', 'created_date_text', 'inspector_name', 'check_status']], use_container_width=True, hide_index=True)

# ==========================================
# 🔵 หน้าจอเฉพาะสำหรับ: 🔍 ผู้ตรวจสอบเอกสาร
# ==========================================
else:
    st.subheader("🔍 ศูนย์ควบคุมการพิจารณาตรวจสอบสิทธิ์")
    
    @st.dialog("🖊️ ลงชื่อพิจารณาอนุมัติเอกสารกลาง", width="large")
    def show_inspection_modal(doc_id):
        df_existing = load_data()
        data = df_existing[df_existing['id'] == doc_id].iloc[0]
        
        st.markdown(f"<h5>📦 ตรวจรับรองทะเบียนเลขที่: <span style='color:#800000;'>{data['doc_id_text']}</span></h5>", unsafe_allow_html=True)
        st.write(f"**ผู้ยื่นคำขอ:** {data['fullname']} | **ประเภทงาน:** {data['doc_type']} | **ผู้บันทึก:** {data['creator_name']}")
        st.write("---")
        
        col_detail, col_form = st.columns([1, 1])
        with col_detail:
            st.markdown("📋 **สรุปไฟล์แนบ:**")
            for i in range(1, 7):
                if f'doc{i}_status' in data and data[f'doc{i}_status'] != "ไม่ได้ระบุ":
                    st.write(f"{'✅' if data[f'doc{i}_status']=='ผ่าน' else '❌'} เอกสาร {i}: **{data[f'doc{i}_status']}** ({data[f'doc{i}_note'] or '-'})")
                    
        with col_form:
            with st.form(key=f'modal_form_{doc_id}'):
                final_status = st.selectbox("มติภาพรวม *", ["รอตรวจเอกสาร", "อนุมัติ", "ไม่อนุมัติ", "ยกเลิก"])
                inspector_input = st.text_input("ผู้ลงนามตรวจสอบ", value=st.session_state.user_fullname, disabled=True)
                inspected_date = st.date_input("วันที่ลงนามอนุมัติ *")
                submit_modal = st.form_submit_button("💾 ยืนยันผลมติภาพรวม")
                
            if submit_modal:
                # แก้ไขสถานะแถวเดิมใน Google Sheet
                df_existing.loc[df_existing['id'] == doc_id, 'inspector_name'] = inspector_input
                df_existing.loc[df_existing['id'] == doc_id, 'check_status'] = final_status
                df_existing.loc[df_existing['id'] == doc_id, 'inspected_date_text'] = str(inspected_date)
                
                conn.update(data=df_existing)
                st.success("🎉 ปรับปรุงสถานะลง Google Sheet สำเร็จ!")
                st.rerun()

    df_all = load_data()
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการค้างใน Google Sheet")
    else:
        # แดชบอร์ดสถิติ
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⏳ รอตรวจเอกสาร", len(df_all[df_all['check_status'] == 'รอตรวจเอกสาร']))
        m2.metric("🟢 อนุมัติแล้ว", len(df_all[df_all['check_status'] == 'อนุมัติ']))
        m3.metric("🔴 ไม่อนุมัติ", len(df_all[df_all['check_status'] == 'ไม่อนุมัติ']))
        m4.metric("⚪ ยกเลิก", len(df_all[df_all['check_status'] == 'ยกเลิก']))
        
        st.write("---")
        st.markdown("<div style='background-color:#800000; padding:10px; border-radius:8px 8px 0px 0px; color:white; font-weight:bold;'><div style='display:flex;'><div style='flex:0.6;'>ID</div><div style='flex:1.4;'>เลขหนังสือ</div><div style='flex:1.6;'>ชื่อผู้ยื่น</div><div style='flex:1.6;'>ประเภท</div><div style='flex:1.8;'>ผู้บันทึก</div><div style='flex:2.0;'>สถานะรวม</div><div style='flex:1.2;'>การจัดการ</div></div></div>", unsafe_allow_html=True)

        for _, row in df_all.iterrows():
            st.markdown("<div style='padding:12px 10px; border-bottom:1px solid #eee; display:flex; align-items:center; background-color:white;'>", unsafe_allow_html=True)
            c_id, c_no, c_name, c_type, c_user, c_status, c_act = st.columns([0.6, 1.4, 1.6, 1.6, 1.8, 2.0, 1.2])
            c_id.write(f"{row['id']}")
            c_no.write(f"{row['doc_id_text']}")
            c_name.write(f"{row['fullname']}")
            c_type.write(f"{row['doc_type']}")
            c_user.write(f"{row['creator_name']}")
            c_status.write(f"🏷️ {row['check_status']}")
            
            if c_act.button("🔍 ตรวจ", key=f"btn_{row['id']}"):
                show_inspection_modal(int(row['id']))
            st.markdown("</div>", unsafe_allow_html=True)
