import streamlit as st
import pandas as pd
import os
from pathlib import Path
from PIL import Image
from PyPDF2 import PdfMerger
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# App Config
#st.set_page_config(page_title="Convoy Documents Submission", layout="centered")
st.title("🚍 Convoy Documents Submission | قافلے کی دستاویزات")

# Setup folders
BASE_DIR = Path("docs")
DOCS_DIR = BASE_DIR / "convoy_docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
KAFLA_CSV = Path("kafla.csv")

if not KAFLA_CSV.exists():
    st.error("⚠️ No Kafla data found. Please register a Kafla first.")
    st.stop()

kafla_df = pd.read_csv(KAFLA_CSV)
kafla_names = kafla_df.apply(lambda row: f"{row['Kafla Name']} ({row['Salar Name']})", axis=1).tolist()
kafla_map = dict(zip(kafla_names, kafla_df["Kafla Code"]))

selected_kafla_name = st.selectbox("Select Kafla", options=kafla_names)

if not selected_kafla_name or selected_kafla_name not in kafla_map:
    st.warning("⚠️ Please select a valid Kafla.")
    st.stop()

kafla_code = kafla_map[selected_kafla_name]
kafla_dir = DOCS_DIR / kafla_code
kafla_dir.mkdir(parents=True, exist_ok=True)

st.markdown("### 📂 Upload Required Documents")

# Upload fields
def save_upload(label, key, subfolder, allow_multiple=False):
    widget_key = f"{key}_{kafla_code}"
    files = st.file_uploader(label, key=widget_key, accept_multiple_files=allow_multiple)
    saved = []
    if files:
        save_path = kafla_dir / subfolder
        save_path.mkdir(parents=True, exist_ok=True)
        for file in files if allow_multiple else [files]:
            out_path = save_path / file.name
            with open(out_path, "wb") as f:
                f.write(file.read())
            saved.append(file.name)
        st.success(f"✅ Uploaded to {subfolder}: {', '.join(saved)}")
    return saved

submitted = {}
submitted['Salar CNIC'] = save_upload("🆔 Salar CNIC Copy", "salar_cnic", "salar_cnic")
submitted['Bus Fitness Certificate'] = save_upload("🚌 Bus Fitness Certificate", "fitness", "fitness")
submitted['Coordinate Document'] = save_upload("📍 Coordinate Document", "coord", "coordinate")
submitted['Vehicle Documents'] = save_upload("🚗 Vehicle Documents", "vehicle_docs", "vehicles", allow_multiple=True)
submitted['Other Documents'] = save_upload("📌 Other Documents (if any)", "other_docs", "others", allow_multiple=True)

# Document status table
st.markdown("### 🗂️ Submission Status")
status_records = []
all_kafla_codes = kafla_df["Kafla Code"].tolist()
for code in all_kafla_codes:
    name = kafla_df[kafla_df["Kafla Code"] == code].iloc[0]
    name_label = f"{name['Kafla Name']} ({name['Salar Name']})"
    group_dir = DOCS_DIR / code
    status = {
        "Kafla": name_label,
        "Salar CNIC": os.path.exists(group_dir / "salar_cnic"),
        "Fitness Cert": os.path.exists(group_dir / "fitness"),
        "Coordinate": os.path.exists(group_dir / "coordinate"),
        "Vehicles": os.path.exists(group_dir / "vehicles"),
        "Others": os.path.exists(group_dir / "others")
    }
    status_records.append(status)

status_df = pd.DataFrame(status_records)
status_df = status_df.replace({True: "✅", False: "❌"})
st.dataframe(status_df, use_container_width=True)

# ---------------- PDF COMBINE SECTION ----------------
st.markdown("### 📄 Generate Final PDF")
if st.button("🧾 Generate Combined PDF"):
    final_pdf_path = kafla_dir / f"{selected_kafla_name.replace(' ', '_')}.pdf"

    # First build main summary page
    base_pdf_path = kafla_dir / "base_summary.pdf"
    doc = SimpleDocTemplate(str(base_pdf_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title Page
    elements.append(Paragraph(f"ZAIREEN LIST 2025 (KHI-GWD)", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Group: {selected_kafla_name}", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Vehicle #: ___________________", styles['Normal']))
    elements.append(Paragraph("Date: _________________________", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Zaireen list table
    zaireen_path = BASE_DIR / "zaireen.csv"
    if zaireen_path.exists():
        zdf = pd.read_csv(zaireen_path)
        zdf = zdf[zdf['Kafla Code'] == kafla_code]
        if not zdf.empty:
            table_data = [["Name", "Passport #", "DOB", "Nationality"]]
            for _, row in zdf.iterrows():
                table_data.append([row['Full Name'], row['Passport Number'], row['Date of Birth'], row['Nationality']])
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))

    # Save main summary PDF
    doc.build(elements)

    # Merge all documents
    merger = PdfMerger()
    merger.append(str(base_pdf_path))

    # Order of document folders
    doc_order = ["salar_cnic", "fitness", "coordinate", "vehicles", "others"]
    for section in doc_order:
        section_dir = kafla_dir / section
        if section_dir.exists():
            for file in sorted(section_dir.iterdir()):
                if file.suffix.lower() == ".pdf":
                    merger.append(str(file))

    # Zaireen documents: passport, iran, iraq
    for _, row in zdf.iterrows():
        z_folder = BASE_DIR / "zaireen_docs" / row['ID']
        if z_folder.exists():
            for doc_type in ["passport", "iran", "iraq"]:
                d_path = z_folder / f"{doc_type}.pdf"
                if d_path.exists():
                    merger.append(str(d_path))

    # Write final merged PDF
    merger.write(str(final_pdf_path))
    merger.close()

    st.success("✅ PDF Combined and Ready")
    with open(final_pdf_path, "rb") as f:
        st.download_button(
            label="📅 Download Combined PDF",
            data=f,
            file_name=final_pdf_path.name,
            mime="application/pdf"
        )
