import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from pathlib import Path
from PIL import Image
import shutil
import io
from passporteye import read_mrz
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# App title and config
st.set_page_config(page_title="Zaireen Registration", layout="centered")
st.title("🧕 Zaireen Registration | زائرین کی رجسٹریشن")

# Define data paths
BASE_DIR = Path("docs")
BASE_DIR.mkdir(exist_ok=True)
CSV_FILE = BASE_DIR / "zaireen.csv"
KAFLA_CSV = Path("kafla.csv")
TEMP_UPLOAD_DIR = BASE_DIR / "temp_uploads"
TEMP_UPLOAD_DIR.mkdir(exist_ok=True)

# Session state for tracking
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# Load kafla list
if KAFLA_CSV.exists():
    kafla_df = pd.read_csv(KAFLA_CSV)
else:
    st.error("⚠️ No Kafla data found. Please register a Kafla first.")
    st.stop()

# Load existing zaireen data
if CSV_FILE.exists():
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Kafla Code", "Zaireen Name", "Passport Number", "Nationality", "Date of Birth", "Sex", "Scan Time"])

# Select kafla
kafla_names = kafla_df.apply(lambda row: f"{row['Kafla Name']} ({row['Salar Name']})", axis=1).tolist()
kafla_map = dict(zip(kafla_names, kafla_df["Kafla Code"]))
kafla_reverse_map = dict(zip(kafla_df["Kafla Code"], kafla_names))

selected_kafla_name = st.selectbox("Select Kafla | قافلہ منتخب کریں", options=kafla_names)
kafla_code = kafla_map[selected_kafla_name]

kafla_dir = BASE_DIR / kafla_code / "zaireen"
kafla_dir.mkdir(parents=True, exist_ok=True)

# Function to convert MRZ date
def convert_mrz_date(mrz_date):
    if not mrz_date or len(mrz_date) != 6:
        return ""
    year = int(mrz_date[:2])
    year += 1900 if year >= 50 else 2000
    return f"{year}-{mrz_date[2:4]}-{mrz_date[4:6]}"

# Upload area
st.markdown("### 📦 Upload Passport Images in Bulk")
uploaded_files = st.file_uploader("Upload JPG or PNG files", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if uploaded_files:
    for file in uploaded_files:
        file_path = TEMP_UPLOAD_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.read())
        if file.name not in st.session_state.uploaded_files:
            st.session_state.uploaded_files.append(file.name)

# Camera input for passport MRZ
st.markdown("### 📷 Scan Passport Using Camera")
camera_image = st.camera_input("Capture passport image (MRZ area should be clearly visible)")

if camera_image:
    with open("temp_camera_passport.jpg", "wb") as f:
        f.write(camera_image.read())
    mrz = read_mrz("temp_camera_passport.jpg")
    if mrz:
        fields = mrz.to_dict()
        passport_number = fields["number"]
        if not ((df["Kafla Code"] == kafla_code) & (df["Passport Number"] == passport_number)).any():
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
            zaireen_subdir = kafla_dir / passport_number
            zaireen_subdir.mkdir(parents=True, exist_ok=True)
            shutil.copy("temp_camera_passport.jpg", zaireen_subdir / "passport.jpg")
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ Passport scanned and added successfully via camera!")
        else:
            st.warning("⚠️ Duplicate passport detected. Entry skipped.")
    else:
        st.error("❌ Could not read MRZ from camera. Please try again with a clearer image.")

# Process uploaded files
if st.session_state.uploaded_files:
    st.info(f"🗂 {len(st.session_state.uploaded_files)} file(s) in queue: " + ", ".join(st.session_state.uploaded_files))
    if st.button("🔍 Scan Uploaded Images"):
        accepted, rejected = 0, []
        for fname in st.session_state.uploaded_files:
            file_path = TEMP_UPLOAD_DIR / fname
            mrz = read_mrz(str(file_path))
            if mrz:
                fields = mrz.to_dict()
                passport_number = fields["number"]
                if not ((df["Kafla Code"] == kafla_code) & (df["Passport Number"] == passport_number)).any():
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
                    zaireen_subdir = kafla_dir / passport_number
                    zaireen_subdir.mkdir(parents=True, exist_ok=True)
                    shutil.copy(str(file_path), zaireen_subdir / "passport.jpg")
                    accepted += 1
                else:
                    rejected.append(f"{fname} (Duplicate)")
            else:
                rejected.append(f"{fname} (MRZ Not Readable)")
            os.remove(file_path)

        df.to_csv(CSV_FILE, index=False)
        st.session_state.uploaded_files.clear()
        st.success(f"✅ {accepted} scanned successfully!")
        if rejected:
            st.warning(f"⚠️ {len(rejected)} rejected:")
            st.code("\n".join(rejected))

# Show Zaireen list for selected kafla
st.markdown("### 🧾 Zaireen List")
kafla_df_filtered = df[df["Kafla Code"] == kafla_code]

if not kafla_df_filtered.empty:
    for idx, row in kafla_df_filtered.iterrows():
        with st.expander(f"{row['Zaireen Name']} - {row['Passport Number']}"):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                visa_iran = st.file_uploader("Iran Visa", key=f"iran_{idx}", label_visibility="collapsed")
                if visa_iran:
                    path = kafla_dir / row["Passport Number"] / "iran_visa.jpg"
                    with open(path, "wb") as f:
                        f.write(visa_iran.read())
            with col2:
                visa_iraq = st.file_uploader("Iraq Visa", key=f"iraq_{idx}", label_visibility="collapsed")
                if visa_iraq:
                    path = kafla_dir / row["Passport Number"] / "iraq_visa.jpg"
                    with open(path, "wb") as f:
                        f.write(visa_iraq.read())
            with col3:
                if st.button("🗑️ Delete", key=f"del_{idx}"):
                    shutil.rmtree(kafla_dir / row["Passport Number"], ignore_errors=True)
                    df = df.drop(index=idx)
                    df.to_csv(CSV_FILE, index=False)
                    st.rerun()

    # Download CSV
    st.download_button("⬇️ Download CSV", data=kafla_df_filtered.to_csv(index=False), file_name=f"{kafla_code}_zaireen.csv", mime="text/csv")

    # Generate PDF
    def generate_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("<b>ZAIREEN LIST 2025 (KHI-GWD)</b>", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Kafla: {selected_kafla_name}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Vehicle No: ____________    Date: ____________", styles["Normal"]),
            Spacer(1, 12),
        ]
        data = [["Name", "Passport No", "Nationality", "DOB", "Sex"]]
        for _, r in kafla_df_filtered.iterrows():
            data.append([r["Zaireen Name"], r["Passport Number"], r["Nationality"], r["Date of Birth"], r["Sex"]])
        t = Table(data)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Sign: ____________________", styles["Normal"]))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_buffer = generate_pdf()
    st.download_button("⬇️ Download PDF", data=pdf_buffer, file_name=f"{kafla_code}_{selected_kafla_name}.pdf", mime="application/pdf")
