import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil
import io
from passporteye import read_mrz
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# App setup
# st.set_page_config(page_title="Zaireen Registration", layout="centered")
st.title("🧕 Zaireen Registration | زائرین کی رجسٹریشن")

# Define storage paths
BASE_DIR = Path("docs")
CSV_FILE = BASE_DIR / "zaireen.csv"
KAFLA_CSV = Path("kafla.csv")
TEMP_UPLOAD_DIR = BASE_DIR / "temp_uploads"
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Load kafla data
if not KAFLA_CSV.exists():
    st.error("⚠️ No Kafla data found. Please register a Kafla first.")
    st.stop()

kafla_df = pd.read_csv(KAFLA_CSV)
if kafla_df.empty:
    st.error("⚠️ Kafla list is empty. Please add entries first.")
    st.stop()

kafla_names = kafla_df.apply(lambda row: f"{row['Kafla Name']} ({row['Salar Name']})", axis=1).tolist()
kafla_map = dict(zip(kafla_names, kafla_df["Kafla Code"]))

selected_kafla_name = st.selectbox("Select Kafla | قافلہ منتخب کریں", options=kafla_names)

if not selected_kafla_name or selected_kafla_name not in kafla_map:
    st.warning("⚠️ Please select a valid Kafla.")
    st.stop()

kafla_code = kafla_map[selected_kafla_name]
kafla_dir = BASE_DIR / kafla_code / "zaireen"
kafla_dir.mkdir(parents=True, exist_ok=True)

# Load existing zaireen
if CSV_FILE.exists():
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Kafla Code", "Zaireen Name", "Passport Number", "Nationality", "Date of Birth", "Sex", "Scan Time"])

# Session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Utility function
def convert_mrz_date(mrz_date):
    if not mrz_date or len(mrz_date) != 6:
        return ""
    year = int(mrz_date[:2])
    year += 1900 if year >= 50 else 2000
    return f"{year}-{mrz_date[2:4]}-{mrz_date[4:6]}"

# Upload via uploader
st.markdown("### 📦 Upload Passport Images")
uploaded_files = st.file_uploader("Upload JPG or PNG", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
if uploaded_files:
    for file in uploaded_files:
        file_path = TEMP_UPLOAD_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.read())
        st.session_state.uploaded_files.append(str(file_path))

# Camera capture
st.markdown("### 📷 Scan Passport (Camera)")
camera_image = st.camera_input("Capture passport image")
if camera_image:
    path = TEMP_UPLOAD_DIR / "camera_passport.jpg"
    with open(path, "wb") as f:
        f.write(camera_image.read())

    mrz = read_mrz(str(path))
    if mrz:
        fields = mrz.to_dict()
        passport_number = fields["number"].strip()

        if not ((df["Kafla Code"] == kafla_code) & (df["Passport Number"].str.lower() == passport_number.lower())).any():
            full_name = f"{fields['surname']} {fields['names'].replace('<', ' ')}".strip()
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = {
                "Kafla Code": kafla_code,
                "Zaireen Name": full_name,
                "Passport Number": passport_number,
                "Nationality": fields["nationality"],
                "Date of Birth": convert_mrz_date(fields["date_of_birth"]),
                "Sex": fields["sex"],
                "Scan Time": scan_time
            }
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            z_dir = kafla_dir / passport_number
            z_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(path), z_dir / "passport.jpg")
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ Passport added via camera!")
        else:
            st.warning("⚠️ Duplicate passport detected.")
    else:
        st.error("❌ Could not read MRZ from image.")

# Process uploaded files
if st.session_state.uploaded_files:
    st.info(f"🗂 {len(st.session_state.uploaded_files)} file(s) ready")
    if st.button("🔍 Scan Uploaded Files"):
        accepted, rejected = 0, []

        for file_path in st.session_state.uploaded_files:
            mrz = read_mrz(file_path)
            if mrz:
                fields = mrz.to_dict()
                passport_number = fields["number"].strip()
                if not ((df["Kafla Code"] == kafla_code) & (df["Passport Number"].str.lower() == passport_number.lower())).any():
                    full_name = f"{fields['surname']} {fields['names'].replace('<', ' ')}".strip()
                    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row = {
                        "Kafla Code": kafla_code,
                        "Zaireen Name": full_name,
                        "Passport Number": passport_number,
                        "Nationality": fields["nationality"],
                        "Date of Birth": convert_mrz_date(fields["date_of_birth"]),
                        "Sex": fields["sex"],
                        "Scan Time": scan_time
                    }
                    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                    z_dir = kafla_dir / passport_number
                    z_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file_path, z_dir / "passport.jpg")
                    accepted += 1
                else:
                    rejected.append(f"{file_path} (Duplicate)")
            else:
                rejected.append(f"{file_path} (Unreadable)")

            os.remove(file_path)

        df.to_csv(CSV_FILE, index=False)
        st.session_state.uploaded_files.clear()
        st.success(f"✅ {accepted} added.")
        if rejected:
            st.warning("⚠️ Some files rejected:")
            st.code("\n".join(rejected))

# Display Zaireen list
st.markdown("### 🧾 Zaireen List")
filtered = df[df["Kafla Code"] == kafla_code]

if not filtered.empty:
    for idx, row in filtered.iterrows():
        with st.expander(f"{row['Zaireen Name']} - {row['Passport Number']}"):
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                visa_iran = st.file_uploader("Iran Visa", key=f"iran_{idx}", label_visibility="collapsed")
                if visa_iran:
                    with open(kafla_dir / row["Passport Number"] / "iran.jpg", "wb") as f:
                        f.write(visa_iran.read())

            with col2:
                visa_iraq = st.file_uploader("Iraq Visa", key=f"iraq_{idx}", label_visibility="collapsed")
                if visa_iraq:
                    with open(kafla_dir / row["Passport Number"] / "iraq.jpg", "wb") as f:
                        f.write(visa_iraq.read())

            with col3:
                if st.button("🗑️ Delete", key=f"del_{idx}"):
                    shutil.rmtree(kafla_dir / row["Passport Number"], ignore_errors=True)
                    df = df.drop(index=idx)
                    df.to_csv(CSV_FILE, index=False)
                    st.rerun()

    # Download CSV
    st.download_button("⬇️ Download CSV", data=filtered.to_csv(index=False), file_name=f"{kafla_code}_zaireen.csv", mime="text/csv")

    # Generate PDF
    def generate_pdf():
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("ZAIREEN LIST 2025", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Kafla: {selected_kafla_name}", styles["Normal"]),
            Spacer(1, 12),
        ]
        table_data = [["Name", "Passport No", "Nationality", "DOB", "Sex"]]
        for _, r in filtered.iterrows():
            table_data.append([r["Zaireen Name"], r["Passport Number"], r["Nationality"], r["Date of Birth"], r["Sex"]])
        t = Table(table_data)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
        ]))
        elements.extend([t, Spacer(1, 24), Paragraph("Sign: ____________________", styles["Normal"])])
        doc.build(elements)
        buf.seek(0)
        return buf

    pdf_data = generate_pdf()
    pdf_filename = f"{kafla_code}_{selected_kafla_name.replace(' ', '_')}.pdf"
    st.download_button("⬇️ Download PDF", data=pdf_data, file_name=pdf_filename, mime="application/pdf")
