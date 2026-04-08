import streamlit as st
import requests
import pandas as pd
import random
import time
import sqlite3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="VaultPay - Secure UPI Payments",
    page_icon="🔐",
    layout="wide"
)

BASE_URL = "https://vaultpay-backend-t4fp.onrender.com"
DB_PATH  = "fraud.db"

# ================================================================
#  7-POINT COLOR PALETTE
#  1. Deep Navy    #0A0F2C  (background)
#  2. Electric Blue #2563EB (primary)
#  3. Purple       #7C3AED  (accent)
#  4. Teal         #0D9488  (success/wallet)
#  5. White        #FFFFFF  (cards)
#  6. Light Gray   #F1F5F9  (page bg)
#  7. Gold         #F59E0B  (warning/highlight)
# ================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --navy:   #0A0F2C;
    --blue:   #2563EB;
    --purple: #7C3AED;
    --teal:   #0D9488;
    --white:  #FFFFFF;
    --gray:   #F1F5F9;
    --gold:   #F59E0B;
    --danger: #DC2626;
    --text:   #1E293B;
    --muted:  #64748B;
}

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }
.stApp { background-color: var(--gray) !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

.vp-nav {
    background: linear-gradient(135deg, var(--navy) 0%, #1E1B4B 100%);
    padding: 16px 28px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    box-shadow: 0 4px 24px rgba(10,15,44,0.18);
}
.vp-nav-logo { font-size: 24px; font-weight: 800; color: var(--white); letter-spacing: -0.5px; }
.vp-nav-logo span { color: var(--gold); }
.vp-nav-user { font-size: 13px; color: #A5B4FC; }

.card {
    background: var(--white);
    border-radius: 20px;
    padding: 28px;
    box-shadow: 0 2px 16px rgba(10,15,44,0.07);
    margin-bottom: 20px;
}
.card-blue {
    background: linear-gradient(135deg, var(--blue) 0%, var(--purple) 100%);
    border-radius: 20px; padding: 28px; color: white; margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(37,99,235,0.25);
}
.card-teal {
    background: linear-gradient(135deg, var(--teal) 0%, #059669 100%);
    border-radius: 20px; padding: 24px; color: white; margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(13,148,136,0.22);
}
.balance-label  { font-size: 13px; opacity: 0.85; font-weight: 500; margin: 0 0 6px 0; }
.balance-amount { font-size: 38px; font-weight: 800; margin: 0; letter-spacing: -1px; }
.balance-sub    { font-size: 12px; opacity: 0.7; margin: 6px 0 0 0; }

.action-item {
    background: var(--white);
    border-radius: 16px; padding: 20px 10px; text-align: center;
    box-shadow: 0 2px 10px rgba(10,15,44,0.06);
    border: 1.5px solid #E2E8F0;
}
.action-icon  { font-size: 30px; margin-bottom: 8px; }
.action-label { font-size: 12px; font-weight: 600; color: var(--text); }

.sec-title {
    font-size: 18px; font-weight: 700; color: var(--navy);
    margin: 24px 0 14px 0; letter-spacing: -0.3px;
}

.contact-card {
    background: var(--white); border: 1.5px solid #E2E8F0;
    border-radius: 16px; padding: 18px 10px; text-align: center;
    box-shadow: 0 1px 6px rgba(10,15,44,0.05); margin-bottom: 4px; min-height: 110px;
}
.avatar {
    width: 52px; height: 52px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700; color: white; margin: 0 auto 10px auto;
}
.contact-name { font-size: 12px; font-weight: 600; color: var(--text); margin-bottom: 2px; }
.contact-id   { font-size: 10px; color: var(--muted); }

.risk-safe    { background:#F0FDF4; border:2px solid #22C55E; border-radius:14px; padding:18px; margin-bottom:14px; }
.risk-warning { background:#FFFBEB; border:2px solid var(--gold); border-radius:14px; padding:18px; margin-bottom:14px; }
.risk-blocked { background:#FFF1F2; border:2px solid var(--danger); border-radius:14px; padding:18px; margin-bottom:14px; }
.risk-score-safe    { color:#15803D; font-size:22px; font-weight:800; }
.risk-score-warning { color:#B45309; font-size:22px; font-weight:800; }
.risk-score-blocked { color:var(--danger); font-size:22px; font-weight:800; }

.txn-row {
    background: var(--white); border-radius: 14px; padding: 16px 20px;
    margin-bottom: 10px; border: 1px solid #E2E8F0;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 1px 4px rgba(10,15,44,0.04);
}
.txn-name   { font-weight: 600; font-size: 14px; color: var(--text); }
.txn-time   { font-size: 11px; color: var(--muted); margin-top: 2px; }
.txn-amount { font-weight: 800; font-size: 16px; color: var(--navy); }

.pill-safe    { background:#DCFCE7; color:#15803D; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }
.pill-warning { background:#FEF3C7; color:#B45309; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }
.pill-blocked { background:#FFE4E6; color:#BE123C; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }
.pill-success { background:#DCFCE7; color:#15803D; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }

.auth-title { text-align: center; margin-bottom: 32px; }
.auth-title h1 { font-size: 36px; font-weight: 800; color: var(--navy); margin: 0; letter-spacing: -1px; }
.auth-title h1 span { color: var(--blue); }
.auth-title p { color: var(--muted); margin-top: 6px; font-size: 14px; }

.input-label { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; margin-top: 12px; }

.qr-wrap { background: var(--white); border-radius: 20px; padding: 32px; text-align: center; box-shadow: 0 4px 24px rgba(10,15,44,0.1); }
.qr-box  { width:160px; height:160px; background:var(--navy); margin:0 auto 16px auto; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:80px; }
.scan-box { background: var(--navy); border-radius: 20px; padding: 40px; text-align: center; color: white; margin: 20px 0; }

.rec-box   { background:linear-gradient(135deg,#EFF6FF 0%,#F5F3FF 100%); border:1.5px solid #BFDBFE; border-radius:14px; padding:16px; }
.rec-title { font-size:13px; font-weight:700; color:var(--blue); margin-bottom:8px; }
.rec-item  { font-size:12px; color:var(--text); margin-bottom:4px; }

.stButton > button { border-radius:12px !important; font-weight:600 !important; font-size:14px !important; padding:10px 18px !important; }
div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label { font-size:13px !important; font-weight:600 !important; color:var(--text) !important; }
.stTextInput input, .stNumberInput input { border-radius:10px !important; border:1.5px solid #CBD5E1 !important; font-size:15px !important; padding:10px 14px !important; }
.stTextInput input:focus, .stNumberInput input:focus { border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(37,99,235,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ================================================================
#  SESSION STATE
# ================================================================
defaults = {
    "logged_in": False, "user": None, "page": "auth", "auth_tab": "login",
    "selected_receiver": None, "entered_amount": 0,
    "risk_result": None, "payment_result": None, "scan_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
#  HELPERS
# ================================================================
COLORS = ["#2563EB","#7C3AED","#0D9488","#DC2626","#F59E0B","#059669","#9333EA","#0891B2"]

def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

def get_color(name):
    return COLORS[sum(ord(c) for c in name) % len(COLORS)]

def nav(page):
    st.session_state.page = page
    st.rerun()

def get_user_name(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else user_id
    except:
        return user_id

def add_balance_to_db(user_id, bank_add, wallet_add):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if bank_add > 0:
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bank_add, user_id))
        if wallet_add > 0:
            c.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id = ?", (wallet_add, user_id))
        conn.commit()
        c.execute("SELECT balance, wallet_balance FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row
    except:
        return None

def nav_bar(title=""):
    user = st.session_state.user or {}
    name = user.get("name", "User").title()
    st.markdown(f"""
    <div class="vp-nav">
        <div class="vp-nav-logo">Vault<span>Pay</span></div>
        <div class="vp-nav-user">👤 {name} &nbsp;|&nbsp; {title}</div>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
#  AUTH
# ================================================================
def show_auth():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div class="auth-title">
            <h1>Vault<span>Pay</span></h1>
            <p>India's Smartest Fraud-Protected Payment System</p>
        </div>
        """, unsafe_allow_html=True)

        tab = st.session_state.auth_tab
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔑  Login", use_container_width=True,
                         type="primary" if tab == "login" else "secondary"):
                st.session_state.auth_tab = "login"; st.rerun()
        with c2:
            if st.button("📝  Register", use_container_width=True,
                         type="primary" if tab == "register" else "secondary"):
                st.session_state.auth_tab = "register"; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if tab == "login":
            st.markdown('<div class="input-label">📱 Mobile Number</div>', unsafe_allow_html=True)
            mobile = st.text_input("Mobile Number", placeholder="Enter your 10-digit mobile number", label_visibility="collapsed")
            st.markdown('<div class="input-label">🔒 MPIN</div>', unsafe_allow_html=True)
            mpin = st.text_input("MPIN", type="password", placeholder="Enter your 4-digit MPIN", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Login to VaultPay", type="primary", use_container_width=True):
                if not mobile or not mpin:
                    st.error("⚠️ Please enter both mobile number and MPIN")
                elif len(mobile) != 10 or not mobile.isdigit():
                    st.error("⚠️ Enter a valid 10-digit mobile number")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/login",
                                            json={"mobile_number": mobile, "mpin": mpin}, timeout=5)
                        if res.status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.user = res.json()
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error("❌ Invalid mobile number or MPIN")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server. Run: python app.py")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        else:
            st.markdown('<div class="input-label">👤 Full Name</div>', unsafe_allow_html=True)
            name = st.text_input("Full Name", placeholder="Enter your full name", label_visibility="collapsed")
            st.markdown('<div class="input-label">📱 Mobile Number</div>', unsafe_allow_html=True)
            mobile = st.text_input("Mobile Number", placeholder="Enter 10-digit mobile number", label_visibility="collapsed", key="reg_mob")
            st.markdown('<div class="input-label">🔑 Password</div>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="Create a strong password", label_visibility="collapsed")
            st.markdown('<div class="input-label">🔑 Confirm Password</div>', unsafe_allow_html=True)
            conf_pwd = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", label_visibility="collapsed")
            st.markdown('<div class="input-label">🔒 MPIN (4 digits)</div>', unsafe_allow_html=True)
            mpin = st.text_input("MPIN", type="password", placeholder="Create a 4-digit MPIN", label_visibility="collapsed", key="reg_mpin")
            st.markdown('<div class="input-label">🔒 Confirm MPIN</div>', unsafe_allow_html=True)
            conf_mpin = st.text_input("Confirm MPIN", type="password", placeholder="Re-enter your MPIN", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create VaultPay Account", type="primary", use_container_width=True):
                if not all([name, mobile, password, conf_pwd, mpin, conf_mpin]):
                    st.error("⚠️ Please fill in all fields")
                elif len(mobile) != 10 or not mobile.isdigit():
                    st.error("⚠️ Enter a valid 10-digit mobile number")
                elif password != conf_pwd:
                    st.error("⚠️ Passwords do not match")
                elif mpin != conf_mpin:
                    st.error("⚠️ MPINs do not match")
                elif len(mpin) != 4 or not mpin.isdigit():
                    st.error("⚠️ MPIN must be exactly 4 digits")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/register", json={
                            "name": name, "mobile_number": mobile,
                            "password": password, "mpin": mpin
                        }, timeout=30)
                        if res.status_code == 200:
                            st.success("✅ Account created! Please login with your mobile and MPIN.")
                            st.session_state.auth_tab = "login"
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {res.json().get('error','Registration failed')}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server. Run: python app.py")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ================================================================
#  DASHBOARD
# ================================================================
def show_dashboard():
    user    = st.session_state.user or {}
    name    = user.get("name", "User").title()
    balance = user.get("balance", 0)
    wallet  = user.get("wallet_balance", 0)
    acc_num = str(user.get("account_number", "0000000000"))
    masked  = "XXXX XXXX " + acc_num[-4:]

    nav_bar("Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card-blue">
            <p class="balance-label">🏦 Bank Account Balance</p>
            <p class="balance-amount">₹ {balance:,.2f}</p>
            <p class="balance-sub">Account: {masked}</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card-teal">
            <p class="balance-label">👛 Wallet Balance</p>
            <p class="balance-amount">₹ {wallet:,.2f}</p>
            <p class="balance-sub">VaultPay Wallet</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Quick Actions</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="action-item"><div class="action-icon">📷</div><div class="action-label">Scan & Pay</div></div>', unsafe_allow_html=True)
        if st.button("Scan & Pay", use_container_width=True, key="scan_btn"): nav("scan")
    with c2:
        st.markdown('<div class="action-item"><div class="action-icon">👥</div><div class="action-label">Pay to Contact</div></div>', unsafe_allow_html=True)
        if st.button("Pay to Contact", use_container_width=True, key="contact_btn"): nav("contacts")
    with c3:
        st.markdown('<div class="action-item"><div class="action-icon">💰</div><div class="action-label">Add Money</div></div>', unsafe_allow_html=True)
        if st.button("Add Money", use_container_width=True, key="add_btn"): nav("add_balance")
    with c4:
        st.markdown('<div class="action-item"><div class="action-icon">📋</div><div class="action-label">History</div></div>', unsafe_allow_html=True)
        if st.button("History", use_container_width=True, key="hist_btn"): nav("history")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="action-item"><div class="action-icon">💳</div><div class="action-label">Check Balance</div></div>', unsafe_allow_html=True)
        if st.button("Check Balance", use_container_width=True, key="bal_btn"): nav("balance")
    with c2:
        st.markdown('<div class="action-item"><div class="action-icon">📱</div><div class="action-label">My Profile & QR</div></div>', unsafe_allow_html=True)
        if st.button("My Profile & QR", use_container_width=True, key="qr_btn"): nav("profile")
    with c3:
        st.markdown('<div class="action-item"><div class="action-icon">🏠</div><div class="action-label">Mobile Recharge</div></div>', unsafe_allow_html=True)
        st.button("Mobile Recharge", use_container_width=True, key="mob_btn", disabled=True)
    with c4:
        st.markdown('<div class="action-item"><div class="action-icon">⚡</div><div class="action-label">Electricity Bill</div></div>', unsafe_allow_html=True)
        st.button("Electricity Bill", use_container_width=True, key="elec_btn", disabled=True)

    st.markdown('<div class="sec-title">Monthly Spending Overview</div>', unsafe_allow_html=True)
    chart_data = pd.DataFrame({
        "Month": ["Oct","Nov","Dec","Jan","Feb","Mar"],
        "Bank Spending (₹)":   [3200,4100,5800,2900,3700,4500],
        "Wallet Spending (₹)": [1200,1800,2100,900,1500,2000]
    })
    st.line_chart(chart_data.set_index("Month"), use_container_width=True, height=200)
    st.caption("📊 Sample monthly spending pattern")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ================================================================
#  PROFILE & QR
# ================================================================
def show_profile():
    nav_bar("My Profile")
    if st.button("← Back to Dashboard", key="back_profile"): nav("dashboard")

    user    = st.session_state.user or {}
    name    = user.get("name", "User").title()
    uid     = user.get("user_id", "VP0000")
    acc_num = str(user.get("account_number", "0000000000"))
    balance = user.get("balance", 0)
    wallet  = user.get("wallet_balance", 0)
    initials= get_initials(name)
    color   = get_color(name)
    upi_id  = f"{uid.lower()}@vaultpay"

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="qr-wrap">
            <div class="avatar" style="background:{color}; width:72px; height:72px; font-size:24px; margin:0 auto 12px auto;">{initials}</div>
            <h2 style="margin:0; font-size:22px; font-weight:800; color:#0A0F2C;">{name}</h2>
            <p style="color:#64748B; margin:4px 0 20px 0; font-size:13px;">VaultPay Member</p>
            <div class="qr-box">&#128379;</div>
            <div style="background:#F1F5F9; border-radius:12px; padding:14px; margin-top:16px;">
                <p style="margin:0; font-size:13px; color:#64748B;">Your UPI ID</p>
                <p style="margin:4px 0 0 0; font-size:18px; font-weight:700; color:#2563EB;">{upi_id}</p>
            </div>
            <div style="margin-top:14px; display:flex; gap:10px; justify-content:center;">
                <div style="background:#F1F5F9; border-radius:12px; padding:12px 20px; flex:1;">
                    <p style="margin:0; font-size:11px; color:#64748B;">Bank Balance</p>
                    <p style="margin:4px 0 0 0; font-size:16px; font-weight:700; color:#0A0F2C;">₹{balance:,.2f}</p>
                </div>
                <div style="background:#F1F5F9; border-radius:12px; padding:12px 20px; flex:1;">
                    <p style="margin:0; font-size:11px; color:#64748B;">Wallet</p>
                    <p style="margin:4px 0 0 0; font-size:16px; font-weight:700; color:#0D9488;">₹{wallet:,.2f}</p>
                </div>
            </div>
            <p style="margin-top:16px; font-size:11px; color:#94A3B8;">Share this QR code to receive money instantly</p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================
#  ADD BALANCE
# ================================================================
def show_add_balance():
    nav_bar("Add Money")
    if st.button("← Back to Dashboard", key="back_add"): nav("dashboard")

    user   = st.session_state.user or {}
    uid    = user.get("user_id")
    balance= user.get("balance", 0)
    wallet = user.get("wallet_balance", 0)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <div>
                    <p style="margin:0; font-size:12px; color:#64748B;">Current Bank Balance</p>
                    <p style="margin:4px 0 0 0; font-size:22px; font-weight:800; color:#2563EB;">₹{balance:,.2f}</p>
                </div>
                <div>
                    <p style="margin:0; font-size:12px; color:#64748B;">Current Wallet Balance</p>
                    <p style="margin:4px 0 0 0; font-size:22px; font-weight:800; color:#0D9488;">₹{wallet:,.2f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="input-label">🏦 Add to Bank Account (₹)</div>', unsafe_allow_html=True)
        st.caption("Enter amount to add to your bank account")
        bank_add = st.number_input("Bank Amount", min_value=0, max_value=100000, step=100, label_visibility="collapsed")

        st.markdown('<div class="input-label">👛 Add to Wallet (₹)</div>', unsafe_allow_html=True)
        st.caption("Enter amount to add to your VaultPay wallet")
        wallet_add = st.number_input("Wallet Amount", min_value=0, max_value=50000, step=100, label_visibility="collapsed", key="w_add")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Money Now", type="primary", use_container_width=True):
            if bank_add == 0 and wallet_add == 0:
                st.error("⚠️ Please enter an amount to add")
            else:
                result = add_balance_to_db(uid, bank_add, wallet_add)
                if result:
                    st.session_state.user["balance"] = result[0]
                    st.session_state.user["wallet_balance"] = result[1]
                    st.success(f"✅ Added! Bank: ₹{result[0]:,.2f} | Wallet: ₹{result[1]:,.2f}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to add money")

# ================================================================
#  SCAN & PAY
# ================================================================
def show_scan():
    nav_bar("Scan & Pay")
    if st.button("← Back to Dashboard", key="back_scan"):
        st.session_state.scan_done = False
        nav("dashboard")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.scan_done:
            st.markdown("""
            <div class="scan-box">
                <div style="font-size:80px; margin-bottom:16px;">📷</div>
                <h3 style="margin:0; font-size:20px; font-weight:700;">Point Camera at QR Code</h3>
                <p style="color:#A5B4FC; margin-top:8px; font-size:13px;">Simulated scanner — press button to scan</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Simulate QR Scan", type="primary", use_container_width=True):
                with st.spinner("Scanning QR Code..."):
                    time.sleep(2)
                try:
                    users = requests.get(f"{BASE_URL}/users").json()
                    if users:
                        st.session_state.selected_receiver = random.choice(users)
                except:
                    pass
                st.session_state.scan_done = True
                st.rerun()
        else:
            receiver = st.session_state.selected_receiver
            if receiver:
                initials = get_initials(receiver["name"])
                color    = get_color(receiver["name"])
                st.markdown(f"""
                <div style="background:white; border-radius:20px; padding:28px; text-align:center; box-shadow:0 4px 20px rgba(10,15,44,0.1);">
                    <div style="color:#15803D; font-size:40px; margin-bottom:8px;">✅</div>
                    <p style="color:#15803D; font-weight:700; font-size:14px; margin:0;">QR Code Scanned Successfully</p>
                    <div class="avatar" style="background:{color}; width:60px; height:60px; font-size:20px; margin:16px auto 10px auto;">{initials}</div>
                    <h3 style="margin:0; font-size:18px; font-weight:700; color:#0A0F2C;">{receiver['name']}</h3>
                    <p style="color:#64748B; font-size:13px;">{receiver['user_id']}@vaultpay</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Proceed to Pay", type="primary", use_container_width=True):
                    st.session_state.scan_done = False
                    nav("enter_amount")

# ================================================================
#  CONTACTS
# ================================================================
def show_contacts():
    nav_bar("Pay to Contact")
    if st.button("← Back to Dashboard", key="back_contacts"): nav("dashboard")

    st.markdown('<div class="input-label">🔍 Search Contact by Name</div>', unsafe_allow_html=True)
    st.caption("Type at least 2 characters to search from 2000+ contacts")
    search = st.text_input("Search", placeholder="e.g. Rahul, Priya, Sharma...", label_visibility="collapsed")

    try:
        users = requests.get(f"{BASE_URL}/users").json()
    except:
        st.error("❌ Cannot connect to server"); return

    if search and len(search) >= 2:
        filtered = [u for u in users if search.lower() in u["name"].lower()]
    elif search:
        st.info("Type at least 2 characters to search"); return
    else:
        filtered = users[:32]

    if not filtered:
        st.warning("No contacts found."); return

    st.markdown(f'<div class="sec-title">Contacts ({len(filtered)} shown)</div>', unsafe_allow_html=True)

    for i in range(0, len(filtered), 4):
        row = filtered[i:i+4]
        cols = st.columns(4)
        for j, u in enumerate(row):
            with cols[j]:
                initials = get_initials(u["name"])
                color    = get_color(u["name"])
                st.markdown(f"""
                <div class="contact-card">
                    <div class="avatar" style="background:{color};">{initials}</div>
                    <div class="contact-name">{u['name']}</div>
                    <div class="contact-id">{u['user_id']}@vaultpay</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Pay", key=f"pay_{u['user_id']}", use_container_width=True):
                    st.session_state.selected_receiver = u
                    nav("enter_amount")

# ================================================================
#  ENTER AMOUNT
# ================================================================
def show_enter_amount():
    nav_bar("Enter Amount")
    receiver = st.session_state.selected_receiver
    if not receiver: nav("contacts"); return

    if st.button("← Back to Contacts", key="back_amt"): nav("contacts")

    initials = get_initials(receiver["name"])
    color    = get_color(receiver["name"])

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <div class="avatar" style="background:{color}; width:68px; height:68px; font-size:22px; margin:0 auto 12px auto;">{initials}</div>
            <h3 style="margin:0; font-size:20px; font-weight:700; color:#0A0F2C;">{receiver['name']}</h3>
            <p style="color:#64748B; font-size:13px; margin:4px 0 0 0;">UPI ID: {receiver['user_id']}@vaultpay</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="input-label">💵 Enter Transfer Amount (₹)</div>', unsafe_allow_html=True)
        st.caption("Enter the amount you want to send. Minimum ₹1, Maximum ₹1,00,000")
        amount = st.number_input("Amount", min_value=1, max_value=100000, step=1, label_visibility="collapsed")

        user_balance = st.session_state.user.get("balance", 0)
        st.caption(f"💳 Available bank balance: ₹{user_balance:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Proceed to Payment →", type="primary", use_container_width=True):
            if amount <= 0:
                st.error("⚠️ Please enter a valid amount")
            elif amount > user_balance:
                st.error("❌ Insufficient bank balance")
            else:
                st.session_state.entered_amount = amount
                nav("payment")

# ================================================================
#  PAYMENT PAGE (SPLIT SCREEN)
# ================================================================
def show_payment():
    nav_bar("Confirm Payment")
    receiver = st.session_state.selected_receiver
    amount   = st.session_state.entered_amount
    user     = st.session_state.user or {}

    if not receiver or not amount: nav("contacts"); return
    if st.button("← Back", key="back_pay"): nav("enter_amount")

    initials = get_initials(receiver["name"])
    color    = get_color(receiver["name"])

    # Fetch risk
    risk_data = {}
    try:
        r = requests.post(f"{BASE_URL}/check-risk", json={
            "sender_id": user.get("user_id"), "amount": amount}, timeout=5)
        if r.status_code == 200:
            risk_data = r.json()
            st.session_state.risk_result = risk_data
    except:
        pass

    risk      = risk_data.get("risk", 0)
    status    = risk_data.get("status", "SAFE")
    breakdown = risk_data.get("breakdown", {})

    left, right = st.columns([1.1, 0.9])

    # ---- LEFT ----
    with left:
        st.markdown(f"""
        <div class="card" style="text-align:center; padding:24px;">
            <div class="avatar" style="background:{color}; width:60px; height:60px; font-size:20px; margin:0 auto 10px auto;">{initials}</div>
            <h3 style="margin:0; font-size:18px; font-weight:700; color:#0A0F2C;">Sending to {receiver['name']}</h3>
            <p style="color:#64748B; font-size:12px; margin:4px 0;">{receiver['user_id']}@vaultpay</p>
            <h2 style="font-size:34px; font-weight:800; color:#2563EB; margin:14px 0 0 0;">₹ {amount:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="input-label">💳 Select Payment Method</div>', unsafe_allow_html=True)
        st.caption("Choose how you want to pay for this transaction")
        pay_method = st.radio("Payment Method",
                              [f"🏦 Bank Account (₹{user.get('balance',0):,.2f} available)",
                               f"👛 Wallet (₹{user.get('wallet_balance',0):,.2f} available)"],
                              label_visibility="collapsed")

        st.markdown('<div class="input-label">🔒 Enter MPIN to Authorize Payment</div>', unsafe_allow_html=True)
        st.caption("Your secret 4-digit security PIN to confirm this transaction")
        mpin = st.text_input("MPIN", type="password", placeholder="Enter your 4-digit MPIN", label_visibility="collapsed")

        is_blocked = status == "BLOCKED"
        if is_blocked:
            st.markdown("""
            <div class="risk-blocked" style="margin-top:12px;">
                <div class="risk-score-blocked">🚫 Transaction Blocked</div>
                <p style="margin:6px 0 0 0; font-size:13px; color:#BE123C;">
                    High fraud risk detected. This transaction cannot be processed.
                </p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔐 Pay Now", type="primary", use_container_width=True):
                if not mpin:
                    st.error("⚠️ Please enter your MPIN")
                elif len(mpin) != 4 or not mpin.isdigit():
                    st.error("⚠️ MPIN must be 4 digits")
                else:
                    with st.spinner("Processing payment securely..."):
                        try:
                            res = requests.post(f"{BASE_URL}/send-money", json={
                                "sender_id": user.get("user_id"),
                                "receiver_id": receiver["user_id"],
                                "amount": amount, "mpin": mpin
                            }, timeout=5)
                            if res.status_code == 200:
                                result = res.json()
                                st.session_state.payment_result = result
                                st.session_state.user["balance"] = result.get("new_balance", user.get("balance", 0))
                                nav("result")
                            elif res.status_code == 401:
                                st.error("❌ Incorrect MPIN. Please try again.")
                            else:
                                st.error(res.json().get("error", "Payment failed"))
                        except Exception as e:
                            st.error(f"❌ Server error: {e}")

    # ---- RIGHT ----
    with right:
        if status == "SAFE":
            box, score_class, icon = "risk-safe", "risk-score-safe", "✅"
            msg = "This transaction appears safe to proceed."
            recs = ["Amount is within your normal spending range",
                    "Account has good standing history",
                    "No suspicious network connections found"]
            rec_color = "#15803D"
        elif status == "WARNING":
            box, score_class, icon = "risk-warning", "risk-score-warning", "⚠️"
            msg = "Moderate risk detected. Proceed with caution."
            recs = ["Amount is higher than your usual transactions",
                    "Consider splitting into smaller amounts",
                    "Verify receiver identity before proceeding"]
            rec_color = "#B45309"
        else:
            box, score_class, icon = "risk-blocked", "risk-score-blocked", "🚫"
            msg = "High fraud risk. Transaction is blocked."
            recs = ["Transaction far exceeds safe risk threshold",
                    "Suspicious fraud network connections found",
                    "Contact support if this is a legitimate payment"]
            rec_color = "#BE123C"

        st.markdown(f"""
        <div class="{box}">
            <div style="font-size:11px; font-weight:600; color:#64748B; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;">
                VaultPay Fraud Risk Analysis
            </div>
            <div class="{score_class}">{icon} {status} — Score: {risk} / 140</div>
            <p style="font-size:12px; margin:8px 0 0 0; color:#475569;">{msg}</p>
        </div>
        """, unsafe_allow_html=True)

        if breakdown:
            st.markdown('<div class="sec-title" style="font-size:15px; margin-top:4px;">DAA Algorithm Breakdown</div>', unsafe_allow_html=True)
            st.caption("Risk score contributed by each algorithm")
            bd_df = pd.DataFrame({"Algorithm": list(breakdown.keys()), "Risk Score": list(breakdown.values())})
            st.bar_chart(bd_df.set_index("Algorithm"), use_container_width=True, height=180)

        st.markdown('<div class="sec-title" style="font-size:15px;">Risk Level Meter</div>', unsafe_allow_html=True)
        st.caption("Where your transaction falls on the risk scale")
        meter_df = pd.DataFrame({
            "Zone": ["Safe (0-50)", "Warning (51-100)", "Blocked (100+)"],
            "Score": [min(risk, 50), max(0, min(risk-50, 50)), max(0, risk-100)]
        })
        st.bar_chart(meter_df.set_index("Zone"), use_container_width=True, height=140)

        rec_html = "".join([f'<div class="rec-item">• {r}</div>' for r in recs])
        st.markdown(f"""
        <div class="rec-box">
            <div class="rec-title" style="color:{rec_color};">{icon} Smart Recommendations</div>
            {rec_html}
        </div>
        """, unsafe_allow_html=True)

# ================================================================
#  RESULT
# ================================================================
def show_result():
    result   = st.session_state.get("payment_result", {})
    receiver = st.session_state.selected_receiver or {}
    amount   = st.session_state.entered_amount or 0
    status   = result.get("status", "UNKNOWN")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if status in ("SUCCESS", "WARNING"):
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:48px 32px;">
                <div style="width:80px; height:80px; background:#DCFCE7; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:36px; margin:0 auto 20px auto;">✅</div>
                <h2 style="color:#15803D; font-weight:800; margin:0; font-size:26px;">Payment Successful</h2>
                <p style="color:#64748B; margin:10px 0; font-size:14px;">Money sent to <strong>{receiver.get('name','')}</strong></p>
                <h1 style="font-size:40px; font-weight:800; color:#2563EB; margin:16px 0;">₹ {amount:,.2f}</h1>
                <div style="background:#F1F5F9; border-radius:12px; padding:14px; margin-top:16px;">
                    <p style="margin:0; font-size:12px; color:#64748B;">Risk Score: <strong>{result.get('risk',0)}</strong> &nbsp;|&nbsp; Status: <strong>{status}</strong> &nbsp;|&nbsp; Protected by VaultPay</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:48px 32px;">
                <div style="width:80px; height:80px; background:#FFE4E6; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:36px; margin:0 auto 20px auto;">🚫</div>
                <h2 style="color:#DC2626; font-weight:800; margin:0; font-size:26px;">Payment Blocked</h2>
                <p style="color:#64748B; margin:10px 0; font-size:14px;">Blocked by VaultPay Fraud Detection Engine</p>
                <h1 style="font-size:40px; font-weight:800; color:#DC2626; margin:16px 0;">₹ {amount:,.2f}</h1>
                <div style="background:#FFF1F2; border-radius:12px; padding:14px; margin-top:16px;">
                    <p style="margin:0; font-size:12px; color:#BE123C;">Risk Score: <strong>{result.get('risk',0)}</strong> &nbsp;|&nbsp; Fraud Detected &nbsp;|&nbsp; Your money is safe</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Go to Dashboard", type="primary", use_container_width=True):
            st.session_state.selected_receiver = None
            st.session_state.entered_amount    = 0
            st.session_state.risk_result       = None
            st.session_state.payment_result    = None
            nav("dashboard")

# ================================================================
#  BALANCE
# ================================================================
def show_balance():
    nav_bar("Check Balance")
    if st.button("← Back to Dashboard", key="back_bal"): nav("dashboard")

    user    = st.session_state.user or {}
    balance = user.get("balance", 0)
    wallet  = user.get("wallet_balance", 0)
    acc_num = str(user.get("account_number", "0000000000"))

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="card-blue" style="text-align:center; padding:36px;">
            <p class="balance-label">🏦 Bank Account Balance</p>
            <p class="balance-amount">₹ {balance:,.2f}</p>
            <p class="balance-sub">Account No: XXXX XXXX {acc_num[-4:]}</p>
        </div>
        <div class="card-teal" style="text-align:center; padding:28px;">
            <p class="balance-label">👛 VaultPay Wallet Balance</p>
            <p class="balance-amount">₹ {wallet:,.2f}</p>
            <p class="balance-sub">Instant payments, zero charges</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➕ Add Money to Account", type="primary", use_container_width=True):
            nav("add_balance")

# ================================================================
#  HISTORY
# ================================================================
def show_history():
    nav_bar("Transaction History")
    if st.button("← Back to Dashboard", key="back_hist"): nav("dashboard")

    st.markdown('<div class="sec-title">Recent Transactions</div>', unsafe_allow_html=True)
    try:
        txns = requests.get(f"{BASE_URL}/transactions", timeout=5).json()
    except:
        st.error("❌ Cannot connect to server"); return

    if not txns:
        st.info("No transactions yet. Make your first payment!"); return

    for t in txns:
        sender_name   = get_user_name(t["sender"])
        receiver_name = get_user_name(t["receiver"])
        status        = t.get("status", "")

        if status == "SUCCESS":
            pill = '<span class="pill-success">SUCCESS</span>'; amt_color = "#15803D"
        elif status == "WARNING":
            pill = '<span class="pill-warning">WARNING</span>'; amt_color = "#B45309"
        else:
            pill = '<span class="pill-blocked">BLOCKED</span>'; amt_color = "#DC2626"

        st.markdown(f"""
        <div class="txn-row">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:42px; height:42px; background:#EFF6FF; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:18px;">
                    {'✅' if status=='SUCCESS' else '⚠️' if status=='WARNING' else '🚫'}
                </div>
                <div>
                    <div class="txn-name">{sender_name} → {receiver_name}</div>
                    <div class="txn-time">{t['time']} &nbsp;|&nbsp; Risk Score: {t['risk']}</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div class="txn-amount" style="color:{amt_color};">₹ {t['amount']:,.2f}</div>
                <div style="margin-top:4px;">{pill}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================
#  ROUTER
# ================================================================
page = st.session_state.page
if not st.session_state.logged_in:
    show_auth()
else:
    if   page == "dashboard":    show_dashboard()
    elif page == "contacts":     show_contacts()
    elif page == "enter_amount": show_enter_amount()
    elif page == "payment":      show_payment()
    elif page == "result":       show_result()
    elif page == "balance":      show_balance()
    elif page == "history":      show_history()
    elif page == "add_balance":  show_add_balance()
    elif page == "scan":         show_scan()
    elif page == "profile":      show_profile()
    else:                        show_dashboard()