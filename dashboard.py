import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# Page Config
#st.set_page_config(page_title="📊 Dashboard | زائرین کی رپورٹ", layout="wide")
st.title("📊 Zaireen Management Dashboard | زائرین کا انتظامی ڈیش بورڈ")

# Load data
base_path = Path("docs")
kafla_file = Path("kafla.csv")
zaireen_file = base_path / "zaireen.csv"

if not kafla_file.exists() or not zaireen_file.exists():
    st.warning("⚠️ Required data not found. Make sure Kafla and Zaireen data is available.")
    st.stop()

kafla_df = pd.read_csv(kafla_file)
zaireen_df = pd.read_csv(zaireen_file)

# Ensure required columns
if "Contact" not in kafla_df.columns:
    kafla_df["Contact"] = ""
if "Contact" not in zaireen_df.columns:
    zaireen_df["Contact"] = ""
if "Sex" not in zaireen_df.columns:
    zaireen_df["Sex"] = "Unknown"

# Merge both for aggregate analysis
merged_df = zaireen_df.merge(kafla_df, on="Kafla Code", how="left")

# Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("🧍‍🤝‍🧍 Total Zaireen | زائرین", f"{len(zaireen_df):,}")
col2.metric("🚌 Total Kaflas | قافلے", f"{len(kafla_df):,}")
col3.metric("🏛️ Cities Covered | شہروں کی تعداد", merged_df['City'].nunique())
col4.metric("📞 Unique Contacts", merged_df['Contact'].nunique())

st.markdown("---")

# Charts Section
st.markdown("### 📈 Visual Insights | بصری جائزہ")

# 1. Zaireen per Kafla
kafla_counts = merged_df['Kafla Name'].value_counts().reset_index()
kafla_counts.columns = ['Kafla', 'Total Zaireen']
kafla_chart = px.bar(
    kafla_counts,
    x='Kafla',
    y='Total Zaireen',
    title='🥮 Zaireen per Kafla | فی قافلہ زائرین',
    template='plotly_dark',
    color_discrete_sequence=['#FFD700']
)
st.plotly_chart(kafla_chart, use_container_width=True)

# 2. Gender Split
if 'Sex' in merged_df.columns:
    gender_chart = px.pie(
        merged_df,
        names='Sex',
        title='♅ Gender Split | صنفی تناسب',
        template='plotly_dark',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(gender_chart, use_container_width=True)

# 3. City-wise Distribution
city_counts = merged_df['City'].value_counts().reset_index()
city_counts.columns = ['City', 'Total Zaireen']
city_chart = px.bar(
    city_counts,
    x='City',
    y='Total Zaireen',
    title='🏛️ City-wise Distribution | شہروں کے لحاظ سے تقسیم',
    template='plotly_dark',
    color_discrete_sequence=['#00BFFF']
)
st.plotly_chart(city_chart, use_container_width=True)

# 4. Kafla vs Province
if 'Province' in merged_df.columns:
    prov_chart = px.histogram(
        merged_df,
        x='Province',
        color='Kafla Name',
        title='🗺️ Kafla by Province | صوبہ وار قافلے',
        template='plotly_dark',
        barmode='group'
    )
    st.plotly_chart(prov_chart, use_container_width=True)

st.markdown("---")

# Export Reports Section
st.markdown("### 📤 Export Reports | رپورٹس ایکسپورٹ کریں")

# Excel export
def generate_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        kafla_df.to_excel(writer, index=False, sheet_name='Kafla')
        zaireen_df.to_excel(writer, index=False, sheet_name='Zaireen')
        merged_df.to_excel(writer, index=False, sheet_name='Merged')
    output.seek(0)
    return output

# PDF export
def generate_pdf():
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("📊 Zaireen Report | زائرین کی رپورٹ", styles['Title']), Spacer(1, 12)]

    # Limit to a subset of fields to avoid PDF overflow
    display_cols = ['Zaireen Name', 'Passport Number', 'Nationality', 'Sex', 'City', 'Province', 'Kafla Name']
    data = [display_cols] + merged_df[display_cols].fillna("").values.tolist()

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey)
    ]))
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output

# Download buttons
excel_file = generate_excel()
pdf_file = generate_pdf()

st.download_button(
    label="📥 Download Excel Report",
    data=excel_file,
    file_name="Zaireen_Dashboard_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_file,
    file_name="Zaireen_Dashboard_Report.pdf",
    mime="application/pdf"
)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for Moakab e Zainabiya")
