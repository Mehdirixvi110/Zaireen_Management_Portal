from streamlit_option_menu import option_menu
import streamlit as st
import base64

# Set background and custom theme
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

        /* Full screen width */
        .main .block-container {{
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }}

        /* Dark header text for light background */
        h1, h2, h3, h4, h5, h6 {{
            color: #111 !important;
        }}

        /* Buttons */
        .stButton>button {{
            background-color: #7c1c2c;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 8px 16px;
        }}

        /* Input fields */
        .stTextInput>div>input,
        .stSelectbox>div>div>div>input,
        .stNumberInput>div>input,
        .stDateInput>div>input {{
            background-color: #ffffffcc;
            border-radius: 6px;
            color: #111;
            font-weight: bold;
        }}

        /* Labels */
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

# Apply background and theme
set_bg_from_local("Background.jpg")

# Title and logo header
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <h2 style="margin-bottom: 0; color: #111;">Zaireen Management Portal - 2025<br><small>(By Moakab E Zainabiya)</small></h2>
    <img src="data:image/jpg;base64,""" + base64.b64encode(open("Logo.jpg", "rb").read()).decode() + """" width="120" style="margin-right: 20px;"/>
</div>
""", unsafe_allow_html=True)

# Option Menu Navigation
selected = option_menu(
    menu_title=None,
    options=["Kafla Registration", "Zaireen Entry", "Convoy Documents", "Admin Panel", "Dashboard"],
    icons=["people-fill", "person-lines-fill", "file-earmark-arrow-up", "tools", "bar-chart-fill"],
    menu_icon="list",
    default_index=0,
    orientation="horizontal"
)

if selected == "Kafla Registration":
    with open("kafla_registration.py", encoding="utf-8") as f:
        exec(f.read())

elif selected == "Zaireen Entry":
    with open("zaireen_entry.py", encoding="utf-8") as f:
        exec(f.read())

elif selected == "Convoy Documents":
    with open("convay_document.py", encoding="utf-8") as f:
        exec(f.read())

elif selected == "Admin Panel":
    with open("admin.py", encoding="utf-8") as f:
        exec(f.read())

elif selected == "Dashboard":
    with open("dashboard.py", encoding="utf-8") as f:
        exec(f.read())
