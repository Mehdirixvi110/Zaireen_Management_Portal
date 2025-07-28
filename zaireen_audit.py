import streamlit as st
import pandas as pd
import os
from pathlib import Path
from PIL import Image

# Setup
st.set_page_config(page_title="Zaireen Document Audit", layout="wide")
st.title("🧾 Zaireen Document Audit & Review")

# Paths
BASE_DIR = Path("docs")
ZAIREEN_CSV = BASE_DIR / "zaireen.csv"
KAFLA_CSV = Path("kafla.csv")
UPLOAD_DIR = BASE_DIR / "zaireen_docs"

if not KAFLA_CSV.exists() or not ZAIREEN_CSV.exists():
    st.error("❗ Kafla or Zaireen data missing. Please enter data first.")
    st.stop()

# Load data
kafla_df = pd.read_csv(KAFLA_CSV)
kafla_names = kafla_df.apply(lambda row: f"{row['Kafla Name']} ({row['Salar Name']})", axis=1).tolist()
kafla_map = dict(zip(kafla_names, kafla_df['Kafla Code']))

selected_kafla = st.selectbox("Select Kafla", kafla_names)
kafla_code = kafla_map[selected_kafla]

zdf = pd.read_csv(ZAIREEN_CSV)
zdf = zdf[zdf['Kafla Code'] == kafla_code]

if zdf.empty:
    st.info("No Zaireen found for this Kafla.")
    st.stop()

st.markdown("### 📋 Document Status Table")

summary = {"Total": len(zdf), "Complete": 0, "Incomplete": 0}

data_rows = []
for index, row in zdf.iterrows():
    pnum = row['Passport Number']
    zaireen_dir = UPLOAD_DIR / kafla_code / pnum
    passport_file = zaireen_dir / f"{pnum}_passport.jpg"
    iran_file = zaireen_dir / f"{pnum}_iran.jpg"
    iraq_file = zaireen_dir / f"{pnum}_iraq.jpg"

    p_ok = passport_file.exists()
    i_ok = iran_file.exists()
    q_ok = iraq_file.exists()

    complete = all([p_ok, i_ok, q_ok])
    summary["Complete" if complete else "Incomplete"] += 1

    data_rows.append({
        "Name": row['Full Name'],
        "Passport #": pnum,
        "Passport Scan": "✅" if p_ok else "❌",
        "Iran Visa": "✅" if i_ok else "❌",
        "Iraq Visa": "✅" if q_ok else "❌",
    })

summary_df = pd.DataFrame(data_rows)
st.dataframe(summary_df, use_container_width=True)

# Summary
st.markdown("### 📊 Summary")
st.metric("Total Zaireen", summary['Total'])
st.metric("Complete Records", summary['Complete'])
st.metric("Incomplete Records", summary['Incomplete'])

# Export Option
csv_out = summary_df.to_csv(index=False)
st.download_button("📥 Download Audit CSV", data=csv_out, file_name=f"audit_{kafla_code}.csv", mime="text/csv")
