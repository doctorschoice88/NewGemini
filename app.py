import streamlit as st
from google import genai
from google.genai import types
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import datetime

# --- PASSWORD KA TAALA ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Agar login nahi hai, toh password maango
if not st.session_state.authenticated:
    st.title("🔒 SUPERB PRO AI (Secured)")
    password = st.text_input("Enter Password:", type="password")
    
    if st.button("Login"):
        if "APP_PASSWORD" in st.secrets and password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Galat Password! Hatt!")
    st.stop()  # Yahin rok dega agar password nahi mila

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Superb Pro AI (Gemini 2.5 Flash)",
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
    st.caption("Model: gemini-2.5-flash (Latest)")

    # API KEY
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("ACCESS GRANTED")
    else:
        api_key = st.text_input("ENTER API KEY", type="password")

    st.divider()
    
    # Mood Slider
    mood = st.select_slider(
        "CURRENT MENTAL STATE",
        options=["PANIC", "ANXIOUS", "STABLE", "CONFIDENT", "EUPHORIC/GREEDY"]
    )
    
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
        
        if hist.empty:
            return None, None, None, "NO DATA"

        # Price Action
        price = hist['Close'].iloc[-1]
        change = price - hist['Close'].iloc[-2]
        
        vix_val = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 0
        
        # Indicators
        hist['RSI'] = ta.rsi(hist['Close'], length=14)
        hist['EMA_20'] = ta.ema(hist['Close'], length=20)
        
        rsi = hist['RSI'].iloc[-1]
        trend = "BULLISH" if price > hist['EMA_20'].iloc[-1] else "BEARISH"
        
        # Pivots (previous candle)
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
    except Exception as e:
        return None, None, None, f"Error fetching data: {e}"

# --- UI LAYER ---
st.title("⚡ SUPERB PRO AI – Gemini 2.5 Flash")

price, vix, rsi, context = get_data()

if price:
    c1, c2, c3 = st.columns(3)
    c1.metric("NIFTY 50", f"{price:.0f}", f"{price * 0.005:.2f}")
    c2.metric("VIX (FEAR)", f"{vix:.2f}")
    c3.metric("RSI", f"{rsi:.2f}")

    if mood == "PANIC":
        st.error("⚠️ HIGH ALERT: EMOTIONS UNSTABLE. DO NOT TRADE.")
else:
    st.warning("Live market data load nahi ho paya. AI phir bhi chat ke liye ready hai.")

# --- AI BRAIN (Gemini 2.5 Flash) ---
if api_key:
    client = genai.Client(api_key=api_key)

    sys_prompt = (
        "You are 'Superb Pro', an elite Trading Psychologist & Analyst. "
        "You speak in Hinglish (Brotherly tone). "
        f"Analyze this Live Data:\n{context}\n"
        "Rules:\n"
        "1. If VIX is high (>15) OR User Mood is PANIC, your ONLY goal is to calm them down. No trade setups.\n"
        "2. If Mood is STABLE/CONFIDENT and VIX < 15, give Nifty intraday levels using Pivots/RSI.\n"
        "3. Be direct. Use short sentences. No generic gyaan. Focused, brother-to-brother tone.\n"
    )

    # Chat history init
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "System upgraded to Gemini 2.5 Flash. Data online. Bol bhai, kya scene hai?"
            }
        ]

    # Show old messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Command..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Conversation ko plain text me convert karo
            conv_text = ""
            for m in st.session_state.messages:
                role = "User" if m["role"] == "user" else "Assistant"
                conv_text += f"{role}: {m['content']}\n"

            # Gemini 2.5 Flash call
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=conv_text,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    system_instruction=sys_prompt
                ),
            )

            full_res = response.text

            with st.chat_message("assistant"):
                st.markdown(full_res)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_res}
            )

        except Exception as e:
            import traceback
            st.error(f"Error: {type(e).__name__}: {e}")
            st.code(traceback.format_exc())
else:
    st.info("Sidebar me Gemini API key daal pehle, phir hi AI BRAIN active hoga.")
