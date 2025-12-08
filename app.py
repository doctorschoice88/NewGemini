# --- PASSWORD KA TAALA ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Agar login nahi hai, toh password maango
if not st.session_state.authenticated:
    st.title("🔒 SUPERB PRO AI (Secured)")
    password = st.text_input("Enter Password:", type="password")
    
    if st.button("Login"):
        if password == st.secrets["APP_PASSWORD"]:  # Secret se match karega
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Galat Password! Hatt!")
    st.stop()  # Yahin rok dega agar password nahi mila

import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Superb Pro AI (gemini-1.5-flash)",
    page_icon="🧠",
    layout="wide"
)

# --- CUSTOM CSS (Ultra Dark Theme) ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    .metric-container {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    h1, h2, h3 { color: #00ff41 !important; }
    .stTextInput input { background-color: #111; color: #00ff41; border: 1px solid #333; }
    .stChatMessage { background-color: #111; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎛️ SYSTEM CONTROL")
    st.caption("Model: gemini-1.5-flash (Latest)")
    
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("ACCESS GRANTED")
    else:
        api_key = st.text_input("ENTER API KEY", type="password")

    st.divider()
    
    # Mood Slider
    mood = st.select_slider("CURRENT MENTAL STATE", options=["PANIC", "ANXIOUS", "STABLE", "CONFIDENT", "EUPHORIC/GREEDY"])
    
    if st.button("🔴 RESET SYSTEM"):
        st.session_state.messages = []
        st.rerun()

# --- MARKET INTELLIGENCE ENGINE ---
def get_data():
    try:
        # Nifty & VIX
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="1mo")
        
        vix = yf.Ticker("^INDIAVIX")
        vix_hist = vix.history(period="5d")
        
        if hist.empty: return None, "NO DATA"

        # Price Action
        price = hist['Close'].iloc[-1]
        change = price - hist['Close'].iloc[-2]
        
        vix_val = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 0
        
        # Indicators
        hist['RSI'] = ta.rsi(hist['Close'], length=14)
        hist['EMA_20'] = ta.ema(hist['Close'], length=20)
        
        rsi = hist['RSI'].iloc[-1]
        trend = "BULLISH" if price > hist['EMA_20'].iloc[-1] else "BEARISH"
        
        # Pivots
        h, l, c = hist['High'].iloc[-2], hist['Low'].iloc[-2], hist['Close'].iloc[-2]
        p = (h + l + c) / 3
        r1 = (2 * p) - l
        s1 = (2 * p) - h
        
        context = (
            f"REAL-TIME DATA:\n"
            f"NIFTY: {price:.2f} (Change: {change:.2f})\n"
            f"INDIA VIX: {vix_val:.2f} (Fear Index)\n"
            f"RSI: {rsi:.2f}\n"
            f"TREND: {trend}\n"
            f"SUPPORTS: S1 {s1:.0f} | RESISTANCE: R1 {r1:.0f}\n"
            f"USER MOOD: {mood}\n"
        )
        return price, vix_val, rsi, context
    except:
        return None, None, None, "Error fetching data"

# --- UI LAYER ---
st.title("⚡ SUPERB PRO AI gemini-1.5-flash ")
price, vix, rsi, context = get_data()

if price:
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50", f"{price:.0f}", f"{price * 0.005:.2f}")
    c2.metric("VIX (FEAR)", f"{vix:.2f}")
    c3.metric("RSI", f"{rsi:.2f}")

    if mood == "PANIC":
        st.error("⚠️ HIGH ALERT: EMOTIONS UNSTABLE. DO NOT TRADE.")

# --- AI BRAIN (gemini-1.5-flash) ---
if api_key:
    genai.configure(api_key=api_key)
    
    sys_prompt = (
        "You are 'Superb Pro', an elite Trading Psychologist & Analyst using Gemini-pro. "
        "You speak in Hinglish (Brotherly tone). "
        f"Analyze this Live Data:\n{context}\n"
        "1. If VIX is high (>15) or User Mood is PANIC, your ONLY goal is to calm them down. No trade setups.\n"
        "2. If Stable, give Nifty levels based on Pivots/RSI.\n"
        "3. Be direct. Use short sentences. No generic advice."
    )
    
    # USING THE LATEST gemini-1.5-flash MODEL
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config={"temperature": 0.3},
        system_instruction=sys_prompt
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "model", "content": "System upgraded to Gemini Pro. Data online. Bol Bhai, kya scene hai?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]])
                response = chat.send_message(prompt, stream=True)
                full_res = ""
                holder = st.empty()
                for chunk in response:
                    if chunk.text:
                        full_res += chunk.text
                        holder.markdown(full_res + "▌")
                holder.markdown(full_res)
                st.session_state.messages.append({"role": "model", "content": full_res})
            except Exception as e:
                st.error(f"Error: {str(e)}")
