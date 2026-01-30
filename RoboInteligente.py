import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import base64
from gtts import gTTS
from groq import Groq

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Tutor Trigonométrico", layout="wide")

# Inicialização Groq
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inicialização de Estados
if 'pagina' not in st.session_state: st.session_state.pagina = 'intro'
if 'angulo' not in st.session_state: st.session_state.angulo = 0
if 'movendo' not in st.session_state: st.session_state.movendo = False
if 'pontos' not in st.session_state: st.session_state.pontos = 0
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""

ANGULOS_NOTAVEIS = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]

# --- FUNÇÃO DE VOZ ---
def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt')
        tts.save("saudacao.mp3")
        with open("saudacao.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- MOTOR GRÁFICO (ECRÃ 2) ---
def desenhar_trigo(angulo):
    rad = np.radians(angulo)
    px, py = np.cos(rad), np.sin(rad)
    
    fig = go.Figure()

    # Círculo (Negrito)
    t = np.linspace(0, 2*np.pi, 200)
    fig.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode='lines', line=dict(color='black', width=4)))

    # Eixos (Horizontal: Vermelho/Cosseno, Vertical: Azul Escuro/Seno)
    fig.add_shape(type="line", x0=-1.3, y0=0, x1=1.3, y1=0, line=dict(color="red", width=3))
    fig.add_shape(type="line", x0=0, y0=-1.3, x1=0, y1=1.3, line=dict(color="darkblue", width=3))

    # Ângulos Notáveis e Rótulos (Sentido Anti-horário)
    for a in ANGULOS_NOTAVEIS:
        ra = np.radians(a)
        fig.add_trace(go.Scatter(x=[np.cos(ra)], y=[np.sin(ra)], mode='markers+text', 
                                 text=[f"<b>{a}º</b>"], textposition="top right",
                                 marker=dict(color='black', size=6)))

    # Segmento 3: OP (Lado móvel - Verde)
    fig.add_trace(go.Scatter(x=[0, px], y=[0, py], mode='lines', line=dict(color='green', width=4), name="OP"))
    
    # Segmento 1: Paralelo ao eixo vertical (Indica Cosseno - Preto)
    fig.add_trace(go.Scatter(x=[px, px], y=[0, py], mode='lines', line=dict(color='black', dash='dash'), name="Seg1"))
    
    # Segmento 2: Paralelo ao eixo horizontal (Indica Seno - Verde Escuro)
    fig.add_trace(go.Scatter(x=[0, px], y=[py, py], mode='lines', line=dict(color='darkgreen', dash='dash'), name="Seg2"))

    # Boneca Robô Vermelha no Ponto P
    fig.add_trace(go.Scatter(x=[px], y=[py], mode='markers', marker=dict(color='red', size=18, symbol='star-diamond')))

    # Valores nos eixos (Negrito)
    ticks = [-1, -0.866, -0.707, -0.5, 0, 0.5, 0.707, 0.866, 1]
    fig.update_layout(
        xaxis=dict(tickvals=ticks, range=[-1.4, 1.4], title="<b>COSSENO (Eixo Vermelho)</b>"),
        yaxis=dict(tickvals=ticks, range=[-1.4, 1.4], title="<b>SENO (Eixo Azul Escuro)</b>"),
        showlegend=False, width=650, height=650, margin=dict(l=20, r=20, t=20, b=20)
    )
    
    # Indicações de Quadrantes
    fig.add_annotation(x=0.7, y=0.7, text="<b>IQ</b>", showarrow=False)
    fig.add_annotation(x=-0.7, y=0.7, text="<b>IIQ</b>", showarrow=False)
    fig.add_annotation(x=-0.7, y=-0.7, text="<b>IIIQ</b>", showarrow=False)
    fig.add_annotation(x=0.7, y=-0.7, text="<b>IVQ</b>", showarrow=False)

    return fig

# --- ESTILIZAÇÃO CSS (Fundo Robô e Barra Lateral) ---
st.markdown("""
<style>
    .stApp { background-color: #f0f0f0; }
    /* Estilo do Robô para o Ecrã 2 */
    .fundo-robo {
        background-color: #D3D3D3; border-radius: 20px; padding: 20px;
        border-top: 50px solid orange; border-bottom: 80px solid #cc5500; /* Braços e pernas */
    }
    /* Barra lateral grossa */
    [data-testid="stSidebar"] { min-width: 250px !important; background-color: #333; color: white; border-right: 30px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---

# ECRÃ 1: INTRODUÇÃO
if st.session_state.pagina == 'intro':
    st.title("Tutor Trigonométrico")
    col_img, col_form = st.columns([0.7, 0.3])
    with col_img:
        # Imagem do robô ocupando 70%
        st.image("https://img.freepik.com/free-vector/cute-robot-waving-hand-cartoon-character_138676-2744.jpg", use_container_width=True)
    
    with col_form:
        nome = st.text_input("Escreva o seu nome:")
        if st.button("Entrar"):
            st.session_state.user_nome = nome
            falar(f"É um prazer conhecer-te {nome}, e discutir contigo assuntos da trigonometria")
            time.sleep(2)
            st.session_state.pagina = 'trigo'
            st.rerun()

# ECRÃ 2: O CÍRCULO
elif st.session_state.pagina == 'trigo':
    st.sidebar.header("CONTROLES")
    
    # Barra lateral com sensor (ilustrado por CSS) e botões
    if st.sidebar.button("Página Inicial"):
        st.session_state.pagina = 'intro'
        st.rerun()
    
    if st.sidebar.button("VAMOS JOGAR"):
        st.session_state.pagina = 'jogo'
        st.rerun()

    st.markdown('<div class="fundo-robo">', unsafe_allow_html=True)
    
    col_plot, col_btn = st.columns([0.7, 0.3])
    
    with col_btn:
        st.write(f"### Olá, {st.session_state.user_nome}")
        if st.button("Iniciar +"): st.session_state.movendo = True
        if st.button("Parar/Avançar"): st.session_state.movendo = not st.session_state.movendo
        if st.button("Reiniciar"):
            st.session_state.angulo = 0
            st.session_state.movendo = False
            st.rerun()
        
        st.metric("Ângulo (α)", f"{int(st.session_state.angulo)}º")
        st.write(f"**Seno:** {np.sin(np.radians(st.session_state.angulo)):.3f}")
        st.write(f"**Cosseno:** {np.cos(np.radians(st.session_state.angulo)):.3f}")

    with col_plot:
        placeholder = st.empty()
        # Loop de movimento controlado para evitar o erro removeChild
        if st.session_state.movendo:
            while st.session_state.movendo:
                st.session_state.angulo = (st.session_state.angulo + 1) % 361
                placeholder.plotly_chart(desenhar_trigo(st.session_state.angulo), use_container_width=True)
                
                if st.session_state.angulo in ANGULOS_NOTAVEIS:
                    time.sleep(2)
                else:
                    time.sleep(0.02)
                
                if not st.session_state.movendo: break
        else:
            placeholder.plotly_chart(desenhar_trigo(st.session_state.angulo), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ECRÃ 3: GAMIFICAÇÃO
elif st.session_state.pagina == 'jogo':
    st.title("🎮 Desafio de Razoes Trigonométricas")
    st.sidebar.write(f"### Pontuação: {st.session_state.pontos}")
    
    # Lógica de Gamificação (Exemplo de uma das 20 questões)
    st.info("Pergunta: Se o cosseno de um ângulo no IQ é 1/2, qual o seu valor em graus?")
    opcoes = ["30º", "45º", "60º", "90º"]
    resp = st.radio("Escolha a opção:", opcoes)
    
    if st.button("Confirmar Resposta"):
        if resp == "60º":
            st.session_state.pontos += 10
            st.success("Correto! Muito bem!")
        else:
            st.error("Incorreto! Acompanha a resolução:")
            st.write("Explicação: No círculo unitário, o cosseno é a abcissa. Para x=0.5, o ângulo é 60º.")
    
    col_nav = st.columns(3)
    if col_nav[0].button("Reiniciar Jogo"): 
        st.session_state.pontos = 0
        st.rerun()
    if col_nav[1].button("Voltar ao Círculo"): 
        st.session_state.pagina = 'trigo'
        st.rerun()
    if col_nav[2].button("Página Inicial"): 
        st.session_state.pagina = 'intro'
        st.rerun()
