import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lakay Pale Pro", page_icon="🇭🇹", layout="wide")

# --- STYLING (Black & Neon) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; color: white !important; }
    h1 { text-align: center; color: #fff; text-shadow: 0 0 10px #00d2ff, 0 0 20px #ff003c; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #00d2ff, #0078ff); color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("LAKAY PALE")
st.markdown("<h3 style='text-align: center; color: #888;'>Entèlijans ki Pale Lang Ou</h3>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR (API KEY) ---
with st.sidebar:
    st.header("⚙️ SISTÈM")
    api_key = st.text_input("Kle API OpenAI", type="password")
    if not api_key:
        st.warning("⚠️ Mete Kle API ou la pou kòmanse.")
        st.stop()

client = OpenAI(api_key=api_key)

# --- MAIN LAYOUT ---
col1, col2 = st.columns(2)

# --- COLUMN 1: VOICE (PALE) ---
with col1:
    st.info("🎙️ 1. PALE / KREYE")
    st.write("Peze bouton an epi pale an Kreyòl:")
    
    # Microphone input
    audio_data = mic_recorder(start_prompt="🔴 KÒMANSE PALE", stop_prompt="⬛ BOUT", key="recorder")
    
    if audio_data:
        st.audio(audio_data['bytes'])
        st.success("Odyo resevwa! M ap reflechi...")
        
        # Transcribe audio (Whisper)
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "audio.wav"
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        user_text = transcript.text
        st.write(f"🗣️ **Ou di:** {user_text}")
        
        # Get AI Response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ou se yon asistan ayisyen entèlijan. Reponn an Kreyòl klè."},
                {"role": "user", "content": user_text}
            ]
        )
        ai_reply = response.choices[0].message.content
        st.markdown(f"🤖 **Lakay Pale:** {ai_reply}")

# --- COLUMN 2: CAMERA & SCANNER (ESKANÈ) ---
with col2:
    st.error("📸 2. ESKANÈ / KAMERA")
    
    # TAB SELECTION: Choose between Camera or Upload
    tab1, tab2 = st.tabs(["📸 Pran Foto", "📂 Chwazi Fichye"])
    
    image_data = None

    with tab1:
        # THE MISSING CAMERA WIDGET
        camera_pic = st.camera_input("Pran yon foto dokiman an")
        if camera_pic:
            image_data = camera_pic

    with tab2:
        uploaded_file = st.file_uploader("Depoze foto a la", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            image_data = uploaded_file

    # Process the image if one exists
    if image_data:
        st.image(image_data, caption="Dokiman ou voye a")
        if st.button("🔍 ANALIZE DOKIMAN AN"):
            with st.spinner("M ap li dokiman an..."):
                # Convert image for OpenAI
                import base64
                bytes_data = image_data.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Esplike m sa ki ekri nan dokiman sa a an Kreyòl."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ],
                        }
                    ],
                    max_tokens=500
                )
                st.markdown(response.choices[0].message.content)
