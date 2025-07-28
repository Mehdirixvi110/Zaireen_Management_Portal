import streamlit as st
import base64

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
            font-family: 'Segoe UI', sans-serif;
        }}

        /* Header Styling */
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff !important;
        }}
        h1 {{ font-size: 40px !important; }}
        h2 {{ font-size: 32px !important; }}
        h3 {{ font-size: 26px !important; }}
        h4 {{ font-size: 22px !important; }}
        h5 {{ font-size: 18px !important; }}
        h6 {{ font-size: 16px !important; }}

        /* Button Styling */
        .stButton>button {{
            background-color: #7c1c2c;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 8px 16px;
        }}

        /* Text Inputs */
        .stTextInput>div>input {{
            background-color: #ffffffaa;
            border-radius: 6px;
            color: black;
            font-weight: 500;
        }}

        /* File Uploader */
        .stFileUploader {{
            background-color: #ffffffdd;
            border-radius: 8px;
            padding: 10px;
        }}

        /* DataFrame table style override */
        .stDataFrame, .css-1lcbmhc {{
            background-color: #ffffffcc;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
