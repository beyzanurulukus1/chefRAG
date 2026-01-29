import streamlit as st
import json
import os
from engine import ChefRAGEngine
from langchain_core.messages import HumanMessage, AIMessage
def local_css():
    st.markdown("""
    <style>
        /* Ana Arkaplan ve Yazı Tipi */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Navbar Tasarımı */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(#2e3440, #1a1c23);
            border-right: 1px solid #4c566a;
        }
        
        /* Mesaj Baloncukları Tasarımı */
        .stChatMessage {
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        /* Butonları Güzelleştirme */
        .stButton>button {
            border-radius: 20px;
            border: 1px solid #61dafb;
            background-color: transparent;
            color: #61dafb;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #61dafb;
            color: #282c34;
            transform: scale(1.02);
        }

        /* Başlık Stilini Özelleştirme */
        h1 {
            color: #61dafb;
            font-family: 'Courier New', Courier, monospace;
            text-shadow: 2px 2px #000000;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 1. YARDIMCI FONKSİYONLAR: VERİ KALICILIĞI ---
DB_FILE = "chat_sessions.json"

def save_sessions(sessions):
    """Sohbet nesnelerini JSON formatına çevirip kaydeder."""
    serializable_sessions = {}
    for title, messages in sessions.items():
        # LangChain nesnelerini JSON'un anlayacağı sözlüklere çeviriyoruz
        serializable_sessions[title] = [
            {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
            for m in messages
        ]
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_sessions, f, ensure_ascii=False, indent=4)

def load_sessions():
    """JSON dosyasını okuyup LangChain nesnelerine geri çevirir."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    loaded_sessions = {}
    for title, messages in data.items():
        # Sözlükleri tekrar HumanMessage/AIMessage nesnelerine çeviriyoruz
        loaded_sessions[title] = [
            HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
            for m in messages
        ]
    return loaded_sessions

# --- 2. UI VE OTURUM YÖNETİMİ ---
st.set_page_config(page_title="ChefRAG", page_icon="🍳", layout="wide")

# Veriyi diskten yükle
if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions()

if "active_session" not in st.session_state:
    st.session_state.active_session = None

# Navbar
with st.sidebar:
    st.title("🥨 Mutfak Arşivi")
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.active_session = None
        st.rerun()
    
    st.divider()
    st.subheader("Eski Sohbetleriniz")
    # Geçmişi yanda listeleme isteğin doğrultusunda
    for title in reversed(list(st.session_state.sessions.keys())):
        if st.sidebar.button(f"💬 {title}", use_container_width=True, key=title):
            st.session_state.active_session = title
            st.rerun()
    
    st.divider()
    k_val = st.slider("İncelenecek Tarif Sayısı", 1, 5, 3)

# ANA EKRAN
st.title("👩🏻‍🍳 ChefRAG: Akıllı Mutfak Asistanı")
st.markdown("##### *Bugün ne pişirsem diye düşünme, malzemeni söyle ben şefin olarak hazırlayayım!*")

if st.session_state.active_session is None:
    st.info("Bugün size nasıl yardımcı olabilirim? Yeni bir sohbet başlatın veya sol menüden eski sohbetlerinizi seçin.")       
    current_chat_history = []
else:
    current_chat_history = st.session_state.sessions[st.session_state.active_session]

# Mesajları Göster
for message in current_chat_history:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# Kullanıcı Girdisi
user_input = st.chat_input("Şefim, dünkü tarifle ilgili bir sorum var...")

if user_input:
    # Oturum oluşturma ve başlıklandırma
    if st.session_state.active_session is None:
        new_title = user_input[:25] + ("..." if len(user_input) > 25 else "")
        if new_title in st.session_state.sessions:
            new_title = f"{new_title} ({len(st.session_state.sessions)})"
        st.session_state.sessions[new_title] = []
        st.session_state.active_session = new_title
        current_chat_history = st.session_state.sessions[new_title]

    with st.chat_message("user"):
        st.markdown(user_input)
    
    engine = ChefRAGEngine(k_val=k_val)
    chef_chain = engine.get_chain()
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        for chunk in chef_chain.stream({"question": user_input, "chat_history": current_chat_history}):
            full_response += chunk
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    
    # 3. VERİYİ KAYDET: Her mesajdan sonra JSON'u güncelle
    st.session_state.sessions[st.session_state.active_session].append(HumanMessage(content=user_input))
    st.session_state.sessions[st.session_state.active_session].append(AIMessage(content=full_response))
    save_sessions(st.session_state.sessions)
    st.rerun()
