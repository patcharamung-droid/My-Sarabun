import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
from streamlit_gsheets import GSheetsConnection
import io

# นำเข้าตัวแปลง HTML เป็น PDF อัจฉริยะ WeasyPrint
from weasyprint import HTML

# ตั้งค่าหน้าเว็บและสไตล์สีแดงเลือดหมูพรีเมียม
st.set_page_config(page_title="ระบบตรวจเช็ครายการเอกสารคำขอใบอนุญาต", layout="wide")

# ปรับแต่ง CSS ซ่อนเครื่องมือระบบ และจัดการตำแหน่งลายน้ำในหน้าเว็บ Streamlit
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stToolbar"] {display: none !important;}
        button[title="View source code"] {display: none !important;}
        
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
        
        section[data-testid="stSidebar"] { 
            background-color: #4a0000; 
            color: white; 
        }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { 
            color: #ffffff !important; 
        }

        .sidebar-watermark {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 260px; 
            text-align: center;
            color: rgba(255, 255, 255, 0.4) !important; 
            font-size: 13px;
            font-family: 'Sarabun', sans-serif;
            pointer-events: none;
            z-index: 999;
        }

        .table-text {
            font-size: 14px !important;
            font-family: 'Sarabun', sans-serif;
            color: #333333;
            word-break: break-word;
        }
        
        /* 🎯 [แก้ไขสำเร็จ] บังคับให้ข้อความหัวตารางแสดงผล "ตรงกลางช่อง" ตัวหนา และสีขาว */
        .table-header-text {
            font-size: 14px !important;
            font-family: 'Sarabun', sans-serif !important;
            color: #ffffff !important;
            font-weight: bold !important;
            text-align: center !important;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

def get_gsheet_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้ กรุณาตรวจสอบ Secrets")
        st.stop()

conn = get_gsheet_connection()

USERS = {
    "Patchara.mu": {"password": "431799", "role": "creator", "name": "นายพัชระ มุงคุลคำซาว"},
    "Supachai.t": {"password": "431612", "role": "creator", "name": "นายศุภชัย ไทยโส"},
    "Theera.j": {"password": "431800", "role": "creator", "name": "นายธีระ จงสมชัย"},
    "Songyos.r": {"password": "431522", "role": "inspector", "name": "นายทรงยศ รังษา"}
}

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "user_fullname" not in st.session_state: st.session_state.user_fullname = None

# --- หน้าจอเลือกล็อกอิน ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🏛️ ระบบตรวจเช็ครายการเอกสารคำขอใบอนุญาต</h1>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        with st.form(key='login_form'):
            st.markdown("<h3 style='text-align: center;'>🔐 เข้าสู่ระบบ</h3>", unsafe_allow_html=True)
            username_input = st.text_input("ชื่อผู้ใช้งาน", placeholder="ระบุชื่อผู้ใช้งาน")
            password_input = st.text_input("รหัสผ่าน", type="password", placeholder="••••••")
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
st.sidebar.markdown("<h2 style='text-align:center;'>🏛️ ส่วนใบอนุญาต</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
st.sidebar.write(f"**ผู้ใช้งาน:** {st.session_state.user_fullname}")
st.sidebar.write(f"**สิทธิ์ระบบ:** {'📝 เจ้าหน้าที่ตรวจเอกสาร' if st.session_state.user_role == 'creator' else '🔍 ผู้อนุมัติออกใบอนุญาต'}")
st.sidebar.write("---")

if st.sidebar.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False; st.rerun()

st.sidebar.markdown('<div class="sidebar-watermark">Developed by Patchara.mu</div>', unsafe_allow_html=True)

status_options = ["ผ่าน", "ไม่ผ่าน"]

def render_doc_row(label):
    c_status, c_note = st.columns([1, 2])
    with c_status: status = st.radio(label, status_options, index=0, horizontal=True, key=f"status_{label}")
    with c_note: note = st.text_input("หมายเหตุเพิ่มเติม", placeholder=f"ระบุรายละเอียด", key=f"note_{label}")
    return status, note

def load_data():
    try:
        df = conn.read(ttl="0d")
        if df.empty: return pd.DataFrame()
        df = df.dropna(subset=['doc_id_text'])
        required_cols = ['source_place', 'inspector_name', 'inspected_date_text', 'check_status', 'inspector_comment']
        for col in required_cols:
            if col not in df.columns: df[col] = "-"
        return df.sort_values(by="id", ascending=False)
    except: return pd.DataFrame()


# ✨ ฟังก์ชันเจน PDF ด้วย WeasyPrint (หัวตารางในเอกสารเป็นตัวหนาสีขาวเรียบร้อย)
def generate_report_pdf_weasy(row_data):
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
            @page {{
                size: A4;
                margin: 20px;
            }}
            body {{
                font-family: 'Sarabun', sans-serif;
                color: #333;
                line-height: 1.6;
                font-size: 15px;
            }}
            .title {{
                color: #800000;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 2px;
            }}
            .subtitle {{
                font-size: 16px;
                text-align: center;
                color: #555;
                margin-bottom: 25px;
            }}
            .info-table {{
                width: 100%;
                margin-bottom: 20px;
                border-collapse: collapse;
            }}
            .info-table td {{
                padding: 6px;
                vertical-align: top;
            }}
            .section-title {{
                font-weight: bold;
                font-size: 16px;
                margin-top: 15px;
                margin-bottom: 8px;
                color: #333;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th {{
                background-color: #800000;
                color: #ffffff !important;
                font-weight: bold !important;
                text-align: left;
                padding: 10px;
                border: 1px solid #ccc;
            }}
            .data-table td {{
                padding: 10px;
                border: 1px solid #ccc;
            }}
            .status-pass {{ color: green; font-weight: bold; }}
            .status-fail {{ color: red; font-weight: bold; }}
            
            .summary-box {{
                width: 100%;
                border: 1px solid #ddd;
                border-collapse: collapse;
                margin-bottom: 40px;
            }}
            .summary-box td {{
                padding: 12px;
                border: 1px solid #ddd;
            }}
            .signature-container {{
                width: 100%;
                margin-top: 50px;
            }}
            .signature-box {{
                width: 48%;
                text-align: center;
                display: inline-block;
                vertical-align: top;
                line-height: 2.0;
            }}
        </style>
    </head>
    <body>
        <div class="title">REPORT: FORM OF APPLICATION LICENSE INSPECTION</div>
        <div class="subtitle">รายงานผลการพิจารณาตรวจสอบยืนยันเอกสารคำขอใบอนุญาต</div>
        
        <table class="info-table">
            <tr>
                <td style="width:15%"><b>เลขหนังสือ:</b></td>
                <td style="width:35%">{row_data['doc_id_text']}</td>
                <td style="width:15%"><b>แหล่งที่มา:</b></td>
                <td style="width:35%">{row_data['source_place']}</td>
            </tr>
            <tr>
                <td><b>ชื่อผู้ยื่นคำขอ:</b></td>
                <td>{row_data['fullname']}</td>
                <td><b>ประเภทคำขอ:</b></td>
                <td>{row_data['doc_type']}</td>
            </tr>
        </table>
        
        <div class="section-title">📋 รายละเอียดและสถานะเอกสารแนบ (Attachment Checklist)</div>
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 25%">ลำดับเอกสาร</th>
                    <th style="width: 20%">สถานะผลตรวจ</th>
                    <th style="width: 55%">รายละเอียดหมายเหตุเพิ่มเติม</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i in range(1, 7):
        st_key = f'doc{i}_status'
        nt_key = f'doc{i}_note'
        if st_key in row_data and row_data[st_key] != "ไม่ได้ระบุ":
            status_class = "status-pass" if row_data[st_key] == "ผ่าน" else "status-fail"
            note_val = row_data[nt_key] if (pd.notna(row_data[nt_key]) and row_data[nt_key] != "") else "-"
            html_content += f"""
                <tr>
                    <td>เอกสารแนบลำดับที่ {i}</td>
                    <td class="{status_class}">{row_data[st_key]}</td>
                    <td>{note_val}</td>
                </tr>
            """
            
    comment_val = row_data['inspector_comment'] if pd.notna(row_data['inspector_comment']) else "-"
    html_content += f"""
            </tbody>
        </table>
        
        <div class="section-title">🔍 สรุปผลพิจารณาจากผู้ตรวจอนุมัติ</div>
        <table class="summary-box">
            <tr>
                <td style="width: 25%; background-color:#fafafa;"><b>สถานะภาพรวม:</b></td>
                <td style="color:#800000; font-weight:bold;">{row_data['check_status']}</td>
            </tr>
            <tr>
                <td style="background-color:#fafafa;"><b>ความคิดเห็นเพิ่มเติม:</b></td>
                <td>{comment_val}</td>
            </tr>
        </table>
        
        <div class="signature-container">
            <div class="signature-box" style="float: left;">
                ลงชื่อ.......................................................... ผู้ตรวจ<br>
                ( {row_data['creator_name']} )<br>
                ตำแหน่ง: เจ้าหน้าที่ตรวจเอกสารคำขอ<br>
                ลงวันที่: {row_data['created_date_text']}
            </div>
            <div class="signature-box" style="float: right;">
                ลงชื่อ.......................................................... ผู้อนุมัติ<br>
                ( {row_data['inspector_name']} )<br>
                ตำแหน่ง: ผู้ตรวจอนุมัติออกใบอนุญาต<br>
                ลงวันที่: {row_data['inspected_date_text']}
            </div>
        </div>
    </body>
    </html>
    """
    return HTML(string=html_content).write_pdf()


# เกลี่ยสัดส่วนคอลัมน์ตารางให้ชื่อผู้ยื่น (1.5) ผู้บันทึก (1.5) และผู้ตรวจ (1.5) มีพื้นที่กว้างพอดี ไม่ตัดข้อความ
col_widths_creator = [0.4, 1.0, 1.0, 1.5, 1.5, 1.7, 0.9, 1.3, 0.9, 1.4, 1.1, 1.3]
col_widths_inspector = [0.4, 1.0, 1.0, 1.5, 1.5, 1.7, 0.9, 1.3, 0.9, 1.4, 1.1, 1.3]

# ==========================================
# 🟢 หน้าจอเฉพาะสำหรับ: 📝 ผู้บันทึกข้อมูล (role == 'creator')
# ==========================================
if st.session_state.user_role == "creator":
    st.subheader("📝 แบบเช็ครายการเอกสารคำขอและตรวจสอบเบื้องต้น")
    
    if 'visible_docs' not in st.session_state: 
        st.session_state.visible_docs = 3

    with st.form(key='creator_form_sheet'):
        col1, col2 = st.columns(2)
        with col1:
            source_place = st.selectbox("แหล่งที่มา *", ["ASMS", "NBTC Service Portal", "ONE STOP SERVICE"])
            doc_id_text = st.text_input("เลขหนังสือ *", placeholder="ระบุเลขหนังสือ")
            creator_name = st.text_input("ผู้บันทึก", value=st.session_state.user_fullname, disabled=True)
        with col2:
            fullname = st.text_input("ชื่อ-สกุลผู้ยื่นคำขอ *", placeholder="ระบุชื่อผู้ยื่นคำขอ")
            doc_type = st.text_input("ประเภทคำขอ *", placeholder="คำขอใบอนุญาต...")
            created_date = st.date_input("วันที่บันทึก *", datetime.now().date())
            
        st.write("---")
        st.markdown(f"<h4 style='color:#800000;'>📄 รายการตรวจเช็คเอกสารแนบ (กำลังเปิดใช้งาน {st.session_state.visible_docs} ช่อง)</h4>", unsafe_allow_html=True)
        
        doc_data_inputs = {}
        for i in range(1, 7):
            if i <= st.session_state.visible_docs:
                status, note = render_doc_row(f"📄 เอกสาร {i}")
                doc_data_inputs[f"doc{i}_status"] = status
                doc_data_inputs[f"doc{i}_note"] = note
            else:
                doc_data_inputs[f"doc{i}_status"] = "ไม่ได้ระบุ"
                doc_data_inputs[f"doc{i}_note"] = ""
            
        st.write("---")
        submit_button = st.form_submit_button(label='💾 บันทึก')

    c_btn1, c_btn2, _ = st.columns([1.2, 1.4, 5])
    with c_btn1:
        if st.button("➕ เพิ่มช่องเอกสาร") and st.session_state.visible_docs < 6:
            st.session_state.visible_docs += 1; st.rerun()
    with c_btn2:
        if st.button("➖ ลบช่องเอกสาร") and st.session_state.visible_docs > 1:
            st.session_state.visible_docs -= 1; st.rerun()

    if submit_button:
        if not doc_id_text or not fullname or not doc_type:
            st.error("❌ กรุณากรอกข้อมูลด่านหลักให้ครบถ้วน")
        else:
            with st.spinner("⏳ กำลังเชื่อมต่อและส่งข้อมูล..."):
                time_lib.sleep(3)
            
            df_existing = conn.read(ttl="0d").dropna(subset=['doc_id_text'])
            next_id = 1 if df_existing.empty else int(df_existing['id'].max()) + 1
            
            new_row_data = {
                "id": next_id, "source_place": source_place, "doc_id_text": doc_id_text, "fullname": fullname, "doc_type": doc_type,
                "creator_name": creator_name, "created_date_text": str(created_date),
                "inspector_name": "ยังไม่ได้ตรวจ", "inspected_date_text": "-", "check_status": "รอตรวจเอกสาร",
                "inspector_comment": "-"
            }
            new_row_data.update(doc_data_inputs)
            
            new_row = pd.DataFrame([new_row_data])
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(data=updated_df)
            
            st.session_state.visible_docs = 3  
            st.success("🎉 บันทึกข้อมูลเรียบร้อย!")
            st.rerun()

    st.write("---")
    
    col_title, col_ref = st.columns([5, 1])
    with col_title:
        st.markdown("<h3 style='color:#800000; margin:0;'>📋 รายการเอกสาร</h3>", unsafe_allow_html=True)
    with col_ref:
        if st.button("🔄 รีเฟรชรายการ", key="ref_creator"):
            st.cache_data.clear(); st.rerun()
            
    df_raw = load_data()
    if not df_raw.empty:
        sq = st.text_input("🔍 พิมพ์ค้นหาข้อมูล (เลขหนังสือ / ชื่อผู้ยื่น)")
        if sq:
            df_filtered = df_raw[df_raw['doc_id_text'].str.contains(sq, case=False, na=False) | df_raw['fullname'].str.contains(sq, case=False, na=False)]
        else:
            df_filtered = df_raw

        st.markdown("<div style='background-color:#800000; padding:12px 10px; border-radius:8px 8px 0px 0px;'><div style='display:flex; align-items:center; text-align:left;'>"
                    f"<div style='flex:{col_widths_creator[0]};' class='table-header-text'>ID</div>"
                    f"<div style='flex:{col_widths_creator[1]};' class='table-header-text'>แหล่งที่มา</div>"
                    f"<div style='flex:{col_widths_creator[2]};' class='table-header-text'>เลขหนังสือ</div>"
                    f"<div style='flex:{col_widths_creator[3]};' class='table-header-text'>ชื่อผู้ยื่น</div>"
                    f"<div style='flex:{col_widths_creator[4]};' class='table-header-text'>ประเภทงาน</div>"
                    f"<div style='flex:{col_widths_creator[5]};' class='table-header-text'>ผู้ตรวจเอกสาร</div>"
                    f"<div style='flex:{col_widths_creator[6]};' class='table-header-text'>วันที่บันทึก</div>"
                    f"<div style='flex:{col_widths_creator[7]};' class='table-header-text'>ผู้อนุมัติ</div>"
                    f"<div style='flex:{col_widths_creator[8]};' class='table-header-text'>วันที่อนุมัติ</div>"
                    f"<div style='flex:{col_widths_creator[9]};' class='table-header-text'>ความคิดเห็นผู้อนุมัติ</div>"
                    f"<div style='flex:{col_widths_creator[10]};' class='table-header-text'>สถานะ</div>"
                    f"<div style='flex:{col_widths_creator[11]};' class='table-header-text'>การจัดการ</div>"
                    "</div></div>", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            st.markdown("<div style='padding:10px 10px; border-bottom:1px solid #eee; display:flex; align-items:center; background-color:white;'>", unsafe_allow_html=True)
            c_id, c_src, c_no, c_name, c_type, c_user, c_date1, c_admin, c_date2, c_comment, c_status, c_act = st.columns(col_widths_creator)
            
            c_id.write(f"{int(row['id'])}")
            c_src.write(f"{row['source_place'] if pd.notna(row['source_place']) else '-'}")
            c_no.write(f"{row['doc_id_text']}")
            c_name.write(f"{row['fullname']}")
            c_type.write(f"{row['doc_type']}")
            c_user.write(f"{row['creator_name']}")
            c_date1.write(f"{row['created_date_text']}")
            
            c_admin.write("-" if row['inspector_name'] == 'ยังไม่ได้ตรวจ' else row['inspector_name'])
            c_date2.write(f"{row['inspected_date_text'] if pd.notna(row['inspected_date_text']) else '-'}")
            c_comment.write(f"{row['inspector_comment'] if pd.notna(row['inspector_comment']) else '-'}")
            
            current_status = row['check_status']
            if current_status == 'รอตรวจเอกสาร':
                c_status.markdown("⏳ <span style='color:orange; font-weight:bold; font-size:14px;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
                c_act.markdown("<div style='color:gray; font-size:13px; font-style:italic; padding-left:5px;'>⏳ รอผลตรวจ</div>", unsafe_allow_html=True)
            else:
                if current_status == 'อนุมัติออกใบอนุญาต':
                    c_status.markdown("🟢 <span style='color:green; font-weight:bold; font-size:14px;'>อนุมัติออกใบอนุญาต</span>", unsafe_allow_html=True)
                elif current_status == 'ไม่อนุมัติคำขอ':
                    c_status.markdown("🔴 <span style='color:#800000; font-weight:bold; font-size:14px;'>ไม่อนุมัติคำขอ</span>", unsafe_allow_html=True)
                else:
                    c_status.markdown("⚪ <span style='color:gray; font-size:14px;'>ยกเลิกคำขอ</span>", unsafe_allow_html=True)
                
                # ปุ่มดาวน์โหลดรายงาน PDF สำหรับฝั่ง Creator
                pdf_data = generate_report_pdf_weasy(row)
                c_act.download_button(
                    label="📄 รายงาน",
                    data=pdf_data,
                    file_name=f"Report_License_{row['doc_id_text'].replace('/','_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_creator_{int(row['id'])}"
                )
                
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("💡 ยังไม่มีแฟ้มข้อมูลบันทึกสะสมในระบบ")


# ==========================================
# 🔵 หน้าจอเฉพาะสำหรับ: 🔍 ผู้ตรวจสอบเอกสาร (role == 'inspector')
# ==========================================
else:
    st.subheader("📝 แบบพิจารณาตรวจสอบรายการเอกสารคำขอและอนุมัติพิมพ์ใบอนุญาต")
    
    @st.dialog("🖊️ พิจารณาอนุมัติออกใบอนุญาต", width="large")
    def show_inspection_modal(doc_id):
        df_existing = conn.read(ttl="0d").dropna(subset=['doc_id_text'])
        data = df_existing[df_existing['id'] == doc_id].iloc[0]
        
        if data['check_status'] != "รอตรวจเอกสาร":
            st.error("🔒 เอกสารรายการนี้ได้รับการพิจารณาและล็อกสถานะถาวรแล้ว ไม่สามารถแก้ไขได้")
            time_lib.sleep(2); st.rerun(); return

        st.markdown(f"<h5>📦 คำขอเลขที่: <span style='color:#800000;'>{data['doc_id_text']}</span></h5>", unsafe_allow_html=True)
        st.write(f"**แหล่งที่มา:** {data['source_place']} | **ผู้ยื่นคำขอ:** {data['fullname']} | **ประเภทงาน:** {data['doc_type']} | **ผู้ตรวจเอกสาร:** {data['creator_name']} ({data['created_date_text']})")
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
                final_status = st.selectbox("สถานะภาพรวม *", ["อนุมัติออกใบอนุญาต", "ไม่อนุมัติคำขอ", "ยกเลิกคำขอ"])
                inspector_input = st.text_input("ผู้ลงนามอนุมัติ", value=st.session_state.user_fullname, disabled=True)
                inspected_date = st.date_input("วันที่ลงนามอนุมัติ *", datetime.now().date())
                
                exist_comment = data['inspector_comment'] if ('inspector_comment' in data and pd.notna(data['inspector_comment']) and data['inspector_comment'] != "-") else ""
                inspector_comment_input = st.text_area("ความคิดเห็นผู้อนุมัติ", value=exist_comment, placeholder="ระบุเหตุผล ข้อเสนอแนะ หรือคำสั่งการเพิ่มเติม")
                
                submit_modal = st.form_submit_button("💾 ยืนยันพิมพ์ใบอนุญาต")
                
            if submit_modal:
                df_existing.loc[df_existing['id'] == doc_id, 'inspector_name'] = inspector_input
                df_existing.loc[df_existing['id'] == doc_id, 'check_status'] = final_status
                df_existing.loc[df_existing['id'] == doc_id, 'inspected_date_text'] = str(inspected_date)
                df_existing.loc[df_existing['id'] == doc_id, 'inspector_comment'] = inspector_comment_input if inspector_comment_input else "-"
                
                conn.update(data=df_existing)
                st.success("🎉 บันทึกผลตรวจเรียบร้อย ระบบได้ทำการล็อกสถานะรายการนี้แล้ว!")
                time_lib.sleep(1); st.rerun()

    df_all = load_data()
    if df_all.empty:
        st.info("💡 ขณะนี้ยังไม่มีรายการเอกสารส่งเข้ามาในระบบ")
    else:
        st.markdown("<h4 style='color:#800000;'>📊 สรุปข้อมูลรายการคำขอ</h4>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        
        # 🎯 [แก้ไขแล้ว] เปลี่ยนตัวนับบล็อกจาก 'อนุมัติพิมพ์ใบอนุญาต' ให้ตรงกับค่าในระบบคือ 'อนุมัติออกใบอนุญาต' เพื่อแสดงจำนวนที่ถูกต้อง
        m1.markdown(f"<div style='background-color:#fff5f5; padding:15px; border-radius:8px; border-left:5px solid orange; text-align:center;'><span style='color:#555;font-weight:bold;'>⏳ รอตรวจเอกสาร</span><br/><h2 style='color:orange;margin:5px;'>{len(df_all[df_all['check_status'] == 'รอตรวจเอกสาร'])}</h2></div>", unsafe_allow_html=True)
        m2.markdown(f"<div style='background-color:#f5fff5; padding:15px; border-radius:8px; border-left:5px solid green; text-align:center;'><span style='color:#555;font-weight:bold;'>🟢 อนุมัติออกใบอนุญาต</span><br/><h2 style='color:green;margin:5px;'>{len(df_all[df_all['check_status'] == 'อนุมัติออกใบอนุญาต'])}</h2></div>", unsafe_allow_html=True)
        m3.markdown(f"<div style='background-color:#fff0f0; padding:15px; border-radius:8px; border-left:5px solid #800000; text-align:center;'><span style='color:#555;font-weight:bold;'>🔴 ไม่อนุมัติคำขอ</span><br/><h2 style='color:#800000;margin:5px;'>{len(df_all[df_all['check_status'] == 'ไม่อนุมัติคำขอ'])}</h2></div>", unsafe_allow_html=True)
        m4.markdown(f"<div style='background-color:#f5f5f5; padding:15px; border-radius:8px; border-left:5px solid gray; text-align:center;'><span style='color:#555;font-weight:bold;'>⚪ ยกเลิกคำขอ</span><br/><h2 style='color:gray;margin:5px;'>{len(df_all[df_all['check_status'] == 'ยกเลิกคำขอ'])}</h2></div>", unsafe_allow_html=True)
        
        st.write("---")
        
        col_title, col_ref = st.columns([5, 1])
        with col_title:
            st.markdown("<h3 style='color:#800000; margin:0;'>📋 รายการข้อมูลคำขอในระบบ</h3>", unsafe_allow_html=True)
        with col_ref:
            if st.button("🔄 รีเฟรชรายการ", key="ref_inspector"):
                st.cache_data.clear(); st.rerun()
        
        search_query = st.text_input("🔍 ค้นหารายการ (เลขหนังสือ / ชื่อผู้ยื่น)")
        if search_query:
            df_filtered = df_all[df_all['doc_id_text'].str.contains(search_query, case=False, na=False) | df_all['fullname'].str.contains(search_query, case=False, na=False)]
        else:
            df_filtered = df_all

        st.markdown("<div style='background-color:#800000; padding:12px 10px; border-radius:8px 8px 0px 0px;'><div style='display:flex; align-items:center; text-align:left;'>"
                    f"<div style='flex:{col_widths_inspector[0]};' class='table-header-text'>ID</div>"
                    f"<div style='flex:{col_widths_inspector[1]};' class='table-header-text'>แหล่งที่มา</div>"
                    f"<div style='flex:{col_widths_inspector[2]};' class='table-header-text'>เลขหนังสือ</div>"
                    f"<div style='flex:{col_widths_inspector[3]};' class='table-header-text'>ชื่อผู้ยื่น</div>"
                    f"<div style='flex:{col_widths_inspector[4]};' class='table-header-text'>ประเภทงาน</div>"
                    f"<div style='flex:{col_widths_inspector[5]};' class='table-header-text'>ผู้ตรวจเอกสาร</div>"
                    f"<div style='flex:{col_widths_inspector[6]};' class='table-header-text'>วันที่บันทึก</div>"
                    f"<div style='flex:{col_widths_inspector[7]};' class='table-header-text'>ผู้อนุมัติ</div>"
                    f"<div style='flex:{col_widths_inspector[8]};' class='table-header-text'>วันที่อนุมัติ</div>"
                    f"<div style='flex:{col_widths_inspector[9]};' class='table-header-text'>ความคิดเห็นผู้อนุมัติ</div>"
                    f"<div style='flex:{col_widths_inspector[10]};' class='table-header-text'>สถานะ</div>"
                    f"<div style='flex:{col_widths_inspector[11]};' class='table-header-text'>การจัดการ</div>"
                    "</div></div>", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            st.markdown("<div style='padding:6px 10px; border-bottom:1px solid #eee; display:flex; align-items:center; background-color:white;'>", unsafe_allow_html=True)
            c_id, c_src, c_no, c_name, c_type, c_user, c_date1, c_admin, c_date2, c_comment, c_status, c_act = st.columns(col_widths_inspector)
            
            c_id.write(f"{int(row['id'])}")
            c_src.write(f"{row['source_place'] if pd.notna(row['source_place']) else '-'}")
            c_no.write(f"{row['doc_id_text']}")
            c_name.write(f"{row['fullname']}")
            c_type.write(f"{row['doc_type']}")
            c_user.write(f"{row['creator_name']}")
            c_date1.write(f"{row['created_date_text']}")
            
            c_admin.write("-" if row['inspector_name'] == 'ยังไม่ได้ตรวจ' else row['inspector_name'])
            c_date2.write(f"{row['inspected_date_text'] if pd.notna(row['inspected_date_text']) else '-'}")
            c_comment.write(f"{row['inspector_comment'] if pd.notna(row['inspector_comment']) else '-'}")
            
            current_status = row['check_status']
            if current_status == 'รอตรวจเอกสาร':
                c_status.markdown("⏳ <span style='color:orange; font-weight:bold; font-size:14px;'>รอตรวจเอกสาร</span>", unsafe_allow_html=True)
            elif current_status == 'อนุมัติออกใบอนุญาต':
                c_status.markdown("🟢 <span style='color:green; font-weight:bold; font-size:14px;'>อนุมัติออกใบอนุญาต</span>", unsafe_allow_html=True)
            elif current_status == 'ไม่อนุมัติคำขอ':
                c_status.markdown("🔴 <span style='color:#800000; font-weight:bold; font-size:14px;'>ไม่อนุมัติคำขอ</span>", unsafe_allow_html=True)
            else:
                c_status.markdown("⚪ <span style='color:gray; font-size:14px;'>ยกเลิกคำขอ</span>", unsafe_allow_html=True)
            
            if current_status == 'รอตรวจเอกสาร':
                if c_act.button("🔍 ตรวจ", key=f"btn_{int(row['id'])}"):
                    show_inspection_modal(int(row['id']))
            else:
                pdf_data = generate_report_pdf_weasy(row)
                c_act.download_button(
                    label="📄 รายงาน",
                    data=pdf_data,
                    file_name=f"Report_License_{row['doc_id_text'].replace('/','_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_inspector_{int(row['id'])}"
                )
                
            st.markdown("</div>", unsafe_allow_html=True)
