import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from pathlib import Path
from PIL import Image
import shutil

# Prevent page config from being called again if this is imported
#if __name__ == "__main__":
    #st.set_page_config(page_title="Kafla Registration", layout="centered")

st.title("🕌 Kafla Registration Form | قافلہ رجسٹریشن")

st.markdown("""
    <style>
    /* Darken the label text */
    label {
        color: #000000 !important;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Define storage path
DATA_DIR = Path("docs")
DATA_DIR.mkdir(exist_ok=True)
CSV_FILE = Path("kafla.csv")

# Load or initialize DataFrame
if CSV_FILE.exists():
    df = pd.read_csv(CSV_FILE)
    if "Created At" not in df.columns:
        df["Created At"] = ""
else:
    df = pd.DataFrame(columns=[
        "Kafla Code", "Kafla Name", "City", "Province", "Country",
        "Salar Name", "Salar CNIC", "Salar Contact", "Created At"
    ])

st.markdown("---")
st.markdown("### 📝 Enter Kafla Details")

# Form to encapsulate all inputs
with st.form("kafla_form", clear_on_submit=True):
    kafla_code = str(uuid.uuid4())[:8]
    st.text_input("Kafla Code | قافلہ کوڈ", value=kafla_code, disabled=True, key="code_display")
    kafla_name = st.text_input("Kafla Name | قافلہ کا نام", placeholder="e.g. Moakab e Zainabiya")
    city = st.text_input("City | شہر", placeholder="e.g. Karachi")
    province = st.text_input("Province | صوبہ", placeholder="e.g. Sindh")
    country = st.text_input("Country | ملک", placeholder="e.g. Pakistan")
    salar_name = st.text_input("Salar Name | سالار کا نام", placeholder="e.g. Syed Ali Raza")
    salar_cnic = st.text_input("Salar CNIC (13 digits) | سالار کا شناختی کارڈ نمبر", max_chars=13, placeholder="e.g. 4210112345678")
    salar_contact = st.text_input("Salar Contact | سالار سے رابطہ", max_chars=11, placeholder="e.g. 03001234567")

    # File upload sections
    with st.expander("📁 Registration Documents | رجسٹریشن کے دستاویزات"):
        reg_files = st.file_uploader("Upload files", accept_multiple_files=True, type=["jpg", "jpeg", "png", "pdf"], key="reg")

    with st.expander("🚌 Vehicle Documents | گاڑی کے کاغذات"):
        vehicle_files = st.file_uploader("Upload vehicle documents", accept_multiple_files=True, type=["jpg", "jpeg", "png", "pdf"], key="vehicle")

    with st.expander("📄 Other Documents | دیگر دستاویزات"):
        other_files = st.file_uploader("Upload any other docs", accept_multiple_files=True, type=["jpg", "jpeg", "png", "pdf"], key="others")

    col1, col2 = st.columns([1, 1])
    with col1:
        submitted = st.form_submit_button("💾 Save Kafla")
    with col2:
        reset = st.form_submit_button("🔄 Reset Form")

# Handle form submission
if submitted:
    if not all([kafla_name, city, province, country, salar_name, salar_cnic, salar_contact]):
        st.error("❌ Please fill all required fields")
    elif not salar_cnic.isdigit() or len(salar_cnic) != 13 or not salar_contact.isdigit() or len(salar_contact) != 11:
        st.error("❌ Please check CNIC and Contact format")
    elif any(char.isdigit() for char in salar_name):
        st.warning("⚠️ Salar name should not contain numbers")
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = {
            "Kafla Code": kafla_code,
            "Kafla Name": kafla_name,
            "City": city,
            "Province": province,
            "Country": country,
            "Salar Name": salar_name,
            "Salar CNIC": salar_cnic,
            "Salar Contact": salar_contact,
            "Created At": now
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        kafla_dir = DATA_DIR / kafla_code
        (kafla_dir / "registration").mkdir(parents=True, exist_ok=True)
        (kafla_dir / "vehicle").mkdir(parents=True, exist_ok=True)
        (kafla_dir / "others").mkdir(parents=True, exist_ok=True)
        (kafla_dir / "zaireen").mkdir(parents=True, exist_ok=True)

        def save_files(file_list, subfolder):
            for file in file_list:
                file_path = kafla_dir / subfolder / file.name
                with open(file_path, "wb") as f:
                    f.write(file.read())

        save_files(reg_files, "registration")
        save_files(vehicle_files, "vehicle")
        save_files(other_files, "others")

        st.success("✅ Kafla registered successfully!")
        st.rerun()

# Display registered kaflas
if not df.empty:
    st.markdown("### 📋 Registered Kaflas")

    if "Created At" not in df.columns:
        df["Created At"] = ""

    sorted_df = df.copy()
    try:
        sorted_df = df.sort_values("Created At", ascending=False)
    except Exception:
        pass

    for index, row in sorted_df.iterrows():
        cols = st.columns([5, 1])
        with cols[0]:
            st.markdown(f"""
            **Code:** {row['Kafla Code']}  
            **Name:** {row['Kafla Name']}  
            **Salar:** {row['Salar Name']} | CNIC: {row['Salar CNIC']}  
            **City/Province/Country:** {row['City']}, {row['Province']}, {row['Country']}  
            **Contact:** {row['Salar Contact']}  
            **Created:** {row.get('Created At', '')}
            """)
        with cols[1]:
            if st.button("🗑️ Delete", key=f"delete_{row['Kafla Code']}"):
                df = df[df["Kafla Code"] != row["Kafla Code"]]
                df.to_csv(CSV_FILE, index=False)
                folder_to_remove = DATA_DIR / row["Kafla Code"]
                if folder_to_remove.exists():
                    shutil.rmtree(folder_to_remove)
                st.success(f"🗑️ Kafla '{row['Kafla Name']}' deleted.")
                st.rerun()

    st.dataframe(sorted_df, use_container_width=True)
