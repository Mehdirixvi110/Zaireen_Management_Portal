import streamlit as st
from streamlit_option_menu import option_menu
import base64
import os
import importlib.util


# ✅ Set Streamlit page configuration (must be at top level)
st.set_page_config(
    page_title="Zaireen Management Portal - Moakab E Zainabiya",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Set background image from file
def set_bg_from_local(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }}

        .main .block-container {{
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #111 !important;
        }}

        .stButton>button {{
            background-color: #7c1c2c;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 8px 16px;
        }}

        .stTextInput>div>input,
        .stSelectbox>div>div>div>input,
        .stNumberInput>div>input,
        .stDateInput>div>input {{
            background-color: #ffffffcc;
            border-radius: 6px;
            color: #111;
            font-weight: bold;
        }}

        label {{
            color: #111;
            font-weight: 700;
            font-size: 16px;
        }}

        .stDataFrame, .css-1lcbmhc {{
            background-color: #ffffffcc;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Apply theme
set_bg_from_local("Background.jpg")

# ✅ Header with logo
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <h1 style="margin-bottom: 0; color: #111;">Zaireen Management Portal - 2025</h1>
    <img src="data:image/jpg;base64,{base64.b64encode(open("Logo.jpg", "rb").read()).decode()}" width="120" style="margin-right: 20px;"/>
</div>
""", unsafe_allow_html=True)

# ✅ Horizontal navigation menu
selected = option_menu(
    menu_title=None,
    options=["Kafla Registration", "Zaireen Entry", "Convoy Documents", "Admin Panel", "Dashboard"],
    icons=["people-fill", "person-lines-fill", "file-earmark-arrow-up", "tools", "bar-chart-fill"],
    menu_icon="list",
    default_index=0,
    orientation="horizontal"
)

# ✅ Define map of options to filenames
page_modules = {
    "Kafla Registration": "kafla_registration.py",
    "Zaireen Entry": "zaireen_entry.py",
    "Convoy Documents": "convay_document.py",
    "Admin Panel": "admin.py",
    "Dashboard": "dashboard.py"
}

# ✅ Load selected page dynamically and safely
selected_file = page_modules.get(selected)

if selected_file:
    file_path = os.path.join(os.getcwd(), selected_file)
    if os.path.exists(file_path):
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("module.name", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            st.error(f"❌ Failed to load `{selected_file}`.")
            st.exception(e)
    else:
        st.warning(f"⚠️ File not found: {selected_file}")
