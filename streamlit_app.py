# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="MycoSense Dashboard", layout="wide", initial_sidebar_state="expanded")

# -------------------------
# DARK MODE CSS (forced)
# -------------------------
dark_css = """
<style>
.stApp { background: #1e1e1e; color: #f5f5f5 !important; }
.header { background: linear-gradient(90deg,#006400, #228B22); padding: 18px; border-radius: 10px;
          color: white; font-weight: 700; box-shadow: 0 6px 18px rgba(0,0,0,0.5); }
.card { background: #2c2c2c; color: #f5f5f5; padding: 14px; border-radius: 8px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.5); margin-bottom: 12px; }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# -------------------------
# Login handling
# -------------------------
def safe_rerun():
    try: st.experimental_rerun()
    except: st.session_state._rerun_fallback = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="header"><h2>🌱 MycoSense</h2><div style="font-size:14px">Soil Safety Dashboard</div></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔑 Login to MycoSense")
        st.write("Please sign in with your username and password to continue.")

        if "login_user" not in st.session_state: st.session_state.login_user = ""
        if "login_pass" not in st.session_state: st.session_state.login_pass = ""

        username_input = st.text_input("Username", value=st.session_state.login_user)
        password_input = st.text_input("Password", type="password", value=st.session_state.login_pass)

        st.session_state.login_user = username_input
        st.session_state.login_pass = password_input

        valid_username = "Joko"
        valid_password = "mycosense123"

        if st.button("Login"):
            if username_input.strip() == valid_username and password_input == valid_password:
                st.session_state.logged_in = True
                st.session_state.username = valid_username
                st.success("Login successful ✅")
                safe_rerun()
            else:
                st.error("Invalid username or password ❌")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # -------------------------
    # AFTER LOGIN: DASHBOARD
    # -------------------------
    st.markdown('<div class="header"><h2>🌱 MycoSense: Soil Safety Dashboard</h2></div>', unsafe_allow_html=True)

    # Sidebar Profile + Logout
    st.sidebar.header("👤 Farmer Profile")
    profile = {"username":"Joko","farm_id":"FieldA","farm_location":"Bandung","farm_size":2.5,"crop_type":"Rice","notes":"Soil often gets water from nearby river."}
    st.sidebar.write(f"👤 {profile['username']} | 🌾 {profile['farm_id']} | 📍 {profile['farm_location']}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        safe_rerun()

    page = st.sidebar.radio("📌 Navigate", ["Home", "Heatmap", "Analytics", "Insights", "Profile Summary"])

    uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type="csv", key="uploader")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        np.random.seed(42)
        df = pd.DataFrame({
            "x": np.random.randint(0, 50, 120),
            "y": np.random.randint(0, 50, 120),
            "voltage": np.round(np.random.uniform(0.1, 0.95, 120), 3),
            "pollutant": np.random.choice(["Lead","Copper","Nickel","PFAS","None"], 120)
        })

    # Pages
    if page == "Home":
        st.subheader(f"👋 Welcome {profile['username']}")
        st.markdown(f"Managing **{profile['farm_id']}** in *{profile['farm_location']}*")

    elif page == "Heatmap":
        st.subheader("🗺️ Soil Contamination Heatmap")
        fig = px.density_heatmap(df, x="x", y="y", z="voltage", histfunc="avg", color_continuous_scale="RdYlGn_r")
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Analytics":
        st.subheader("📊 Pollutant Distribution")
        st.bar_chart(df['pollutant'].value_counts())

        st.subheader("📈 Voltage Trend")
        df2 = df.reset_index().rename(columns={"index": "sample_idx"})
        line = px.line(df2, x="sample_idx", y="voltage", title="Voltage over samples")
        st.plotly_chart(line, use_container_width=True)

        st.subheader("🔮 Voltage Trend Prediction")
        x = np.arange(len(df2))
        y = df2['voltage'].values
        coeffs = np.polyfit(x, y, 1)
        trendline = np.poly1d(coeffs)
        df2['predicted'] = trendline(x)
        pred_line = px.line(df2, x="sample_idx", y=["voltage","predicted"],
                            labels={"value":"Voltage","sample_idx":"Sample Index"},
                            title="Observed vs Predicted Trend")
        st.plotly_chart(pred_line, use_container_width=True)

    elif page == "Insights":
        st.subheader("✅ Insights")
        avg_voltage = df['voltage'].mean()
        if avg_voltage < 0.4: st.success("Safe soil ✅")
        elif avg_voltage < 0.7: st.warning("Moderate risk ⚠️")
        else: st.error("High contamination ❌")

    elif page == "Profile Summary":
        st.subheader("📌 Profile Summary")
        st.json(profile)
