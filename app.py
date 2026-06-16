import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าเว็บและสไตล์สีแดงเลือดหมูพรีเมียม
st.set_page_config(page_title="ระบบงานสารบรรณ Google Sheets", layout="wide")

# ปรับแต่ง CSS ซ่อนเครื่องมือระบบ และจัดการตำแหน่งลายน้ำ
st.markdown("""
    <style>
        /* 1. ซ่อนเครื่องมือ Streamlit Toolbar ทั้งหมด */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stToolbar"] {display: none !important;}
        button[title="View source code"] {display: none !important;}
        
        /* ปรับแต่งปุ่มหลัก (Primary Buttons) ให้เป็นสีแดงเลือดหมู */
        div.stButton > button:first-child { 
            background-color: #800000; 
            color: white; 
            border-radius: 8px; 
            font-weight: bold; 
        }
        div.stButton > button:first-child:hover { 
            background-color: #550000; 
            color: #ffcccc; 
        }
        
        /* ปรับแต่งกรอบ Form ด้านบน */
        div[data-testid="stForm"] { 
            border: 2px solid #800000 !important; 
            border-radius: 12px !important; 
            background-color: #fffafb; 
            padding: 25px !important; 
        }
        
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

        /* 2. บังคับให้บล็อกลายน้ำใน Sidebar อยู่ติดขอบล่างสุดเสมอ */
        .sidebar-watermark {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 260px; 
            text-align: center;
            color: rgba(255, 255, 255, 0.4) !important; 
            font-size: 13px;
            font-family: 'Sarabun', sans-serif;
            letter-spacing: 0.5px;
            pointer-events: none;
            z-index: 999;
        }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันเชื่อมต่อ Google Sheets ดึงข้อมูลจากคีย์ลับใน Secrets
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
st.sidebar.write("---")
st.sidebar.write(f"**ผู้ใช้งาน:** {st.session_state.user_fullname}")
st.sidebar.write(f"**สิทธิ์ระบบ:** {'📝 เจ้าหน้าที่บันทึก' if st.session_state.user_role == 'creator' else '🔍 ผู้ตรวจอนุมัติ'}")
st.sidebar.write("---")

if st.sidebar.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False; st.rerun()

# ฝังกล่องลายน้ำไว้ใน Sidebar
st.sidebar.markdown('<div class="sidebar-watermark">Developed by Patchara.mu</div>', unsafe_allow_html=True)

status_options = ["ผ่าน", "ไม่ผ่าน"]

def render_doc_row(label):
    c_status, c_note = st.columns([1, 2])
    with c_status: status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
    with c_note: note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียด (ถ้ามี)", key=f"note_{label}")
    return status, note

def load_data():
    try:
        df = conn.read(ttl="0d")
        if df.empty: return pd.DataFrame()
        df = df.dropna(subset=['doc_id_text'])
        required_cols = ['inspector_name', 'inspected_date_text', 'check_status']
        for col in required_cols:
            if col not in df.columns: df[col] = "-"
        return df.sort_values(by="id", ascending=False)
    except: return pd.DataFrame()


# ==========================================
# 🟢 หน้าจอเฉพาะสำหรับ: 📝 ผู้บันทึกข้อมูล (role == 'creator')
# ==========================================
if st.session_state.user_role == "creator":
    st.subheader("📝 ฟอร์มลงทะเบียนเอกสารและตรวจสอบเบื้องต้น")
    if 'visible_docs' not in st.session_state: st.session_state.visible_docs = 3

    with st.form(key='creator_form_sheet'):
        col1, col2 = st.columns(2)
        with col1:
            # ✨ ปรับเป็น Dropdown สำเร็จรูปตามที่ขอเรียบร้อยครับ
            source_place = st.selectbox(
                "แหล่งที่มา *", 
                ["ASMS", "NBTC Service Portal", "ONE STOP SERVICE"]
            )
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="เช่น สร.0001/2569")
            creator_name = st.text_input("ผู้บันทึก", value=st.session_state.user_fullname, disabled=True)
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="เช่น ขออนุมัติโครงการ")
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
        if not doc_id_text or not fullname or not doc_type:
            st.error("❌ กรุณากรอกข้อมูลด่านหลักให้ครบถ้วน")
        else:
            with st.spinner("⏳ กำลังเชื่อมต่อและส่งข้อมูลเข้า Google Sheet..."):
                time_lib.sleep(3)
            
            df_existing = conn.read(ttl="0d").dropna(subset=['doc_id_text'])
            next_id = 1 if df_existing.empty else int(df_existing['id'].max()) + 1
            
            new_row = pd.DataFrame([{
                "id": next_id, "source_place": source_place, "doc_id_text": doc_id_text, "fullname": fullname, "doc_type": doc_type,
                "creator_name": creator_name, "created_date_text": str(created_date),
                "doc1_status": doc1_status, "doc1_note": doc1_note, "doc2_status": doc2_status, "doc2_note": doc2_note,
                "doc3_status": doc3_status, "doc3_note": doc3_note, "doc4_status": doc4_status, "doc4_note": doc4_note,
                "doc5_status": doc5_note, "doc5_note": doc5_note, "doc6_status": doc6_status, "doc6_note": doc6_note,
                "inspector_name": "ยังไม่ได้ตรวจ", "inspected_date_text": "-", "check_status": "รอตรวจเอกสาร"
            }])
            
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.session_state.visible_docs = 3
            st.success("🎉 บันทึกข้อมูลลง Google Sheet เรียบร้อยและถาวร!")
            st.rerun()

    st.write("---")
    st.markdown("<h3 style='color:#800000;'>📋 คลังประวัติรายการเอกสารใน Google Sheet (สำหรับดูข้อมูล)</h3>", unsafe_allow_html=True)
    df_raw = load_data()
    if not df_raw.empty:
        sq = st.text_input("🔍 พิมพ์ค้นหาข้อมูลด่วนในตาราง (เลขหนังสือ / ชื่อผู้ยื่น)")
        if sq:
            df_filtered = df_raw[df_raw['doc_id_text'].str.contains(sq, case=False, na=False) | df_raw['fullname'].str.contains(sq, case=False, na=False)]
        else:
            df_filtered = df_raw

        st.markdown("<div style='background-color:#800000; padding:10px; border-radius:8px 8px 0px 0px; color:white; font-weight:bold;'><div style='display:flex;'><div style='flex:0.5;'>ID</div><div style='flex:1.2;'>เลขหนังสือ</div><div style='flex:1.4;'>ชื่อผู้ยื่น</div><div style='flex:1.4;'>ประเภทงาน</div><div style='flex:1.4;'>ผู้บันทึก</div><div style='flex:1.1;'>วันที่บันทึก</div><div style='flex:1.4;'>ผู้ตรวจรับรอง</div><div style='flex:1.1;'>วันที่ตรวจ</div><div style='flex:1.5;'>Ref สถานะ</div></div></div>", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            st.markdown("<div style='padding:12px 10px; border-bottom:1px solid #eee; display:flex; align-items:center; background-color:white;'>", unsafe_allow_html=True)
            c_id, c_no, c_name, c_type, c_user, c_date1, c_admin, c_date2, c_status = st.columns([0.5, 1.2, 1.4, 1.4, 1.4, 1.1, 1.4, 1.1, 1.5])
            
            c_id.write(f"{int(row['id'])}")
            c_no.write(f"{row['doc_id_text']}")
            c_name.write(f"{row['fullname']}")
            c_type.write(f"{row['doc_type']}")
            c_user.write(f"{row['creator_name']}")
            c_date1.write(f"{row['created_date_text']}")
            
            date_ins = row['inspected_date_text'] if pd.notna(row['inspected_date_text']) else "-"
            c_admin.write("-" if row['inspector_name'] == 'ยังไม่ได้ตรวจ' else f"{row['inspector_name']}")
            c_date2.write(f"{date_ins}")
            
            if row['check_status'] == 'รอตรวจเอกสาร':
                c_status.markdown("⏳ <span style='color:orange; font-weight:bold;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'อนุมัติ':
                c_status.markdown("🟢 <span style='color:green; font-weight:bold;'>อนุมัติ</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'ไม่อนุมัติ':
                c_status.markdown("🔴 <span style='color:#800000; font-weight:bold;'>ไม่อนุมัติ</span>", unsafe_allow_html=True)
            else:
                c_status.markdown("⚪ <span style='color:gray;'>ยกเลิก</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("💡 ยังไม่มีแฟ้มข้อมูลบันทึกสะสมในระบบ")


# ==========================================
# 🔵 หน้าจอเฉพาะสำหรับ: 🔍 ผู้ตรวจสอบเอกสาร (role == 'inspector')
# ==========================================
else:
    st.subheader("🔍 ศูนย์ควบคุมการพิจารณาตรวจสอบสิทธิ์ผู้ตรวจอนุมัติ")
    
    @st.dialog("🖊️ ลงชื่อพิจารณาอนุมัติเอกสารกลาง", width="large")
    def show_inspection_modal(doc_id):
        df_existing = conn.read(ttl="0d").dropna(subset=['doc_id_text'])
        data = df_existing[df_existing['id'] == doc_id].iloc[0]
        
        st.markdown(f"<h5>📦 ตรวจรับรองทะเบียนเลขที่: <span style='color:#800000;'>{data['doc_id_text']}</span></h5>", unsafe_allow_html=True)
        st.write(f"**ผู้ยื่นคำขอ:** {data['fullname']} | **ประเภทงาน:** {data['doc_type']} | **ผู้บันทึก:** {data['creator_name']} | **วันที่บันทึก:** {data['created_date_text']}")
        st.write("---")
        
        col_detail, col_form = st.columns([1, 1])
        with col_detail:
            st.markdown("📋 **สรุปไฟล์แนบตรวจสอบเบื้องต้น:**")
            for i in range(1, 7):
                status_key = f'doc{i}_status'
                note_key = f'doc{i}_note'
                if status_key in data and data[status_key] != "ไม่ได้ระบุ":
                    note_val = data[note_key] if pd.notna(data[note_key]) else "-"
                    st.write(f"{'✅' if data[status_key]=='ผ่าน' else '❌'} เอกสาร {i}: **{data[status_key]}** (หมายเหตุ: {note_val})")
                    
        with col_form:
            with st.form(key=f'modal_form_{doc_id}'):
                final_status = st.selectbox("มติสถานะภาพรวม *", ["รอตรวจเอกสาร", "อนุมัติ", "ไม่อนุมัติ", "ยกเลิก"])
                inspector_input = st.text_input("ผู้ลงนามตรวจสอบ", value=st.session_state.user_fullname, disabled=True)
                inspected_date = st.date_input("วันที่ลงนามอนุมัติเอกสาร *", datetime.now().date())
                submit_modal = st.form_submit_button("💾 ยืนยันผลมติภาพรวม")
                
            if submit_modal:
                df_existing.loc[df_existing['id'] == doc_id, 'inspector_name'] = inspector_input
                df_existing.loc[df_existing['id'] == doc_id, 'check_status'] = final_status
                df_existing.loc[df_existing['id'] == doc_id, 'inspected_date_text'] = str(inspected_date)
                
                conn.update(data=df_existing)
                st.success("🎉 บันทึกผลตรวจและวันที่รับรองลง Google Sheet สำเร็จ!")
                st.rerun()

    df_all = load_data()
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบ")
    else:
        st.markdown("<h4 style='color:#800000;'>📊 แดชบอร์ดสรุปสถิติทะเบียนรวม</h4>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div style='background-color:#fff5f5; padding:15px; border-radius:8px; border-left:5px solid orange; text-align:center;'><span style='color:#555;font-weight:bold;'>⏳ รอตรวจเอกสาร</span><br/><h2 style='color:orange;margin:5px;'>{len(df_all[df_all['check_status'] == 'รอตรวจเอกสาร'])}</h2></div>", unsafe_allow_html=True)
        m2.markdown(f"<div style='background-color:#f5fff5; padding:15px; border-radius:8px; border-left:5px solid green; text-align:center;'><span style='color:#555;font-weight:bold;'>🟢 อนุมัติแล้ว</span><br/><h2 style='color:green;margin:5px;'>{len(df_all[df_all['check_status'] == 'อนุมัติ'])}</h2></div>", unsafe_allow_html=True)
        m3.markdown(f"<div style='background-color:#fff0f0; padding:15px; border-radius:8px; border-left:5px solid #800000; text-align:center;'><span style='color:#555;font-weight:bold;'>🔴 ไม่อนุมัติ</span><br/><h2 style='color:#800000;margin:5px;'>{len(df_all[df_all['check_status'] == 'ไม่อนุมัติ'])}</h2></div>", unsafe_allow_html=True)
        m4.markdown(f"<div style='background-color:#f5f5f5; padding:15px; border-radius:8px; border-left:5px solid gray; text-align:center;'><span style='color:#555;font-weight:bold;'>⚪ ยกเลิก</span><br/><h2 style='color:gray;margin:5px;'>{len(df_all[df_all['check_status'] == 'ยกเลิก'])}</h2></div>", unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("<h3 style='color:#800000;'>📋 รายการข้อมูลเอกสารทุกลำดับชั้นในระบบ</h3>", unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 ค้นหาด่วนในคลังสารบรรณ (เลขหนังสือ / ชื่อผู้ยื่น)")
        if search_query:
            df_filtered = df_all[df_all['doc_id_text'].str.contains(search_query, case=False, na=False) | df_all['fullname'].str.contains(search_query, case=False, na=False)]
        else:
            df_filtered = df_all

        st.markdown("<div style='background-color:#800000; padding:10px; border-radius:8px 8px 0px 0px; color:white; font-weight:bold;'><div style='display:flex;'><div style='flex:0.5;'>ID</div><div style='flex:1.2;'>เลขหนังสือ</div><div style='flex:1.4;'>ชื่อผู้ยื่น</div><div style='flex:1.4;'>ประเภทงาน</div><div style='flex:1.4;'>ผู้บันทึก</div><div style='flex:1.1;'>วันที่บันทึก</div><div style='flex:1.4;'>ผู้ตรวจรับรอง</div><div style='flex:1.1;'>วันที่ตรวจ</div><div style='flex:1.5;'>Ref สถานะ</div><div style='flex:1.0;'>การจัดการ</div></div></div>", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            st.markdown("<div style='padding:12px 10px; border-bottom:1px solid #eee; display:flex; align-items:center; background-color:white;'>", unsafe_allow_html=True)
            c_id, c_no, c_name, c_type, c_user, c_date1, c_admin, c_date2, c_status, c_act = st.columns([0.5, 1.2, 1.4, 1.4, 1.4, 1.1, 1.4, 1.1, 1.5, 1.0])
            
            c_id.write(f"{int(row['id'])}")
            c_no.write(f"{row['doc_id_text']}")
            c_name.write(f"{row['fullname']}")
            c_type.write(f"{row['doc_type']}")
            c_user.write(f"{row['creator_name']}")
            c_date1.write(f"{row['created_date_text']}")
            
            date_ins = row['inspected_date_text'] if pd.notna(row['inspected_date_text']) else "-"
            c_admin.write("-" if row['inspector_name'] == 'ยังไม่ได้ตรวจ' else f"{row['inspector_name']}")
            c_date2.write(f"{date_ins}")
            
            if row['check_status'] == 'รอตรวจเอกสาร':
                c_status.markdown("⏳ <span style='color:orange; font-weight:bold;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'อนุมัติ':
                c_status.markdown("🟢 <span style='color:green; font-weight:bold;'>อนุมัติ</span>", unsafe_allow_html=True)
            elif row['check_status'] == 'ไม่อนุมัติ':
                c_status.markdown("🔴 <span style='color:#800000; font-weight:bold;'>ไม่อนุมัติ</span>", unsafe_allow_html=True)
            else:
                c_status.markdown("⚪ <span style='color:gray;'>ยกเลิก</span>", unsafe_allow_html=True)
            
            if c_act.button("🔍 ตรวจ", key=f"btn_{int(row['id'])}"):
                show_inspection_modal(int(row['id']))
            st.markdown("</div>", unsafe_allow_html=True)
