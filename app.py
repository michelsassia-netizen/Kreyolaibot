import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io
import base64

# --- CONFIG ---
st.set_page_config(page_title="Lakay Pale Pro", page_icon="🇭🇹", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    
    /* Tit Gwo ak Neon */
    .neon-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#00d2ff, #ff003c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    /* Bwat Sponsor Gold (San Imaj) */
    .sponsor-box {
        border: 2px solid #FFD700;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        background: #1a1a00;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        margin-top: 20px;
    }
    
    /* Bouton yo */
    .stButton>button { border-radius: 20px; background: #111; color: white; border: 1px solid #444; width: 100%; }
    .stButton>button:hover { border-color: #00d2ff; color: #00d2ff; }
    
    /* Expander Kamera */
    .stExpander { background-color: #111; border: 1px solid #333; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🤖 KreyolAIHub")
    st.markdown("---")
    api_key = st.text_input("Kle API OpenAI", type="password")
    if not api_key:
        st.warning("Mete Kle API a.")
        st.stop()
client = OpenAI(api_key=api_key)

# --- HEADER (TIT LA SÈLMAN) ---
st.markdown('<h1 class="neon-title">LAKAY PALE</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Entèlijans Atifisyèl Ayisyen 🇭🇹</p>", unsafe_allow_html=True)
st.divider()

# --- FONKSYON POU FÈ LOGO ---
def generate_image(prompt):
    with st.spinner("🎨 M ap desinen logo a... Tann 10 segonn."):
        try:
            response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
            return response.data[0].url
        except Exception as e:
            return f"Erè: {str(e)}"

# --- LAYOUT (3 KOLÒN) ---
col1, col2, col3 = st.columns([1, 2, 2])

# 1. SPONSOR (Bwat Gold)
with col1:
    st.markdown("""
        <div class="sponsor-box">
            <h2 style='color: #FFD700; margin:0;'>PRESTIGE</h2>
            <p style='font-size: 3rem; margin:0;'>🍺</p>
            <p style='color: #FFD700; font-size: 0.8rem;'>SPONSOR OFISYÈL</p>
        </div>
    """, unsafe_allow_html=True)

# 2. PALE / KREYE
with col2:
    st.info("🎙️ **PALE / KREYE**")
    st.write("Di: *'Fè yon logo pou yon magazen soulye...'*")
    
    audio_data = mic_recorder(start_prompt="🔴 PALE", stop_prompt="⬛ STOP", key="recorder")
    
    if audio_data:
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "audio.wav"
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        text = transcript.text
        st.write(f"🗣️ **Ou di:** {text}")

        # DETEKSYON LOGO
        if any(w in text.lower() for w in ["logo", "imaj", "desen", "foto", "fè"]):
            st.success("🎨 M ap travay sou desen an...")
            img_url = generate_image(text)
            if "http" in img_url: st.image(img_url)
            else: st.error(img_url)
        else:
            resp = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":text}])
            st.write(f"🤖 {resp.choices[0].message.content}")

# 3. ESKANÈ (KACHE)
with col3:
    st.error("📸 **ESKANÈ**")
    
    with st.expander("📸 Klike la pou wouvri Kamera a"):
        cam = st.camera_input("Foto")
    
    up = st.file_uploader("Oswa upload yon foto", type=['jpg','png'])
    final = cam if cam else up

    if final:
        st.image(final, width=150)
        if st.button("🔍 ANALIZE"):
            with st.spinner("M ap gade..."):
                b64 = base64.b64encode(final.getvalue()).decode()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":[{"type":"text", "text":"Esplike sa."},{"type":"image_url", "image_url":{"url":f"data:image/jpeg;base64,{b64}"}}] }])
                st.write(res.choices[0].message.content)
