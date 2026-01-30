import streamlit as st
from groq import Groq
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="TutorIntEqQuadratica",
    layout="centered",
    page_icon="🧮"
)

# --- DESIGN CUSTOMIZADO (CSS) PARA APK ---
st.markdown("""
    <style>
    /* Estilo para botões mobile-friendly */
    div.stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        padding: 0.75rem;
        border: none;
    }
    /* Estilo para as mensagens do chat */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 5px;
    }
    /* Esconder o menu padrão do Streamlit para parecer App nativo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO SEGURA ---
def get_groq_client():
    try:
        # Puxa a chave gsk_... configurada no secrets.toml ou no Cloud
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("ERRO: Configuração de chave ausente.")
        st.stop()

client = get_groq_client()

# --- BLINDAGEM DE FOCO (SYSTEM PROMPT) ---
SYSTEM_PROMPT = """
VOCÊ É O "TutorIntEqQuadratica".
SEU ÚNICO OBJETIVO É ENSINAR EQUAÇÕES DO 2º GRAU.

INSTRUÇÕES DE SEGURANÇA E FOCO:
1. FOCO TOTAL: Se o aluno perguntar sobre qualquer tema que NÃO seja equações quadráticas ou matemática básica relacionada, responda educadamente: "Como TutorIntEqQuadratica, meu foco é ajudar você a dominar equações do 2º grau. Vamos voltar ao tema?"
2. MÉTODO SCAFFOLDING: Nunca dê o valor de 'x' direto. Pergunte pelos coeficientes (a, b, c), peça para calcular o Delta ($\Delta$), etc.
3. VISÃO: Se receber imagem, identifique os termos da equação quadrática nela.
4. FORMATAÇÃO: Use LaTeX para clareza matemática.
"""

# --- INICIALIZAÇÃO DO ESTADO ---
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "camera_ativa" not in st.session_state:
    st.session_state.camera_ativa = False

# --- UI DO APLICATIVO ---
st.title("🧮 TutorIntEqQuadratica")
st.caption("Especialista em Equações de 2º Grau")

# Exibição do Histórico
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ÁREA DE INPUT ---
st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📷 Abrir Câmera"):
        st.session_state.camera_ativa = not st.session_state.camera_ativa

foto_aluno = None
if st.session_state.camera_ativa:
    foto_aluno = st.camera_input("Capture o exercício")

prompt_texto = st.chat_input("Ex: Como calculo o delta desta equação?")

# --- PROCESSAMENTO IA ---
if prompt_texto or (foto_aluno and st.session_state.camera_ativa):
    payload = []
    
    if prompt_texto:
        st.session_state.mensagens.append({"role": "user", "content": prompt_texto})
        payload.append({"type": "text", "text": prompt_texto})

    if foto_aluno:
        img_base64 = base64.b64encode(foto_aluno.getvalue()).decode('utf-8')
        payload.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
        })
        if not prompt_texto:
            st.session_state.mensagens.append({"role": "user", "content": "📸 [Imagem enviada para análise]"})

    # Chamada à Groq com Temperatura Baixa (Foco Máximo)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Analisando foco..."):
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": payload}
                    ],
                    temperature=0.1, # Temperatura mínima para evitar que a IA "viaje"
                    max_tokens=600
                )
                
                texto_resposta = response.choices[0].message.content
                st.markdown(texto_resposta)
                st.session_state.mensagens.append({"role": "assistant", "content": texto_resposta})
                st.session_state.camera_ativa = False # Fecha câmera após processar
                
        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")

# Sidebar para funções administrativas
with st.sidebar:
    st.title("Configurações")
    if st.button("🗑️ Reiniciar Tutor"):
        st.session_state.mensagens = []
        st.rerun()
