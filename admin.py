import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

# Page Config
st.set_page_config(page_title="🛠️ Admin Panel | ایڈمن پینل", layout="wide")
st.title("🛠️ Zaireen Admin Panel | زائرین کا ایڈمن پینل")

# Load data
base_path = Path("docs")
kafla_file = Path("kafla.csv")
zaireen_file = base_path / "zaireen.csv"

if not kafla_file.exists() or not zaireen_file.exists():
    st.warning("⚠️ Required data not found. Make sure Kafla and Zaireen data is available.")
    st.stop()

kafla_df = pd.read_csv(kafla_file)
zaireen_df = pd.read_csv(zaireen_file)

# Generate dropdown label
kafla_df['Label'] = kafla_df.apply(lambda row: f"{row['Kafla Name']} ({row['Salar Name']}) - {row['Kafla Code']}", axis=1)
kafla_map = dict(zip(kafla_df['Label'], kafla_df['Kafla Code']))

selected_label = st.selectbox("🔍 Select Kafla | قافلہ منتخب کریں", list(kafla_map.keys()))
selected_kafla_code = kafla_map[selected_label]
kafla_info = kafla_df[kafla_df['Kafla Code'] == selected_kafla_code].iloc[0]

st.markdown("### 🏷️ Kafla Information | قافلہ کی معلومات")

kafla_name = st.text_input("Kafla Name", kafla_info['Kafla Name'], key="edit_kafla_name")
salar_name = st.text_input("Salar Name", kafla_info['Salar Name'], key="edit_salar_name")
city = st.text_input("City", kafla_info['City'], key="edit_city")
province = st.text_input("Province", kafla_info['Province'], key="edit_province")
contact_value = st.text_input("Contact", kafla_info.get('Contact', ''), key="edit_contact")

if st.button("💾 Save Kafla Info"):
    kafla_df.loc[kafla_df['Kafla Code'] == selected_kafla_code, 'Kafla Name'] = kafla_name
    kafla_df.loc[kafla_df['Kafla Code'] == selected_kafla_code, 'Salar Name'] = salar_name
    kafla_df.loc[kafla_df['Kafla Code'] == selected_kafla_code, 'City'] = city
    kafla_df.loc[kafla_df['Kafla Code'] == selected_kafla_code, 'Province'] = province
    kafla_df.loc[kafla_df['Kafla Code'] == selected_kafla_code, 'Contact'] = contact_value
    kafla_df.to_csv(kafla_file, index=False)
    st.success("✅ Kafla info updated successfully!")

# Filter Zaireen of selected Kafla
filtered_df = zaireen_df[zaireen_df['Kafla Code'] == selected_kafla_code].reset_index(drop=True)

st.markdown("### 👥 Zaireen Entries | زائرین کی فہرست")

# Editable Table
if filtered_df.empty:
    st.info("ℹ️ No Zaireen found for selected Kafla.")
else:
    for i, row in filtered_df.iterrows():
        st.markdown("---")
        cols = st.columns([2, 2, 2, 2, 1, 1])
        full_name = cols[0].text_input("Full Name", row['Full Name'], key=f"name_{i}")
        passport = cols[1].text_input("Passport Number", row['Passport Number'], key=f"passport_{i}", disabled=True)
        contact = cols[2].text_input("Contact", row.get('Contact', ''), key=f"contact_{i}")
        nationality = cols[3].text_input("Nationality", row['Nationality'], key=f"nationality_{i}")

        # Show attachments (passport, iran, iraq visa)
        docs_path = base_path / selected_kafla_code / "zaireen" / passport
        doc_cols = st.columns(3)
        for idx, doc_type in enumerate(['passport', 'iran_visa', 'iraq_visa']):
            file = docs_path / f"{doc_type}.jpg"
            if file.exists():
                doc_cols[idx].image(Image.open(file), caption=file.name, width=100)
            else:
                doc_cols[idx].markdown(f"*{doc_type.replace('_', ' ').title()}: N/A*")

        col_action = st.columns([1, 1])
        if col_action[0].button("💾 Save", key=f"save_{i}"):
            zaireen_df.loc[(zaireen_df['Passport Number'] == row['Passport Number']), 'Full Name'] = full_name
            zaireen_df.loc[(zaireen_df['Passport Number'] == row['Passport Number']), 'Contact'] = contact
            zaireen_df.loc[(zaireen_df['Passport Number'] == row['Passport Number']), 'Nationality'] = nationality
            zaireen_df.to_csv(zaireen_file, index=False)
            st.success(f"✅ Updated: {full_name}")
            st.session_state["_refresh"] = True

        if col_action[1].button("🗑️ Delete", key=f"delete_{i}"):
            zaireen_df = zaireen_df[zaireen_df['Passport Number'] != row['Passport Number']]
            zaireen_df.to_csv(zaireen_file, index=False)
            st.warning(f"❌ Deleted: {full_name}")
            st.session_state["_refresh"] = True

# Optional refresh workaround
if st.session_state.get("_refresh"):
    st.session_state.pop("_refresh")
    st.experimental_set_query_params(refreshed=1)
    st.experimental_rerun()

st.markdown("---")
st.markdown("Made with ❤️ for Moakab e Zainabiya")
